#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import time
import random
import csv
import html
from urllib.parse import urlparse, quote_plus
from uuid import uuid4
import os

# =========================================================
# KONFIG
# =========================================================

PROXIES = [
    {"server": "http://89.249.194.231:6630", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://191.96.202.229:6275", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://89.249.195.211:6966", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://45.61.122.149:6441", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://45.61.124.153:6482", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://64.64.110.63:6586", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://145.223.58.21:6290", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://82.23.206.96:5902", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://45.61.118.128:5825", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://191.96.202.229:6275", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://23.27.196.145:6514", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://154.6.126.37:6008", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://147.124.198.69:5928", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://82.24.238.65:6872", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://38.154.217.34:7225", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://174.140.200.142:6422", "username": "arssrhsq", "password": "x1vpi09f4v1g"}
]
HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.target.com/",
    "Origin": "https://www.target.com",
    "Connection": "keep-alive",
}

TARGET_NUTRIENTS = [
    "Calories","Total Fat","Saturated Fat","Trans Fat","Cholesterol","Sodium","Total Carbohydrate","Dietary Fiber","Sugars","Added Sugars","Protein","Vitamin A", "Vitamin C", "Vitamin D","Calcium","Iron","Potassium"
]

CATEGORY_ID = "5xszd"
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"
PLP_URL = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
PDP_URL = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"

STORE_ID = "2250"
PER_PAGE = 24

NUM_PRODUCTS_TO_FETCH = None
REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_REQUESTS = 0.8
SLEEP_BETWEEN_PDP = 0.6
MAX_ATTEMPTS_PER_REQUEST = 6
BACKOFF_BASE = 2.0
MAX_EMPTY_PAGES = 2

OUT_DIR = "results_target"
os.makedirs(OUT_DIR, exist_ok=True)

CSV_FILENAME = os.path.join(OUT_DIR, "Frozen_Foods.csv")


# =========================================================
# UTIL PROXY / SESSION / ROTATION
# =========================================================

def build_requests_proxies(proxy_cfg):
    server = proxy_cfg.get("server")
    user = proxy_cfg.get("username", "")
    pwd = proxy_cfg.get("password", "")

    parsed = urlparse(server)
    scheme = parsed.scheme or "http"
    hostport = parsed.netloc or parsed.path

    if user or pwd:
        user_enc = quote_plus(user)
        pwd_enc = quote_plus(pwd)
        proxy_auth = f"{scheme}://{user_enc}:{pwd_enc}@{hostport}"
    else:
        proxy_auth = f"{scheme}://{hostport}"

    return {"http": proxy_auth, "https": proxy_auth}


def get_proxy_candidates():
    if not PROXIES:
        return [None]
    candidates = PROXIES[:]
    random.shuffle(candidates)
    return candidates


def build_headers(visitor_id=None):
    if visitor_id is None:
        visitor_id = uuid4().hex.upper()

    headers = HEADERS_BASE.copy()
    headers["Cookie"] = f"visitorId={visitor_id};"
    return headers


def create_session(proxy_cfg=None, visitor_id=None):
    s = requests.Session()
    s.headers.update(build_headers(visitor_id))
    if proxy_cfg:
        s.proxies.update(build_requests_proxies(proxy_cfg))
    return s


def log_preview_response(resp):
    try:
        return resp.text[:250].replace("\n", " ")
    except Exception:
        return ""


# =========================================================
# REQUEST ROTATION
# =========================================================

def request_json_with_rotation(url, params=None, extra_headers=None, label="REQUEST"):
    proxy_candidates = get_proxy_candidates()

    for proxy_cfg in proxy_candidates:
        for attempt in range(MAX_ATTEMPTS_PER_REQUEST):
            visitor_id = uuid4().hex.upper()
            session = create_session(proxy_cfg=proxy_cfg, visitor_id=visitor_id)

            if extra_headers:
                session.headers.update(extra_headers)

            proxy_label = proxy_cfg["server"] if proxy_cfg else "NO_PROXY"

            try:
                resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                status = resp.status_code

                if status == 200:
                    try:
                        return True, resp.json(), proxy_label, visitor_id, status, "OK"
                    except Exception as e:
                        wait = (BACKOFF_BASE ** (attempt + 1)) * 0.2
                        print(f"[WARN] {label} JSON parse gagal | proxy={proxy_label} | error={e} | backoff={wait:.1f}s")
                        time.sleep(wait)
                        continue

                preview = log_preview_response(resp)
                wait = (BACKOFF_BASE ** (attempt + 1)) * 0.2
                print(f"[INFO] {label} status={status} | proxy={proxy_label} | visitor={visitor_id} | preview={preview}")
                time.sleep(wait)

            except requests.RequestException as e:
                wait = (BACKOFF_BASE ** (attempt + 1)) * 0.2
                print(f"[WARN] {label} exception | proxy={proxy_label} | error={e} | backoff={wait:.1f}s")
                time.sleep(wait)

    return False, None, None, None, None, "EXHAUSTED"


