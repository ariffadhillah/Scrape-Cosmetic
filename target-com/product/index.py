#!/usr/bin/env python3
"""
target_scraper_full.py

Versi:
- rotate proxy per request
- rotate visitor_id
- retry/backoff
- incremental CSV
- resume offset
- dedup TCIN
- fetch PLP + PDP stabil
- output CSV dari parse_item_data()
- support category token seperti:
  - 5xszd
  - N-5xszd
  - URL lengkap target
"""

import requests
import re
import csv
import time
import logging
import os
import uuid
import random
import html
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
    "67.227.14.204:6796:arssrhsq:x1vpi09f4v1g"
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

file_save = "Snack Variety Packs"
category_input = "https://www.target.com/c/snack-variety-packs-snacks-grocery/-/N-sjs32"

REQUEST_TIMEOUT = 10
SLEEP_BETWEEN = 0.95
CSV_FILE = f"{file_save}-tambahan.csv"
STATE_FILE = f"{file_save}.txt"
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

MAX_CONSECUTIVE_EMPTY = 20
PER_PAGE = 24
MAX_ATTEMPTS = 5
BACKOFF_BASE = 1.5
STORE_ID = 3991
ZIP_CODE = "23362"

TARGET_NUTRIENTS = [
    "Calories","Total Fat","Saturated Fat","Trans Fat","Cholesterol","Sodium","Total Carbohydrate","Dietary Fiber","Sugars","Added Sugars","Protein","Vitamin A", "Vitamin C", "Vitamin D","Calcium","Iron","Potassium"
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("target_scraper")


# ------------------------- CATEGORY NORMALIZER -------------------------

def parse_category_input(raw_value: str):
    """
    Support input:
    - '5xszd'
    - 'N-5xszd'
    - 'https://www.target.com/c/frozen-foods-grocery/-/N-5xszd'
    """
    raw = (raw_value or "").strip()
    slug = None
    token = None
    code = None

    if not raw:
        return {"raw": "", "slug": None, "token": None, "code": None}

    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        path = parsed.path.strip("/")

        # contoh: c/frozen-foods-grocery/-/N-5xszd
        m_slug = re.search(r"/c/([^/]+)/", parsed.path)
        if m_slug:
            slug = m_slug.group(1)

        m_token = re.search(r"/(N-[A-Za-z0-9]+)/?$", parsed.path)
        if m_token:
            token = m_token.group(1)

    else:
        if raw.lower().startswith("n-"):
            token = raw
        else:
            code = raw

    if token and token.lower().startswith("n-"):
        code = token[2:]

    return {
        "raw": raw,
        "slug": slug,
        "token": token,
        "code": code,
    }


def build_category_candidates(raw_value: str):
    info = parse_category_input(raw_value)

    raw = info["raw"]
    slug = info["slug"]
    token = info["token"]
    code = info["code"]

    category_values = []
    page_values = []

    def add_unique(lst, value):
        if value and value not in lst:
            lst.append(value)

    # kandidat category param
    add_unique(category_values, code)
    add_unique(category_values, token)
    add_unique(category_values, raw if raw and not raw.startswith("http") else None)

    # kandidat page param
    if slug and token:
        add_unique(page_values, f"/c/{slug}/-/{token}")
    if slug and code:
        add_unique(page_values, f"/c/{slug}/-/N-{code}")
    if slug:
        add_unique(page_values, f"/c/{slug}")
    if token:
        add_unique(page_values, f"/c/{token}")
        add_unique(page_values, f"/c/-/{token}")
    if code:
        add_unique(page_values, f"/c/{code}")
        add_unique(page_values, f"/c/-/N-{code}")

    # buang nilai None / URL penuh dari category
    category_values = [x for x in category_values if x and not x.startswith("http")]

    # fallback terakhir
    if not category_values and code:
        category_values = [code]
    if not page_values and code:
        page_values = [f"/c/{code}", f"/c/-/N-{code}"]

    return {
        "slug": slug,
        "token": token,
        "code": code,
        "category_values": category_values,
        "page_values": page_values,
    }


CATEGORY_INFO = build_category_candidates(category_input)

# ------------------------- CSV HEADER -------------------------

def build_csv_header():
    header = [
        "Title",
        "TCIN",
        "UPC",
        "DPCI",
        "Primary Brand",
        "Rating",
        "Total Review Count",
        "Features",
        "Form",
        "State of Readiness",
        "Package Quantity",
        "Pre-package preparation",
        "Net weight",
        "Country of Origin",
        "Origin",
        "Ingredients",
        "Allergens & Warnings",
        "Product Link",
        "Product Image Link",
        "Price",
        "Breadcrumbs",
        "Is Variant",
        "Serving Size",
        "Serving Size Unit",
        "Servings Per Container",
    ]
    for name in TARGET_NUTRIENTS:
        header.extend([
            f"{name} quantity",
            f"{name} unit",
            f"{name} percentage"
        ])
    return header

CSV_HEADER = build_csv_header()

# ------------------------- UTIL -------------------------

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

# ------------------------- EXTRACTION HELPERS -------------------------

def get_rating_data(node):
    rr = node.get("ratings_and_reviews", {}).get("statistics", {})
    raw_rating = rr.get("rating", {}).get("average")
    count = rr.get("rating", {}).get("count", "")
    return raw_rating, count

def extract_nutrients(nutrition_node):
    # 1. Inisialisasi dictionary dengan kolom serving info
    nut_dict = {
        "Serving Size": "",
        "Serving Size Unit": "",
        "Servings Per Container": ""
    }
    
    # Inisialisasi kolom nutrisi target
    for name in TARGET_NUTRIENTS:
        nut_dict[f"{name} quantity"] = ""
        nut_dict[f"{name} unit"] = ""
        nut_dict[f"{name} percentage"] = ""
    
    prepared_list = nutrition_node.get("value_prepared_list", [])
    if prepared_list:
        p_node = prepared_list[0]
        
        # Ekstraksi Serving Info
        raw_ss = p_node.get("serving_size", "")
        if raw_ss:
            try:
                # Bersihkan .0 jika angka, biarkan jika teks (misal 2/3)
                if str(raw_ss).replace('.','',1).isdigit():
                    nut_dict["Serving Size"] = f"{float(raw_ss):g}"
                else:
                    nut_dict["Serving Size"] = raw_ss
            except:
                nut_dict["Serving Size"] = raw_ss
        
        nut_dict["Serving Size Unit"] = p_node.get("serving_size_unit_of_measurement", "")
        nut_dict["Servings Per Container"] = p_node.get("servings_per_container", "")

        # Ekstraksi Nutrisi
        nutrients = p_node.get("nutrients", [])
        for n in nutrients:
            name = n.get("name")
            if name in TARGET_NUTRIENTS:
                # Quantity: Bersihkan nol di belakang
                raw_qty = n.get("quantity")
                if raw_qty is not None and raw_qty != "":
                    try:
                        nut_dict[f"{name} quantity"] = f"{float(raw_qty):g}"
                    except:
                        nut_dict[f"{name} quantity"] = raw_qty
                
                nut_dict[f"{name} unit"] = n.get("unit_of_measurement", "")
                
                # Percentage: Bersihkan nol + Tambahkan %
                raw_pct = n.get("percentage")
                if raw_pct is not None and raw_pct != "":
                    try:
                        clean_pct = f"{float(raw_pct):g}"
                        nut_dict[f"{name} percentage"] = f"{clean_pct}%"
                    except:
                        nut_dict[f"{name} percentage"] = f"{raw_pct}%"
                        
    return nut_dict

def parse_item_data(node, breadcrumb_path, is_variant="No", inherited_rating=None, inherited_count=None):
    item = node.get("item", {})
    enrichment = item.get("enrichment", {})
    desc = item.get("product_description", {})
    
    bullets_enrich = enrichment.get("product_description", {}).get("bullet_descriptions", [])
    bullets_item = desc.get("bullet_descriptions", [])
    all_bullets = bullets_enrich if bullets_enrich else bullets_item

    bullet_map = {}
    for b in all_bullets:
        clean_text = re.sub(r'<[^>]+>', '', b)
        if ":" in clean_text:
            key, val = clean_text.split(":", 1)
            bullet_map[key.strip().lower()] = val.strip()

    # Origin dari handling
    origin_from_handling = item.get("handling", {}).get("import_designation_description", "")
    final_origin = origin_from_handling if origin_from_handling else bullet_map.get("origin", "")

    # Clean Title
    raw_title = desc.get("title", "")
    clean_title = html.unescape(raw_title) if raw_title else ""

    raw_upc = item.get("primary_barcode", "")
    upc_formatted = f"'{raw_upc}" if raw_upc else ""
    
    node_rating, node_count = get_rating_data(node)
    final_rating = node_rating if node_rating else inherited_rating
    final_count = node_count if node_count else inherited_count
    rounded_rating = round(float(final_rating), 1) if final_rating else ""

    base_data = {
        "Title": clean_title,
        "TCIN": node.get("tcin"),
        "UPC": upc_formatted,
        "DPCI": item.get("dpci"),
        "Primary Brand": item.get("primary_brand", {}).get("name"),
        "Rating": rounded_rating,
        "Total Review Count": final_count,
        "Features": bullet_map.get("features", ""),
        "Form": bullet_map.get("form", ""),
        "State of Readiness": bullet_map.get("state of readiness", ""),
        "Package Quantity": bullet_map.get("package quantity", ""),
        "Pre-package preparation": bullet_map.get("pre-package preparation", ""),
        "Net weight": bullet_map.get("net weight", ""),
        "Country of Origin": bullet_map.get("country of origin", ""),
        "Origin": final_origin,
        "Ingredients": enrichment.get("nutrition_facts", {}).get("ingredients"),
        "Allergens & Warnings": enrichment.get("nutrition_facts", {}).get("warning"),
        "Product Link": enrichment.get("buy_url"),
        "Product Image Link": enrichment.get("image_info", {}).get("primary_image", {}).get("url"),
        "Price": node.get("price", {}).get("formatted_current_price") or node.get("price", {}).get("current_retail"),
        "Breadcrumbs": breadcrumb_path,
        "Is Variant": is_variant
    }
    
    nutrition_data = extract_nutrients(enrichment.get("nutrition_facts", {}))
    return {**base_data, **nutrition_data}

# ------------------------- REQUESTS -------------------------

def build_plp_param_variants(offset):
    variants = []
    seen = set()

    for category_value in CATEGORY_INFO["category_values"]:
        for page_value in CATEGORY_INFO["page_values"]:
            key = (category_value, page_value)
            if key in seen:
                continue
            seen.add(key)

            variants.append({
                "category": category_value,
                "count": PER_PAGE,
                "default_purchasability_filter": "false",
                "include_sponsored": "true",
                "include_review_summarization": "true",
                "offset": offset,
                "page": page_value,
                "platform": "desktop",
                "pricing_store_id": STORE_ID,
                "spellcheck": "true",
                "visitor_id": random_visitor_id(),
                "zip": ZIP_CODE,
                "key": API_KEY,
                "channel": "WEB",
                "include_dmc_dmr": "false",
            })

    return variants

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

def fetch_plp_variants(offset):
    base = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"

    for params in build_plp_param_variants(offset):
        try:
            data = request_json_with_rotation(
                base,
                params,
                label=f"PLP offset={offset} category={params.get('category')} page={params.get('page')}"
            )
            if data:
                return data
        except Exception as e:
            log.warning(
                "PLP variant gagal offset=%s category=%s page=%s: %s",
                offset, params.get("category"), params.get("page"), e
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
    log.info("Category parsed | slug=%s | token=%s | code=%s",
             CATEGORY_INFO["slug"], CATEGORY_INFO["token"], CATEGORY_INFO["code"])
    log.info("Category values to try: %s", CATEGORY_INFO["category_values"])
    log.info("Page values to try: %s", CATEGORY_INFO["page_values"])

    offset = read_state() if start_offset is None else int(start_offset)

    csv_fh, writer = ensure_csv_header(CSV_FILE, CSV_HEADER)
    existing_tcins = load_existing_tcins(CSV_FILE)

    total_saved = 0
    consecutive_empty = 0
    total_results = None

    first_json = fetch_plp_variants(offset)
    if first_json and isinstance(first_json, dict):
        total_results = first_json.get("data", {}).get("search", {}).get("total_results")
        log.info("Total reported oleh API: %s", total_results)
    else:
        log.warning("Gagal membaca first PLP. Lanjut dengan heuristik offset.")

    page_idx = offset // PER_PAGE

    while True:
        if NUM_PRODUCTS_TO_FETCH is not None and total_saved >= NUM_PRODUCTS_TO_FETCH:
            log.info("Limit produk tercapai: %s", total_saved)
            break

        cur_offset = page_idx * PER_PAGE
        log.info("Memuat halaman offset=%s", cur_offset)

        try:
            plp_json = fetch_plp_variants(cur_offset)
        except Exception as e:
            log.error("Gagal fetch PLP offset=%s: %s", cur_offset, e)
            consecutive_empty += 1
            if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                log.warning("Terlalu banyak halaman gagal/kosong berturut-turut. Stop.")
                break
            page_idx += 1
            write_state(cur_offset)
            continue

        if not plp_json:
            log.warning("PLP kosong untuk offset=%s", cur_offset)
            consecutive_empty += 1
            if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                log.warning("Terlalu banyak halaman kosong berturut-turut. Stop.")
                break
            page_idx += 1
            write_state(cur_offset)
            continue

        products = plp_json.get("data", {}).get("search", {}).get("products", []) or []
        log.info("  → ditemukan %s produk", len(products))

        if not products:
            consecutive_empty += 1
            if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                log.warning("Terlalu banyak halaman kosong berturut-turut. Stop.")
                break
            page_idx += 1
            write_state(cur_offset)
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
            if not pd:
                continue

            breadcrumbs = pd.get("category", {}).get("breadcrumbs", []) or []
            breadcrumb_path = " > ".join(
                [
                    bc.get("name", "").title() if bc.get("name", "").lower() != "target" else "Target"
                    for bc in breadcrumbs
                    if bc.get("name")
                ]
            )

            p_rating, p_count = get_rating_data(pd)
            children = pd.get("children") or []
            if not isinstance(children, list):
                children = []

            if (not p_rating or p_rating == 0) and children:
                p_rating, p_count = get_rating_data(children[0])

            parent_info = parse_item_data(pd, breadcrumb_path, "No", p_rating, p_count)
            parent_tcin = str(parent_info.get("TCIN") or tcin)

            if parent_tcin and parent_tcin not in existing_tcins:
                writer.writerow(parent_info)
                csv_fh.flush()
                existing_tcins.add(parent_tcin)
                total_saved += 1
                time.sleep(SLEEP_BETWEEN)

            for ch in children:
                child_info = parse_item_data(ch, breadcrumb_path, "Yes", p_rating, p_count)
                child_tcin = str(child_info.get("TCIN") or "")

                if not child_tcin or child_tcin in existing_tcins:
                    continue

                writer.writerow(child_info)
                csv_fh.flush()
                existing_tcins.add(child_tcin)
                total_saved += 1
                time.sleep(SLEEP_BETWEEN)

        write_state(cur_offset)
        page_idx += 1

        if total_results and page_idx * PER_PAGE >= total_results:
            log.info("Sudah mencapai akhir berdasarkan total_results=%s", total_results)
            break

    csv_fh.close()
    log.info("Selesai. Total saved: %s rows. CSV: %s", total_saved, CSV_FILE)

if __name__ == "__main__":
    main()