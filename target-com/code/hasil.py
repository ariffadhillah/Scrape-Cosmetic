#!/usr/bin/env python3
"""
target_scraper.py
Versi final: rapih, retry/backoff, variasi endpoint, incremental CSV, resume support.
"""

import requests
import re
import csv
import time
import logging
import os
import uuid
from urllib.parse import urlparse, quote_plus, urlencode

# -------------------------
# CONFIG
# -------------------------
PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Accept": "application/json",
    "Referer": "https://www.target.com/",
}

NUM_PRODUCTS_TO_FETCH = 2213       # jumlah target (None = semua)
REQUEST_TIMEOUT = 15
SLEEP_BETWEEN = 0.6
CSV_FILE = "Makeup_Deals_final.csv"
STATE_FILE = "scrape_state.txt"    # menyimpan last_offset untuk resume

# endpoint key (tetap gunakan key yang sama bila tersedia)
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

# -------------------------
# LOGGING
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("target_scraper")

# -------------------------
# UTIL
# -------------------------
def build_proxies(cfg):
    parsed = urlparse(cfg["server"])
    scheme = parsed.scheme or "http"
    hostport = parsed.netloc or parsed.path
    auth = f"{quote_plus(cfg['username'])}:{quote_plus(cfg['password'])}"
    proxy_url = f"{scheme}://{auth}@{hostport}"
    return {"http": proxy_url, "https": proxy_url}

def extract_tcin(buy_url: str):
    if not buy_url:
        return None
    m = re.search(r"/A-(\d+)", buy_url)
    return m.group(1) if m else None

def ensure_csv_header(filename, header):
    """ buat file CSV dan header bila belum ada """
    write_header = not os.path.exists(filename)
    f = open(filename, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=header)
    if write_header:
        writer.writeheader()
    return f, writer

def read_state():
    if not os.path.exists(STATE_FILE):
        return 0
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            v = int(fh.read().strip() or "0")
            return v
    except Exception:
        return 0

def write_state(offset):
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        fh.write(str(int(offset)))

def random_visitor_id():
    return uuid.uuid4().hex.upper()

# -------------------------
# SESSION (dengan retries sederhana)
# -------------------------
session = requests.Session()
session.headers.update(HEADERS)
session.proxies.update(build_proxies(PROXY))

# -------------------------
# BUILD VARIANT URLS
# -------------------------
def build_plp_urls(offset, visitor_id, category_candidates=("mpo32","6n69n")):
    """
    Kembalikan list URL berbeda untuk dicoba (mpo32 / 6n69n, plus useragent param variant).
    """
    urls = []
    base = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
    for cat in category_candidates:
        # page param must match category slug
        page_enc = "%2Fc%2F" + cat
        qs = {
            "category": cat,
            "count": 24,
            "default_purchasability_filter": "false",
            "include_sponsored": "true",
            "include_review_summarization": "true",
            "offset": offset,
            "page": page_enc,
            "platform": "desktop",
            "pricing_store_id": 3991,
            "spellcheck": "true",
            "visitor_id": visitor_id,
            "zip": "23362",
            "key": API_KEY,
            "channel": "WEB",
            "include_dmc_dmr": "false",
        }
        # normal URL
        urls.append(base + "?" + urlencode(qs, safe="%2F%,:"))
        # variant with useragent param (some Redsky calls include it)
        qs2 = qs.copy()
        qs2["useragent"] = session.headers.get("User-Agent")
        urls.append(base + "?" + urlencode(qs2, safe="%2F%,:"))
    return urls

