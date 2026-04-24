#!/usr/bin/env python3
"""
redsky_rotate.py

Scrapes Target RedSky PLP endpoint with:
- pagination (offset/count)
- rotating proxies (host:port or host:port:user:pass)
- rotating visitor_id (UUID-like)
- retries and exponential backoff
- saves per-page JSON and a combined CSV

Usage:
    - Edit PROXIES, CATEGORY_ID, KEY, OUTPUT_PREFIX as needed
    - python redsky_rotate.py
"""

import requests
import time
import random
import csv
import json
import os
import sys
from urllib.parse import urljoin, urlencode
from uuid import uuid4
from datetime import datetime
import pandas as pd

# ----------------- CONFIG -----------------
# category id (ganti sesuai kebutuhan). Contoh '55r1x' untuk "Beauty"
CATEGORY_ID = "55r1x"

# public key yang sering muncul di URL - ganti jika perlu
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

# base url
BASE_URL = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"

# jumlah item per halaman
COUNT = 24

# store / platform / others (bisa sesuaikan)
PLATFORM = "desktop"
PRICING_STORE_ID = "3991"
CHANNEL = "WEB"
ZIP = "24166"

# proxies list:
# format per entry:
#   - "host:port:username:password"  OR
#   - "host:port"
# contoh:
PROXIES = [
    # "dc.decodo.com:10001:user-scraping-country-us:Zg1wsoj_6A1hdI6orG",
    # "us-proxy.example.com:8000:user:pass",
    # "host:port"  # jika tanpa auth
]

# Jika tidak ada proxy (langsung), set ke [] atau leave empty above.
# BUT: untuk Target sebaiknya gunakan proxy AS agar hasil lebih stabil.

# safety limits
MAX_PAGES = 200
MAX_ATTEMPTS_PER_PAGE = 6
SLEEP_BETWEEN_REQUESTS = 0.8  # base delay between successful requests (seconds)
BACKOFF_BASE = 2.0  # exponential backoff base

# output
OUTPUT_PREFIX = f"target_{CATEGORY_ID}"
OUT_DIR = "results"
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------

def parse_proxy_string(p):
    """Convert proxy string to requests proxies dict.
       Accepts host:port:user:pass OR host:port"""
    if not p:
        return None
    parts = p.split(":")
    if len(parts) == 2:
        host, port = parts
        proxy_url = f"http://{host}:{port}"
    elif len(parts) == 4:
        host, port, user, pw = parts
        proxy_url = f"http://{user}:{pw}@{host}:{port}"
    else:
        # allow full URL as single entry
        if p.startswith("http://") or p.startswith("https://"):
            proxy_url = p
        else:
            raise ValueError(f"Proxy string format not supported: {p}")
    return {"http": proxy_url, "https": proxy_url}

def build_headers(visitor_id=None):
    """Return headers with a (rotated) visitor id and normal UA etc."""
    if visitor_id is None:
        visitor_id = uuid4().hex.upper()
    # user agent chosen to mimic modern Chrome desktop
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
         "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    headers = {
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.target.com/c/beauty/-/N-{CATEGORY_ID}",
        "Origin": "https://www.target.com",
        # visitorId often passed as query param, but some calls also set cookies - we set a cookie header too
        "Cookie": f"visitorId={visitor_id};",
    }
    return headers

def make_params(offset, visitor_id):
    return {
        "category": CATEGORY_ID,
        "count": str(COUNT),
        "offset": str(offset),
        "page": f"/c/{CATEGORY_ID}",
        "platform": PLATFORM,
        "pricing_store_id": PRICING_STORE_ID,
        "spellcheck": "true",
        "visitor_id": visitor_id,
        "zip": ZIP,
        "key": API_KEY,
        "channel": CHANNEL,
        "include_sponsored": "true",
        "include_review_summarization": "true",
        "default_purchasability_filter": "false",
    }

