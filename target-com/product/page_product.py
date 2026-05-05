import requests
import re
import json
import time
from urllib.parse import urlparse, quote_plus
import random
import csv
import html 

# ---------- KONFIG ----------
PROXIES = [
    {""}
]

HEADERS = {
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

NUM_PRODUCTS_TO_FETCH = None
REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.8

# ---------- UTIL ----------
def build_requests_proxies(proxy_cfg):
    server = proxy_cfg.get("server")
    user = proxy_cfg.get("username", "")
    pwd = proxy_cfg.get("password", "")
    parsed = urlparse(server)
    scheme = parsed.scheme or "http"
    hostport = parsed.netloc or parsed.path
    user_enc = quote_plus(user)
    pwd_enc = quote_plus(pwd)
    proxy_auth = f"{scheme}://{user_enc}:{pwd_enc}@{hostport}"
    return {"http": proxy_auth, "https": proxy_auth}

def get_random_proxy():
    return random.choice(PROXIES)

def extract_tcin_from_buy_url(buy_url):
    m = re.search(r'/A-(\d+)', buy_url or "")
    return m.group(1) if m else None

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


# ---------- SESSION ----------
selected_proxy = get_random_proxy()
proxies = build_requests_proxies(selected_proxy)
session = requests.Session()
session.headers.update(HEADERS)
session.proxies.update(proxies)

store_id = '2250'

def fetch_plp_page(offset):
    id_site = '019CFA2A0A070200A381BD2602D2BA4E'
    url = (
        "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
        "?category=5xszd&count=24&default_purchasability_filter=false"
        "&include_sponsored=true&include_review_summarization=true"
        f"&offset={offset}&page=%2Fc%2F5xszd&platform=desktop&pricing_store_id={store_id}"
        f"&visitor_id={id_site}&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
        "&channel=WEB"
    )
    r = session.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()

# ---------- JALANKAN ----------
first_page = fetch_plp_page(0)
total_results = first_page.get("data", {}).get("search", {}).get("total_results", 1755)
PER_PAGE = 24
total_pages = (total_results + PER_PAGE - 1) // PER_PAGE
global_counter = 0
products_data = []

for page_no in range(total_pages):
    offset = page_no * PER_PAGE
    print(offset)
    try:
        plp_json = fetch_plp_page(offset)
    except: continue
    
    products = plp_json.get("data", {}).get("search", {}).get("products", [])

    for p in products:
        if NUM_PRODUCTS_TO_FETCH is not None and global_counter >= NUM_PRODUCTS_TO_FETCH:
            break

        buy_url = p.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url") or p.get("item", {}).get("enrichment", {}).get("buy_url")
        tcin = extract_tcin_from_buy_url(buy_url)
        if not tcin: continue

        detail_url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
            f"?tcin={tcin}&is_bot=false&pricing_store_id={store_id}&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
        )

        try:
            print(f"Membuka API PDP: {tcin}")
            dr = session.get(detail_url, timeout=REQUEST_TIMEOUT)
            dr.raise_for_status()
            detail_json = dr.json()
        except: continue

        product_node = detail_json.get("data", {}).get("product")
        if not product_node: continue

        breadcrumbs = product_node.get("category", {}).get("breadcrumbs", [])
        breadcrumb_path = " > ".join([bc.get("name", "").title() if bc.get("name", "").lower() != "target" else "Target" for bc in breadcrumbs])

        p_rating, p_count = get_rating_data(product_node)
        children = product_node.get("children", [])
        if not isinstance(children, list): children = []

        if (not p_rating or p_rating == 0) and children:
            p_rating, p_count = get_rating_data(children[0])

        parent_info = parse_item_data(product_node, breadcrumb_path, "No", p_rating, p_count)
        products_data.append(parent_info)

        for child in children:
            child_info = parse_item_data(child, breadcrumb_path, "Yes", p_rating, p_count)
            products_data.append(child_info)

        global_counter += 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    if NUM_PRODUCTS_TO_FETCH is not None and global_counter >= NUM_PRODUCTS_TO_FETCH:
        break

# ---------- CSV SAVING ----------
if products_data:
    csv_filename = "Frozen_Foods.csv"
    headers = list(products_data[0].keys())
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(products_data)
    print(f"\nSelesai! Data disimpan ke {csv_filename}")
