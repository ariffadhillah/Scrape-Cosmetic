#!/usr/bin/env python3
"""
target_scraper_full.py

Search-mode version for Target search URLs, for example:
https://www.target.com/s?searchTerm=Cocokind

Perubahan:
- tetap pakai rotate proxy per request
- rotate visitor_id
- retry/backoff
- incremental CSV
- resume offset
- dedup TCIN
- fetch search PLP + PDP stabil
- struktur data CSV TIDAK diubah
"""

import requests
import re
import csv
import time
import logging
import os
import uuid
import random
from urllib.parse import (
    urlparse,
    quote_plus,
    parse_qs,
    unquote_plus,
)

# ------------------------- CONFIG -------------------------
PROXIES_LIST = [
    ""
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Accept": "application/json",
    "Referer": "https://www.target.com/",
    "Origin": "https://www.target.com",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.5",
}

NUM_PRODUCTS_TO_FETCH = None

file_save = "Cocokind_Search"
search_input = "https://www.target.com/s?searchTerm=Cocokind"

REQUEST_TIMEOUT = 15
SLEEP_BETWEEN = 0.45
CSV_FILE = f"{file_save}.csv"
STATE_FILE = f"{file_save}.txt"
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

MAX_CONSECUTIVE_EMPTY = 20
PER_PAGE = 24
MAX_ATTEMPTS = 5
BACKOFF_BASE = 1.5
STORE_ID = 3991
ZIP_CODE = "23362"
MAX_OFFSET = 3000

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("target_scraper")

CSV_HEADER = [
    "Brand", "Product Name", "Product Name Color", "Category",
    "Product Link", "Product Image Link", "TCIN", "UPC", "Price",
    "Ingredients", "Description"
]

# ------------------------- UTIL -------------------------