def extract_products_from_response(data):
    """
    Try to locate product list from response JSON.
    Returns list of items (may be empty).
    """
    # The JSON structure may vary; we'll attempt several common paths
    candidates = []
    if not isinstance(data, dict):
        return []
    # common path: data.search.products OR data.search_response.products OR data['search_response']['products']
    possible_paths = [
        ("data", "search", "products"),
        ("data", "search_response", "products"),
        ("search_response", "products"),
        ("products",),
        ("data", "products"),
        ("data", "search", "results"),
    ]
    for path in possible_paths:
        temp = data
        try:
            for key in path:
                temp = temp[key]
            if isinstance(temp, list):
                candidates = temp
                break
        except Exception:
            candidates = []
    # if items are nested product wrappers, we try to extract meaningful fields
    items = []
    for p in candidates:
        # Try several ways to get title/url/price
        title = None
        url = None
        price = None
        itemid = None
        try:
            # some entries have p['item']['product_description']['title']
            if isinstance(p, dict):
                # item id
                itemid = p.get("item", {}).get("tcin") or p.get("tcin") or p.get("id") or p.get("itemId")
                # title
                title = (p.get("item", {}).get("product_description", {}).get("title")
                         or p.get("item", {}).get("title")
                         or p.get("title")
                         or p.get("product_description", {}).get("title", None) if p.get("product_description") else None)
                # url
                # often path in p['item']['enrichment']['buy_url'] or p['item']['url'] or p['item']['tcin']
                if p.get("item", {}).get("enrichment", {}).get("buy_url"):
                    url = p["item"]["enrichment"]["buy_url"]
                elif p.get("canonical_url"):
                    url = p.get("canonical_url")
                elif p.get("item", {}).get("product_description", {}).get("title"):
                    # fallback: build with TCIN if present
                    if itemid:
                        url = f"https://www.target.com/p/-/{itemid}"
                # price
                try:
                    price = p.get("price", {}).get("current_retail") or p.get("item", {}).get("price", {}).get("current_retail")
                except Exception:
                    price = None
        except Exception:
            pass
        # as final fallback, include raw dict for debugging
        items.append({
            "itemid": itemid,
            "title": title,
            "url": url,
            "price": price,
            "raw": p
        })
    return items

def test_proxy(proxy_entry):
    """Quick test proxy via httpbin.org/ip"""
    if not proxy_entry:
        return True, "NO_PROXY"
    try:
        proxies = parse_proxy_string(proxy_entry)
        r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        return (r.status_code == 200, r.text)
    except Exception as e:
        return False, str(e)

def request_with_rotation(offset, proxies_list):
    """
    Attempt to fetch one page (offset) using rotation of proxies+visitor_id.
    Returns tuple (success_bool, response_json or None, used_proxy, used_visitor_id, status_code, reason)
    """
    attempts = 0
    proxy_candidates = proxies_list[:] if proxies_list else [None]
    # Shuffle to avoid using same one first every run
    random.shuffle(proxy_candidates)
    for proxy_entry in proxy_candidates:
        proxies = parse_proxy_string(proxy_entry) if proxy_entry else None
        for try_num in range(MAX_ATTEMPTS_PER_PAGE):
            attempts += 1
            visitor_id = uuid4().hex.upper()
            headers = build_headers(visitor_id=visitor_id)
            params = make_params(offset, visitor_id)
            try:
                # new session per attempt
                s = requests.Session()
                if proxies:
                    s.proxies.update(proxies)
                # give a modest timeout
                resp = s.get(BASE_URL, headers=headers, params=params, timeout=20)
            except requests.RequestException as e:
                # network/proxy failure: backoff and try next visitor/proxy
                wait = BACKOFF_BASE ** (try_num + 1) * 0.2
                print(f"  [WARN] Request exception using proxy={proxy_entry}: {e}  (backoff {wait:.1f}s)")
                time.sleep(wait)
                continue

            status = resp.status_code
            # quick parse for small responses
            text_preview = resp.text[:300].replace("\n", " ")

            if status == 200:
                try:
                    data = resp.json()
                except Exception:
                    print("  [WARN] Response not JSON, saving raw for inspect.")
                    data = None
                # if data contains errors or empty, treat as failure to get items
                if data:
                    # heuristics: if data has meaningful products?
                    items = extract_products_from_response(data)
                    # if items non-empty -> success
                    if items and len(items) > 0:
                        return True, data, proxy_entry, visitor_id, status, "OK"
                    else:
                        # maybe page is valid but no products (last page or category empty)
                        # we'll return success if status 200 but with empty items (caller will check)
                        return True, data, proxy_entry, visitor_id, status, "NO_ITEMS"
                else:
                    # no JSON, but status 200 — return raw
                    return True, resp.text, proxy_entry, visitor_id, status, "RAW_NONJSON"
            else:
                # non-200: log and continue rotating
                print(f"  [INFO] proxy={proxy_entry} visitor={visitor_id} -> status {status}. preview: {text_preview}")
                # if 404, likely category / resource missing for this visitor/param — try rotating visitor_id or proxy
                wait = BACKOFF_BASE ** (try_num + 1) * 0.2
                time.sleep(wait)
                continue
    # exhausted proxies/attempts
    return False, None, None, None, None, "EXHAUSTED"