# =========================================================
# PARSING
# =========================================================

def extract_tcin_from_buy_url(buy_url):
    m = re.search(r"/A-(\d+)", buy_url or "")
    return m.group(1) if m else None


def get_rating_data(node):
    rr = node.get("ratings_and_reviews", {}).get("statistics", {})
    raw_rating = rr.get("rating", {}).get("average")
    count = rr.get("rating", {}).get("count", "")
    return raw_rating, count


def extract_nutrients(nutrition_node):
    nut_dict = {
        "Serving Size": "",
        "Serving Size Unit": "",
        "Servings Per Container": ""
    }

    for name in TARGET_NUTRIENTS:
        nut_dict[f"{name} quantity"] = ""
        nut_dict[f"{name} unit"] = ""
        nut_dict[f"{name} percentage"] = ""

    prepared_list = nutrition_node.get("value_prepared_list", [])
    if prepared_list:
        p_node = prepared_list[0]

        raw_ss = p_node.get("serving_size", "")
        if raw_ss:
            try:
                if str(raw_ss).replace('.', '', 1).isdigit():
                    nut_dict["Serving Size"] = f"{float(raw_ss):g}"
                else:
                    nut_dict["Serving Size"] = raw_ss
            except Exception:
                nut_dict["Serving Size"] = raw_ss

        nut_dict["Serving Size Unit"] = p_node.get("serving_size_unit_of_measurement", "")
        nut_dict["Servings Per Container"] = p_node.get("servings_per_container", "")

        nutrients = p_node.get("nutrients", [])
        for n in nutrients:
            name = n.get("name")
            if name in TARGET_NUTRIENTS:
                raw_qty = n.get("quantity")
                if raw_qty is not None and raw_qty != "":
                    try:
                        nut_dict[f"{name} quantity"] = f"{float(raw_qty):g}"
                    except Exception:
                        nut_dict[f"{name} quantity"] = raw_qty

                nut_dict[f"{name} unit"] = n.get("unit_of_measurement", "")

                raw_pct = n.get("percentage")
                if raw_pct is not None and raw_pct != "":
                    try:
                        clean_pct = f"{float(raw_pct):g}"
                        nut_dict[f"{name} percentage"] = f"{clean_pct}%"
                    except Exception:
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
        clean_text = re.sub(r"<[^>]+>", "", b)
        if ":" in clean_text:
            key, val = clean_text.split(":", 1)
            bullet_map[key.strip().lower()] = val.strip()

    origin_from_handling = item.get("handling", {}).get("import_designation_description", "")
    final_origin = origin_from_handling if origin_from_handling else bullet_map.get("origin", "")

    raw_title = desc.get("title", "")
    clean_title = html.unescape(raw_title) if raw_title else ""

    raw_upc = item.get("primary_barcode", "")
    upc_formatted = f"'{raw_upc}" if raw_upc else ""

    node_rating, node_count = get_rating_data(node)
    final_rating = node_rating if node_rating else inherited_rating
    final_count = node_count if node_count else inherited_count

    try:
        rounded_rating = round(float(final_rating), 1) if final_rating not in (None, "", 0) else ""
    except Exception:
        rounded_rating = ""

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


# =========================================================
# FETCH PLP / PDP
# =========================================================

def fetch_plp_page(offset):
    visitor_id = uuid4().hex.upper()

    params = {
        "category": CATEGORY_ID,
        "count": str(PER_PAGE),
        "offset": str(offset),
        "page": f"/c/{CATEGORY_ID}",
        "platform": "desktop",
        "pricing_store_id": STORE_ID,
        "spellcheck": "true",
        "visitor_id": visitor_id,
        "key": API_KEY,
        "channel": "WEB",
        "include_sponsored": "true",
        "include_review_summarization": "true",
        "default_purchasability_filter": "false",
    }

    ok, data, proxy_used, vid_used, status, reason = request_json_with_rotation(
        PLP_URL,
        params=params,
        label=f"PLP offset={offset}"
    )

    print(f"[PLP] offset={offset} | ok={ok} | status={status} | reason={reason} | proxy={proxy_used} | visitor={vid_used}")
    return ok, data


def fetch_pdp_page(tcin):
    params = {
        "tcin": tcin,
        "is_bot": "false",
        "pricing_store_id": STORE_ID,
        "key": API_KEY,
    }

    ok, data, proxy_used, vid_used, status, reason = request_json_with_rotation(
        PDP_URL,
        params=params,
        label=f"PDP tcin={tcin}"
    )

    print(f"[PDP] tcin={tcin} | ok={ok} | status={status} | reason={reason} | proxy={proxy_used} | visitor={vid_used}")
    return ok, data