def clean_html(raw):
    if not raw:
        return ""

    text = raw
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"\s*<li>\s*", "\n• ", text, flags=re.I)
    text = re.sub(r"</li>", "", text, flags=re.I)
    text = re.sub(r"</?ul>", "", text, flags=re.I)
    text = re.sub(r"</?b>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()

def get_random_proxy_config():
    proxy_str = random.choice(PROXIES_LIST)
    ip, port, user, pw = proxy_str.split(":")
    return {
        "server": f"http://{ip}:{port}",
        "username": user,
        "password": pw
    }

def build_proxies(cfg):
    parsed = urlparse(cfg["server"])
    scheme = parsed.scheme or "http"
    hostport = parsed.netloc or parsed.path
    auth = f"{quote_plus(cfg['username'])}:{quote_plus(cfg['password'])}"
    proxy_url = f"{scheme}://{auth}@{hostport}"
    return {"http": proxy_url, "https": proxy_url}

def make_session(proxy_cfg=None, visitor_id=None):
    s = requests.Session()
    s.headers.update(HEADERS)
    if visitor_id:
        s.headers["Cookie"] = f"visitorId={visitor_id};"
    if proxy_cfg:
        s.proxies.update(build_proxies(proxy_cfg))
    return s

def extract_tcin(buy_url: str):
    if not buy_url:
        return None
    m = re.search(r"/A-(\d+)", buy_url)
    return m.group(1) if m else None

def random_visitor_id():
    return uuid.uuid4().hex.upper()

def ensure_csv_header(filename, header):
    write_header = not os.path.exists(filename)
    f = open(filename, "a", newline="", encoding="utf-8-sig")
    writer = csv.DictWriter(f, fieldnames=header)
    if write_header:
        writer.writeheader()
    return f, writer

def read_state():
    if not os.path.exists(STATE_FILE):
        return 0
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return int(fh.read().strip() or "0")
    except Exception:
        return 0

def write_state(offset):
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        fh.write(str(int(offset)))

def load_existing_tcins(csv_file):
    if not os.path.exists(csv_file):
        return set()
    tcins = set()
    try:
        with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                t = r.get("TCIN") or r.get("tcin") or ""
                if t:
                    tcins.add(str(t))
    except Exception:
        pass
    return tcins

def get_buy_url_from_product(prod):
    candidates = [
        prod.get("item", {}).get("enrichment", {}).get("buy_url"),
        prod.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url"),
        prod.get("item", {}).get("enrichment", {}).get("product_url"),
    ]
    for c in candidates:
        if c:
            return c
    return None


# ------------------------- SEARCH INPUT PARSER -------------------------

def parse_search_input(raw_value: str):
    """
    Support:
    - 'Cocokind'
    - 'https://www.target.com/s?searchTerm=Cocokind'
    """
    raw = (raw_value or "").strip()
    term = raw

    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        qs = parse_qs(parsed.query)

        term = (
            qs.get("searchTerm", [None])[0]
            or qs.get("term", [None])[0]
            or qs.get("q", [None])[0]
            or ""
        )

        term = unquote_plus(term).strip()

    return {
        "raw": raw,
        "term": term,
    }


SEARCH_INFO = parse_search_input(search_input)


# ------------------------- EXTRACTION HELPERS -------------------------

def build_search_page_variants(term: str):
    """
    Beberapa variasi page / keyword agar endpoint lebih fleksibel.
    """
    clean_term = (term or "").strip()
    if not clean_term:
        return []

    encoded = quote_plus(clean_term)
    variants = []
    seen = set()

    page_variants = [
        f"/s?searchTerm={clean_term}",
        f"/s?searchTerm={encoded}",
        "/s",
    ]

    keyword_keys = ["keyword", "searchTerm", "term", "q"]

    for key_name in keyword_keys:
        for page_value in page_variants:
            key = (key_name, clean_term, page_value)
            if key in seen:
                continue
            seen.add(key)

            params = {
                key_name: clean_term,
                "count": PER_PAGE,
                "default_purchasability_filter": "false",
                "include_sponsored": "true",
                "include_review_summarization": "true",
                "offset": 0,  # nanti di-overwrite
                "page": page_value,
                "platform": "desktop",
                "pricing_store_id": STORE_ID,
                "spellcheck": "true",
                "visitor_id": random_visitor_id(),
                "zip": ZIP_CODE,
                "key": API_KEY,
                "channel": "WEB",
                "include_dmc_dmr": "false",
            }
            variants.append(params)

    return variants


SEARCH_PARAM_TEMPLATES = build_search_page_variants(SEARCH_INFO["term"])


# ------------------------- REQUESTS -------------------------

def request_json_with_rotation(url, params, label):
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        proxy_cfg = get_random_proxy_config()
        visitor_id = random_visitor_id()

        req_params = dict(params)
        req_params["visitor_id"] = visitor_id

        session = make_session(proxy_cfg=proxy_cfg, visitor_id=visitor_id)

        try:
            resp = session.get(url, params=req_params, timeout=REQUEST_TIMEOUT)
            status = resp.status_code

            if status == 200:
                return resp.json()

            if status in (400, 404):
                log.warning("%s status=%s", label, status)
                return None

            if status in (429, 500, 502, 503, 504):
                wait = BACKOFF_BASE ** attempt
                log.warning("%s status=%s retry %s/%s wait %.1fs", label, status, attempt, MAX_ATTEMPTS, wait)
                time.sleep(wait)
                continue

            resp.raise_for_status()

        except requests.RequestException as e:
            last_error = e
            wait = BACKOFF_BASE ** attempt
            log.warning("%s exception retry %s/%s: %s | wait %.1fs", label, attempt, MAX_ATTEMPTS, e, wait)
            time.sleep(wait)

    if last_error:
        raise last_error
    return None


def fetch_search_variants(offset):
    base = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"

    for template in SEARCH_PARAM_TEMPLATES:
        params = dict(template)
        params["offset"] = offset

        term_key = None
        for k in ("keyword", "searchTerm", "term", "q"):
            if k in params:
                term_key = k
                break

        try:
            data = request_json_with_rotation(
                base,
                params,
                label=f"SEARCH offset={offset} {term_key}={params.get(term_key)} page={params.get('page')}"
            )
            if data:
                return data
        except Exception as e:
            log.warning(
                "SEARCH variant gagal offset=%s %s=%s page=%s: %s",
                offset,
                term_key,
                params.get(term_key),
                params.get("page"),
                e
            )

    return None


def fetch_pdp(tcin):
    base = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
    params = {
        "tcin": tcin,
        "is_bot": "false",
        "pricing_store_id": STORE_ID,
        "has_pricing_store_id": "true",
        "has_financing_options": "true",
        "include_obsolete": "true",
        "skip_personalized": "true",
        "skip_variation_hierarchy": "true",
        "channel": "WEB",
        "key": API_KEY,
    }

    return request_json_with_rotation(base, params, label=f"PDP tcin={tcin}")


# ------------------------- MAIN -------------------------

def main(start_offset=None):
    log.info("Mulai scraper.")
    log.info("Search term parsed: %s", SEARCH_INFO["term"])

    offset = read_state() if start_offset is None else int(start_offset)

    csv_fh, writer = ensure_csv_header(CSV_FILE, CSV_HEADER)
    existing_tcins = load_existing_tcins(CSV_FILE)

    total_saved = 0
    consecutive_empty = 0
    total_results = None

    first_json = fetch_search_variants(offset)
    if first_json and isinstance(first_json, dict):
        total_results = first_json.get("data", {}).get("search", {}).get("total_results")
        log.info("Total reported oleh API: %s", total_results)
    else:
        log.warning("Gagal membaca first search PLP. Lanjut dengan heuristik offset.")

    page_idx = offset // PER_PAGE

    while True:
        if NUM_PRODUCTS_TO_FETCH is not None and total_saved >= NUM_PRODUCTS_TO_FETCH:
            log.info("Limit produk tercapai: %s", total_saved)
            break

        cur_offset = page_idx * PER_PAGE
        if cur_offset > MAX_OFFSET:
            log.info("Mencapai MAX_OFFSET=%s. Stop.", MAX_OFFSET)
            break

        log.info("Memuat halaman offset=%s", cur_offset)

        try:
            plp_json = fetch_search_variants(cur_offset)
        except Exception as e:
            log.error("Gagal fetch search PLP offset=%s: %s", cur_offset, e)
            consecutive_empty += 1
            if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                log.warning("Terlalu banyak halaman gagal/kosong berturut-turut. Stop.")
                break
            page_idx += 1
            write_state(cur_offset + PER_PAGE)
            continue

        if not plp_json:
            log.warning("Search PLP kosong untuk offset=%s", cur_offset)
            consecutive_empty += 1
            if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                log.warning("Terlalu banyak halaman kosong berturut-turut. Stop.")
                break
            page_idx += 1
            write_state(cur_offset + PER_PAGE)
            continue

        products = plp_json.get("data", {}).get("search", {}).get("products", []) or []
        log.info("  → ditemukan %s produk", len(products))

        if not products:
            consecutive_empty += 1
            if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                log.warning("Terlalu banyak halaman kosong berturut-turut. Stop.")
                break
            page_idx += 1
            write_state(cur_offset + PER_PAGE)
            continue

        consecutive_empty = 0

        for prod in products:
            if NUM_PRODUCTS_TO_FETCH is not None and total_saved >= NUM_PRODUCTS_TO_FETCH:
                break

            buy_url = get_buy_url_from_product(prod)
            tcin = extract_tcin(buy_url)

            if not tcin:
                tcin = prod.get("tcin") or prod.get("product_id")

            if not tcin:
                continue

            tcin = str(tcin)

            if tcin in existing_tcins:
                continue

            try:
                pd_json = fetch_pdp(tcin)
            except Exception as e:
                log.warning("Gagal fetch PDP untuk TCIN %s: %s", tcin, e)
                continue

            if not pd_json:
                continue

            pd = pd_json.get("data", {}).get("product") or {}
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
                    child_tcin = str(ch.get("tcin") or "")
                    if not child_tcin or child_tcin in existing_tcins:
                        continue

                    ch_item = ch.get("item", {}) or {}
                    ch_enrich = ch_item.get("enrichment", {}) or {}
                    ch_desc = ch_item.get("product_description", {}) or {}

                    row = {
                        "Brand": ch_item.get("primary_brand", {}).get("name"),
                        "Product Name": parent_title,
                        "Product Name Color": ch_desc.get("title") or parent_title,
                        "Category": breadcrumbs,
                        "Product Link": ch_enrich.get("buy_url") or buy_url,
                        "Product Image Link": (ch_enrich.get("image_info", {}) or {}).get("primary_image", {}).get("url"),
                        "TCIN": child_tcin,
                        "UPC": ch_item.get("primary_barcode"),
                        "Price": ch.get("price", {}).get("formatted_current_price") or ch.get("price", {}).get("current_retail"),
                        "Ingredients": clean_html((ch_enrich.get("nutrition_facts", {}) or {}).get("ingredients", "")),
                        "Description": clean_html(ch_desc.get("downstream_description", "")),
                    }

                    writer.writerow(row)
                    csv_fh.flush()
                    existing_tcins.add(child_tcin)
                    total_saved += 1
                    time.sleep(SLEEP_BETWEEN)

            else:
                row = {
                    "Brand": item_parent.get("primary_brand", {}).get("name"),
                    "Product Name": parent_title,
                    "Product Name Color": parent_title,
                    "Category": breadcrumbs,
                    "Product Link": buy_url,
                    "Product Image Link": (enrich_parent.get("image_info", {}) or {}).get("primary_image", {}).get("url"),
                    "TCIN": tcin,
                    "UPC": item_parent.get("primary_barcode"),
                    "Price": pd.get("price", {}).get("formatted_current_price") or pd.get("price", {}).get("current_retail"),
                    "Ingredients": clean_html((enrich_parent.get("nutrition_facts", {}) or {}).get("ingredients", "")),
                    "Description": clean_html(desc_parent.get("downstream_description", "")),
                }

                writer.writerow(row)
                csv_fh.flush()
                existing_tcins.add(tcin)
                total_saved += 1
                time.sleep(SLEEP_BETWEEN)

        write_state(cur_offset + PER_PAGE)
        page_idx += 1

        if total_results and page_idx * PER_PAGE >= total_results:
            log.info("Sudah mencapai akhir berdasarkan total_results=%s", total_results)
            break

    csv_fh.close()
    log.info("Selesai. Total saved: %s rows. CSV: %s", total_saved, CSV_FILE)


if __name__ == "__main__":
    main()