def fetch_plp_with_variants(offset, visitor_id, max_attempts=4):
    """
    Coba beberapa variant url dan retry/backoff pada error 4xx/5xx.
    Kembalikan JSON response atau raise.
    """
    urls = build_plp_urls(offset, visitor_id)
    attempt = 0
    last_exc = None
    for url in urls:
        attempt = 0
        backoff = 1.0
        while attempt < max_attempts:
            try:
                log.debug("GET %s", url)
                r = session.get(url, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    return r.json()
                # for certain client errors (400/404) maybe try next url variant
                if r.status_code in (400, 404):
                    log.warning("Endpoint returned %s for url: %s", r.status_code, url)
                    break  # coba url variant berikutnya
                # other status codes: raise to be caught below and retried
                r.raise_for_status()
            except requests.RequestException as e:
                last_exc = e
                attempt += 1
                log.warning("Request gagal (attempt %s/%s) -> %s. Backoff %s s", attempt, max_attempts, e, backoff)
                time.sleep(backoff)
                backoff *= 2
        # lanjut ke variant url berikutnya
    # jika sampai sini belum berhasil
    raise last_exc or RuntimeError("Tidak berhasil memanggil PLP API")

def fetch_pdp(tcin, max_attempts=3):
    base = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
    qs = {
        "tcin": tcin,
        "is_bot": "false",
        "pricing_store_id": 3991,
        "has_pricing_store_id": "true",
        "has_financing_options": "true",
        "include_obsolete": "true",
        "skip_personalized": "true",
        "skip_variation_hierarchy": "true",
        "channel": "WEB",
        "key": API_KEY,
    }
    url = base + "?" + urlencode(qs, safe="%2F%,:")
    attempt = 0
    backoff = 1.0
    last_exc = None
    while attempt < max_attempts:
        try:
            r = session.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_exc = e
            attempt += 1
            log.warning("PDP request failed for TCIN %s (attempt %s/%s): %s", tcin, attempt, max_attempts, e)
            time.sleep(backoff)
            backoff *= 2
    raise last_exc

# -------------------------
# EXTRACTION HELPERS
# -------------------------
def get_buy_url(prod):
    # beberapa lokasi potensial untuk buy_url
    candidates = [
        prod.get("item", {}).get("enrichment", {}).get("buy_url"),
        prod.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url"),
        prod.get("item", {}).get("enrichment", {}).get("product_url"),
    ]
    for c in candidates:
        if c:
            return c
    return None

# -------------------------
# CSV HEADER
# -------------------------
CSV_HEADER = [
    "Manufacturer", "Product Name Parent", "Product Name", "Category",
    "Product Link", "Product Image Link", "TCIN", "UPC", "Price", "Ingredients", "Description"
]

# -------------------------
# MAIN
# -------------------------
def main(start_offset=None):
    log.info("Proxy aktif.")
    # resume offset dari state file kecuali user override
    offset = read_state() if start_offset is None else int(start_offset)
    per_page = 24
    visitor_id = random_visitor_id()

    # open CSV (append mode) dan dapatkan writer
    csv_fh, writer = ensure_csv_header(CSV_FILE, CSV_HEADER)

    total_saved = 0
    global_count = 0

    # ambil halaman pertama untuk mengetahui total_results (coba beberapa variant)
    try:
        first_json = fetch_plp_with_variants(offset, visitor_id)
    except Exception as e:
        log.error("Gagal memuat PLP pertama: %s", e)
        csv_fh.close()
        return

    total_results = first_json.get("data", {}).get("search", {}).get("total_results")
    if not isinstance(total_results, int):
        log.warning("total_results tidak terbaca, default gunakan NUM_PRODUCTS_TO_FETCH atau 0.")
        total_results = NUM_PRODUCTS_TO_FETCH or 0

    pages = (total_results + per_page - 1) // per_page
    log.info("Total produk (API): %s ; starting offset=%s ; halaman total ~= %s", total_results, offset, pages)

    # loop halaman mulai dari offset
    page_idx = offset // per_page
    while True:
        if NUM_PRODUCTS_TO_FETCH is not None and total_saved >= NUM_PRODUCTS_TO_FETCH:
            log.info("✅ Limit produk tercapai: %s", total_saved)
            break

        cur_offset = page_idx * per_page
        log.info("Memuat halaman offset=%s (page %s)", cur_offset, page_idx)

        # coba fetch plp
        try:
            plp_json = fetch_plp_with_variants(cur_offset, visitor_id)
        except Exception as e:
            log.error("Gagal fetch halaman offset=%s: %s", cur_offset, e)
            # jika 400/404 terus muncul, coba regenerate visitor_id dan ulangi sekali
            visitor_id = random_visitor_id()
            log.info("Regenerate visitor_id -> %s and retry once", visitor_id)
            try:
                plp_json = fetch_plp_with_variants(cur_offset, visitor_id)
            except Exception as e2:
                log.error("Masih gagal setelah regenerate visitor_id: %s", e2)
                # lanjut ke halaman berikutnya (skip) atau hentikan?
                # kita skip ke halaman berikutnya untuk mencoba lanjut
                page_idx += 1
                write_state(cur_offset)  # save progress
                time.sleep(1)
                continue

        products = plp_json.get("data", {}).get("search", {}).get("products", []) or []
        log.info("  → %s produk ditemukan di offset %s", len(products), cur_offset)

        if not products:
            # kemungkinan API menolak offset besar -> hentikan atau lompat sedikit
            log.warning("Tidak ada produk di offset %s. Hentikan loop untuk menghindari putaran tak berujung.", cur_offset)
            break

        for prod in products:
            if NUM_PRODUCTS_TO_FETCH is not None and total_saved >= NUM_PRODUCTS_TO_FETCH:
                break

            buy_url = get_buy_url(prod)
            tcin = extract_tcin(buy_url)
            if not tcin:
                # skip bila tidak dapat TCIN
                continue

            # ambil detail PDP
            try:
                pd_json = fetch_pdp(tcin)
            except Exception as e:
                log.warning("Gagal fetch PDP untuk tcin %s: %s -- skip", tcin, e)
                continue

            pd = pd_json.get("data", {}).get("product") or {}
            # parent fallback
            item_parent = pd.get("item", {}) or {}
            enrich_parent = item_parent.get("enrichment", {}) or {}
            desc_parent = item_parent.get("product_description", {}) or {}
            parent_title = desc_parent.get("title") or ""

            breadcrumbs = " > ".join(
                bc.get("name", "").title()
                for bc in pd.get("category", {}).get("breadcrumbs", []) or []
                if bc.get("name")
            )

            children = pd.get("children") or []
            if children:
                for ch in children:
                    if NUM_PRODUCTS_TO_FETCH is not None and total_saved >= NUM_PRODUCTS_TO_FETCH:
                        break
                    ch_item = ch.get("item", {}) or {}
                    ch_enrich = ch_item.get("enrichment", {}) or {}
                    ch_desc = ch_item.get("product_description", {}) or {}

                    row = {
                        "Manufacturer": ch_item.get("primary_brand", {}).get("name"),
                        "Product Name Parent": parent_title,
                        "Product Name": ch_desc.get("title") or parent_title,
                        "Category": breadcrumbs,
                        "Product Link": ch_enrich.get("buy_url") or buy_url,
                        "Product Image Link": (ch_enrich.get("image_info", {}) or {}).get("primary_image", {}).get("url"),
                        "TCIN": ch.get("tcin"),
                        "UPC": ch_item.get("primary_barcode"),
                        "Price": ch.get("price", {}).get("formatted_current_price"),
                        "Ingredients": (ch_enrich.get("nutrition_facts", {}) or {}).get("ingredients", ""),
                        "Description": ch_desc.get("downstream_description"),
                    }
                    writer.writerow(row)
                    csv_fh.flush()
                    total_saved += 1
                    global_count += 1
                    time.sleep(SLEEP_BETWEEN)
            else:
                row = {
                    "Manufacturer": item_parent.get("primary_brand", {}).get("name"),
                    "Product Name Parent": parent_title,
                    "Product Name": parent_title,
                    "Category": breadcrumbs,
                    "Product Link": buy_url,
                    "Product Image Link": (enrich_parent.get("image_info", {}) or {}).get("primary_image", {}).get("url"),
                    "TCIN": tcin,
                    "UPC": item_parent.get("primary_barcode"),
                    "Price": pd.get("price", {}).get("formatted_current_price"),
                    "Ingredients": (enrich_parent.get("nutrition_facts", {}) or {}).get("ingredients", ""),
                    "Description": desc_parent.get("downstream_description"),
                }
                writer.writerow(row)
                csv_fh.flush()
                total_saved += 1
                global_count += 1
                time.sleep(SLEEP_BETWEEN)

        # simpan progress (offset) agar bisa resume
        write_state(cur_offset)
        page_idx += 1

        # break kondisi bila sudah iterasi semua halaman menurut API
        if page_idx * per_page >= total_results:
            log.info("Telah mencapai akhir hasil menurut total_results.")
            break

    csv_fh.close()
    log.info("Selesai. Total saved: %s rows. CSV: %s", total_saved, CSV_FILE)


if __name__ == "__main__":
    # jika ingin override start offset, panggil main(1176)
    main()