def save_json_page(data, page_idx, offset):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = os.path.join(OUT_DIR, f"{OUTPUT_PREFIX}_page_{page_idx}_off{offset}_{ts}.json")
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return fname

def main():
    print("=== RedSky Rotating Scraper ===")
    print(f"Category: {CATEGORY_ID}  count={COUNT}")
    print("Proxies configured:", len(PROXIES))
    if PROXIES:
        for p in PROXIES:
            ok, info = test_proxy(p)
            print(" - proxy test:", p, "OK?" , ok)
            if not ok:
                print("   -> proxy test failed:", info)

    all_results = []
    offset = 0
    page_idx = 1
    consecutive_empty_pages = 0

    while page_idx <= MAX_PAGES:
        print(f"\n[PAGE {page_idx}] offset={offset}  (attempting with rotation...)")
        ok, data, used_proxy, visitor_id, status_code, reason = request_with_rotation(offset, PROXIES)
        print("  -> result:", "OK" if ok else "FAILED", f" status_code={status_code}", "reason=", reason, "proxy=", used_proxy, "visitor_id=", visitor_id)
        if not ok:
            print("  [ERROR] Tidak memperoleh respons valid untuk halaman ini. Hentikan scraping.")
            break

        # save raw page for inspection if data present
        if data is not None:
            try:
                saved = save_json_page(data, page_idx, offset)
                print("  [SAVED] JSON saved to", saved)
            except Exception as e:
                print("  [WARN] gagal menyimpan JSON:", e)

        # extract items
        items = extract_products_from_response(data) if isinstance(data, dict) else []
        if not items:
            print("  [INFO] Tidak ada produk ditemukan di halaman ini.")
            consecutive_empty_pages += 1
            if consecutive_empty_pages >= 2:
                print("  [STOP] Banyak halaman kosong berturut-turut. Hentikan.")
                break
        else:
            consecutive_empty_pages = 0
            # normalize items for CSV
            for it in items:
                # flatten possible inner product object
                rec = {
                    "itemid": it.get("itemid"),
                    "title": it.get("title"),
                    "url": it.get("url"),
                    "price": it.get("price")
                }
                all_results.append(rec)

        # progress to next page
        if items and len(items) >= COUNT:
            offset += COUNT
            page_idx += 1
            # delay between pages to be polite
            time.sleep(SLEEP_BETWEEN_REQUESTS + random.random()*0.6)
            continue
        else:
            # fewer items than count -> last page
            print("  [DONE] Halaman berisi kurang dari count; sepertinya halaman terakhir.")
            break

    # save combined CSV & JSON
    if all_results:
        csv_name = os.path.join(OUT_DIR, f"{OUTPUT_PREFIX}_all_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.csv")
        df = pd.DataFrame(all_results)
        df.to_csv(csv_name, index=False, encoding="utf-8-sig")
        print(f"\n[OUTPUT] Saved combined CSV: {csv_name}  (total rows: {len(df)})")
        # also raw combined json
        json_name = os.path.join(OUT_DIR, f"{OUTPUT_PREFIX}_all_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json")
        with open(json_name, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print("[OUTPUT] Saved combined JSON:", json_name)
    else:
        print("\n[OUTPUT] Tidak ada produk yang berhasil dikumpulkan.")

    print("\n=== selesai ===")

if __name__ == "__main__":
    main()
