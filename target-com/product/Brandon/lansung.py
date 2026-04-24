#!/usr/bin/env python3
"""
target_scraper_full.py

Mode:
- ambil TCIN/acin langsung dari file CSV input
- tanpa search_input / tanpa PLP search
- rotate proxy per request
- rotate visitor_id
- retry/backoff
- incremental CSV
- resume index
- dedup TCIN
- struktur data output TIDAK diubah
"""

import requests
import re
import csv
import time
import logging
import os
import uuid
import random
from urllib.parse import urlparse, quote_plus

# ------------------------- CONFIG -------------------------
PROXIES_LIST = [
    "191.96.254.80:6127:arssrhsq:x1vpi09f4v1g",
    "45.61.122.149:6441:arssrhsq:x1vpi09f4v1g",
    "45.61.124.153:6482:arssrhsq:x1vpi09f4v1g",
    "64.64.110.63:6586:arssrhsq:x1vpi09f4v1g",
    "145.223.58.21:6290:arssrhsq:x1vpi09f4v1g",
    "82.23.206.96:5902:arssrhsq:x1vpi09f4v1g",
    "38.154.233.46:5456:arssrhsq:x1vpi09f4v1g",
    "45.61.118.128:5825:arssrhsq:x1vpi09f4v1g",
    "191.96.202.229:6275:arssrhsq:x1vpi09f4v1g",
    "23.27.196.145:6514:arssrhsq:x1vpi09f4v1g",
    "154.6.126.37:6008:arssrhsq:x1vpi09f4v1g",
    "89.249.195.211:6966:arssrhsq:x1vpi09f4v1g",
    "147.124.198.69:5928:arssrhsq:x1vpi09f4v1g",
    "82.24.238.65:6872:arssrhsq:x1vpi09f4v1g",
    "38.154.217.34:7225:arssrhsq:x1vpi09f4v1g",
    "174.140.200.142:6422:arssrhsq:x1vpi09f4v1g",
    "46.202.224.238:5790:arssrhsq:x1vpi09f4v1g",
    "31.57.87.145:5830:arssrhsq:x1vpi09f4v1g",
    "38.154.233.181:5591:arssrhsq:x1vpi09f4v1g",
    "198.46.241.143:6678:arssrhsq:x1vpi09f4v1g",
    "23.27.203.134:6869:arssrhsq:x1vpi09f4v1g",
    "104.168.118.219:6175:arssrhsq:x1vpi09f4v1g",
    "152.232.14.43:7174:arssrhsq:x1vpi09f4v1g",
    "82.26.238.68:6375:arssrhsq:x1vpi09f4v1g",
    "89.249.194.231:6630:arssrhsq:x1vpi09f4v1g",
    "104.232.211.0:5613:arssrhsq:x1vpi09f4v1g",
    "38.154.217.123:7314:arssrhsq:x1vpi09f4v1g",
    "67.227.14.204:6796:arssrhsq:x1vpi09f4v1g",
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



INPUT_CSV_FILE = "tcin-ecos.csv"
INPUT_TCIN_COLUMNS = ["acin", "tcin", "TCIN", "Acin", "Tcin"]

category_PDF = "ECOS"
file_save = f"{category_PDF}"

REQUEST_TIMEOUT = 5
SLEEP_BETWEEN = 0.95
CSV_FILE = f"{file_save}.csv"
STATE_FILE = f"{file_save}.txt"
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

MAX_ATTEMPTS = 5
BACKOFF_BASE = 2.5
STORE_ID = 3991

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("target_scraper")

CSV_HEADER = [
    "Product ID","SKU","Product Name","Product Variant Name","Product Brand","Category","Category PDF","Ingredients", "Allergens & Warnings","Description","Product URL","Image URL","Price"
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

def write_state(index_value):
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        fh.write(str(int(index_value)))

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
                    tcins.add(str(t).strip())
    except Exception:
        pass
    return tcins

def normalize_tcin_value(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    # ambil digit saja jika ada noise
    digits = re.sub(r"\D+", "", text)
    if digits:
        return digits

    return text

def load_input_tcins(input_csv_file):
    if not os.path.exists(input_csv_file):
        raise FileNotFoundError(f"Input CSV tidak ditemukan: {input_csv_file}")

    tcins = []
    seen = set()

    with open(input_csv_file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError("Input CSV tidak memiliki header/kolom.")

        for row in reader:
            raw_value = None
            for col in INPUT_TCIN_COLUMNS:
                if col in row and row[col]:
                    raw_value = row[col]
                    break

            tcin = normalize_tcin_value(raw_value)
            if not tcin:
                continue

            if tcin in seen:
                continue

            seen.add(tcin)
            tcins.append(tcin)

    return tcins


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

def main(start_index=None):
    log.info("Mulai scraper dari CSV input.")
    log.info("Input CSV: %s", INPUT_CSV_FILE)

    input_tcins = load_input_tcins(INPUT_CSV_FILE)
    log.info("Total TCIN unik dari input: %s", len(input_tcins))

    start_idx = read_state() if start_index is None else int(start_index)
    if start_idx < 0:
        start_idx = 0

    csv_fh, writer = ensure_csv_header(CSV_FILE, CSV_HEADER)
    existing_tcins = load_existing_tcins(CSV_FILE)

    total_saved = 0
    total_processed = 0

    for idx in range(start_idx, len(input_tcins)):
        if NUM_PRODUCTS_TO_FETCH is not None and total_saved >= NUM_PRODUCTS_TO_FETCH:
            log.info("Limit produk tercapai: %s", total_saved)
            break

        tcin = str(input_tcins[idx]).strip()
        if not tcin:
            write_state(idx + 1)
            continue

        log.info("Memproses index=%s | tcin=%s", idx, tcin)

        # kalau parent/TCIN ini sudah pernah tersimpan di output, skip
        if tcin in existing_tcins:
            write_state(idx + 1)
            total_processed += 1
            continue

        try:
            pd_json = fetch_pdp(tcin)
        except Exception as e:
            log.warning("Gagal fetch PDP untuk TCIN %s: %s", tcin, e)
            write_state(idx + 1)
            continue

        if not pd_json:
            write_state(idx + 1)
            continue

        pd = pd_json.get("data", {}).get("product") or {}
        if not pd:
            write_state(idx + 1)
            continue

        item_parent = pd.get("item", {}) or {}
        enrich_parent = item_parent.get("enrichment", {}) or {}
        desc_parent = item_parent.get("product_description", {}) or {}
        parent_title = desc_parent.get("title") or ""

        # breadcrumbs = " > ".join(
        #     bc.get("name", "").title()
        #     for bc in pd.get("category", {}).get("breadcrumbs", []) or []
        #     if bc.get("name")
        # )

# --- PERBAIKAN BREADCRUMBS ---
        category_data = pd.get("category", {}) or {}
        # Coba ambil dari pd['category'], jika kosong coba dari item_parent
        if not category_data:
            category_data = item_parent.get("category", {}) or {}
            
        raw_breadcrumbs = category_data.get("breadcrumbs", []) or []
        
        breadcrumb_list = []
        for bc in raw_breadcrumbs:
            name = bc.get("name")
            if name:
                breadcrumb_list.append(name.strip().title())
        
        breadcrumbs = " > ".join(breadcrumb_list) if breadcrumb_list else ""
        # -----------------------------

        children = pd.get("children") or []

        if children:
            for ch in children:
                child_tcin = str(ch.get("tcin") or "").strip()
                if not child_tcin or child_tcin in existing_tcins:
                    continue

                ch_item = ch.get("item", {}) or {}
                ch_enrich = ch_item.get("enrichment", {}) or {}
                ch_desc = ch_item.get("product_description", {}) or {}

                row = {
                    "Product ID": child_tcin,
                    "SKU": ch_item.get("primary_barcode"),
                    "Product Name": parent_title,
                    "Product Variant Name": ch_desc.get("title") or parent_title,
                    "Product Brand": ch_item.get("primary_brand", {}).get("name"),
                    "Category": breadcrumbs,
                    "Category PDF": f"{category_PDF}",
                    "Ingredients": clean_html((ch_enrich.get("nutrition_facts", {}) or {}).get("ingredients", "")),
                    "Allergens & Warnings": clean_html((ch_enrich.get("nutrition_facts", {}) or {}).get("warning", "")),
                    "Description": clean_html(ch_desc.get("downstream_description", "")),
                    "Product URL": ch_enrich.get("buy_url") or enrich_parent.get("buy_url"),
                    "Image URL": (ch_enrich.get("image_info", {}) or {}).get("primary_image", {}).get("url"),
                    "Price": ch.get("price", {}).get("formatted_current_price") or ch.get("price", {}).get("current_retail"),
                }

                writer.writerow(row)
                csv_fh.flush()
                existing_tcins.add(child_tcin)
                total_saved += 1
                time.sleep(SLEEP_BETWEEN)

        else:
            row = {
                "Product ID": tcin,
                "SKU": item_parent.get("primary_barcode"),
                "Product Name": parent_title,
                "Product Variant Name": parent_title,
                "Product Brand": item_parent.get("primary_brand", {}).get("name"),
                "Category": breadcrumbs,
                "Category PDF": f"{category_PDF}",
                "Ingredients": clean_html((enrich_parent.get("nutrition_facts", {}) or {}).get("ingredients", "")),
                "Allergens & Warnings": clean_html((enrich_parent.get("nutrition_facts", {}) or {}).get("warning", "")),
                "Description": clean_html(desc_parent.get("downstream_description", "")),
                "Product URL": enrich_parent.get("buy_url"),
                "Image URL": (enrich_parent.get("image_info", {}) or {}).get("primary_image", {}).get("url"),
                "Price": pd.get("price", {}).get("formatted_current_price") or pd.get("price", {}).get("current_retail"),
            }

            writer.writerow(row)
            csv_fh.flush()
            existing_tcins.add(tcin)
            total_saved += 1
            time.sleep(SLEEP_BETWEEN)

        total_processed += 1
        write_state(idx + 1)

    csv_fh.close()
    log.info("Selesai. Total processed: %s | Total saved: %s | CSV: %s", total_processed, total_saved, CSV_FILE)


if __name__ == "__main__":
    main()