# =========================================================
# MAIN
# =========================================================

def main():
    print("=== TARGET SCRAPER WITH ROTATION ===")
    print(f"Category ID: {CATEGORY_ID}")
    print(f"Store ID   : {STORE_ID}")
    print(f"Proxies    : {len(PROXIES)}")

    ok, first_page = fetch_plp_page(0)
    if not ok or not isinstance(first_page, dict):
        print("[ERROR] Gagal mengambil halaman pertama.")
        return

    total_results = first_page.get("data", {}).get("search", {}).get("total_results", 0)
    if not total_results:
        print("[INFO] total_results kosong. Pakai fallback 1755.")
        total_results = 1755

    total_pages = (total_results + PER_PAGE - 1) // PER_PAGE
    print(f"[INFO] total_results={total_results} | total_pages={total_pages}")

    global_counter = 0
    products_data = []
    seen_tcins = set()
    empty_pages = 0

    for page_no in range(total_pages):
        offset = page_no * PER_PAGE
        print(f"\n=== PAGE {page_no + 1}/{total_pages} | offset={offset} ===")

        ok, plp_json = fetch_plp_page(offset)
        if not ok or not isinstance(plp_json, dict):
            print(f"[WARN] Gagal fetch PLP offset={offset}, skip.")
            continue

        products = plp_json.get("data", {}).get("search", {}).get("products", [])

        if not products:
            print("[INFO] Halaman kosong.")
            empty_pages += 1
            if empty_pages >= MAX_EMPTY_PAGES:
                print("[STOP] Terlalu banyak halaman kosong berturut-turut.")
                break
            continue
        else:
            empty_pages = 0

        for p in products:
            if NUM_PRODUCTS_TO_FETCH is not None and global_counter >= NUM_PRODUCTS_TO_FETCH:
                break

            buy_url = (
                p.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url")
                or p.get("item", {}).get("enrichment", {}).get("buy_url")
            )
            tcin = extract_tcin_from_buy_url(buy_url)

            if not tcin:
                tcin = (
                    p.get("parent", {}).get("item", {}).get("tcin")
                    or p.get("item", {}).get("tcin")
                    or p.get("tcin")
                )

            if not tcin:
                print("[SKIP] TCIN tidak ditemukan.")
                continue

            if tcin in seen_tcins:
                print(f"[SKIP] TCIN duplicate: {tcin}")
                continue

            print(f"Ambil PDP: {tcin}")
            ok, detail_json = fetch_pdp_page(tcin)
            if not ok or not isinstance(detail_json, dict):
                print(f"[WARN] Gagal PDP untuk TCIN {tcin}")
                continue

            product_node = detail_json.get("data", {}).get("product")
            if not product_node:
                print(f"[WARN] data.product kosong untuk TCIN {tcin}")
                continue

            breadcrumbs = product_node.get("category", {}).get("breadcrumbs", [])
            breadcrumb_path = " > ".join(
                [
                    bc.get("name", "").title() if bc.get("name", "").lower() != "target" else "Target"
                    for bc in breadcrumbs
                ]
            )

            p_rating, p_count = get_rating_data(product_node)
            children = product_node.get("children", [])
            if not isinstance(children, list):
                children = []

            if (not p_rating or p_rating == 0) and children:
                p_rating, p_count = get_rating_data(children[0])

            parent_info = parse_item_data(product_node, breadcrumb_path, "No", p_rating, p_count)
            products_data.append(parent_info)

            for child in children:
                child_info = parse_item_data(child, breadcrumb_path, "Yes", p_rating, p_count)
                products_data.append(child_info)

            seen_tcins.add(tcin)
            global_counter += 1

            time.sleep(SLEEP_BETWEEN_PDP + random.random() * 0.5)

        if NUM_PRODUCTS_TO_FETCH is not None and global_counter >= NUM_PRODUCTS_TO_FETCH:
            break

        time.sleep(SLEEP_BETWEEN_REQUESTS + random.random() * 0.6)

    if products_data:
        headers = list(products_data[0].keys())
        with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(products_data)

        print(f"\n[SUCCESS] CSV saved: {CSV_FILENAME}")
        print(f"[SUCCESS] Total parent products processed: {global_counter}")
        print(f"[SUCCESS] Total rows saved (parent + variants): {len(products_data)}")
    else:
        print("\n[OUTPUT] Tidak ada data yang berhasil dikumpulkan.")

    print("\n=== selesai ===")


if __name__ == "__main__":
    main()