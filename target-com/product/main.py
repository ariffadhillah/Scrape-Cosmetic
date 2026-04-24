import requests
import re
import json
import time
from urllib.parse import urlparse, quote_plus
import random
import csv

# ---------- KONFIG ----------
PROXIES = [
    {"server": "http://191.96.254.80:6127", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://191.96.202.229:6275", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://89.249.195.211:6966", "username": "arssrhsq", "password": "x1vpi09f4v1g"},
    {"server": "http://89.249.194.231:6630", "username": "arssrhsq", "password": "x1vpi09f4v1g"}
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

NUM_PRODUCTS_TO_FETCH = 10
REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.6

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
    """Fungsi helper untuk mengambil rating & count dari node JSON"""
    rr = node.get("ratings_and_reviews", {}).get("statistics", {})
    raw_rating = rr.get("rating", {}).get("average")
    count = rr.get("rating", {}).get("count", "")
    return raw_rating, count

def extract_nutrients(nutrition_node):
    nut_dict = {}
    for name in TARGET_NUTRIENTS:
        nut_dict[f"{name} quantity"] = ""
        nut_dict[f"{name} unit"] = ""
        nut_dict[f"{name} percentage"] = ""
    
    prepared_list = nutrition_node.get("value_prepared_list", [])
    if prepared_list:
        nutrients = prepared_list[0].get("nutrients", [])
        for n in nutrients:
            name = n.get("name")
            if name in TARGET_NUTRIENTS:
                nut_dict[f"{name} quantity"] = n.get("quantity")
                nut_dict[f"{name} unit"] = n.get("unit_of_measurement")
                nut_dict[f"{name} percentage"] = n.get("percentage", "")
    return nut_dict

# ---------- SESSION ----------
selected_proxy = get_random_proxy()
proxies = build_requests_proxies(selected_proxy)
session = requests.Session()
session.headers.update(HEADERS)
session.proxies.update(proxies)

def fetch_plp_page(offset):
    id_site = '019A62A8EEE8020199CEE3E689734F84'
    url = (
        "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
        "?category=5xszd&count=24&default_purchasability_filter=false"
        "&include_sponsored=true&include_review_summarization=true"
        f"&offset={offset}&page=%2Fc%2F5xszd&platform=desktop&pricing_store_id=3991"
        f"&visitor_id={id_site}&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
        "&channel=WEB"
    )
    r = session.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()

# def parse_item_data(node, breadcrumb_path, is_variant="No", inherited_rating=None, inherited_count=None):
#     """Fungsi inti untuk parsing data produk/varian"""
#     item = node.get("item", {})
#     enrichment = item.get("enrichment", {})
#     desc = item.get("product_description", {})
    
#     raw_upc = item.get("primary_barcode", "")
#     upc_formatted = f"'{raw_upc}" if raw_upc else ""

#     # Ambil rating asli dari node ini
#     node_rating, node_count = get_rating_data(node)
    
#     # Jika kosong, gunakan data warisan (inheritance)
#     final_rating = node_rating if node_rating else inherited_rating
#     final_count = node_count if node_count else inherited_count
    
#     rounded_rating = round(float(final_rating), 1) if final_rating else ""

#     base_data = {
#         "Title": desc.get("title"),
#         "TCIN": node.get("tcin"),
#         "UPC": upc_formatted,
#         "Primary Brand": item.get("primary_brand", {}).get("name"),
#         "Rating": rounded_rating,
#         "Total Review Count": final_count,
#         "Description": desc.get("downstream_description"),
#         "Ingredients": enrichment.get("nutrition_facts", {}).get("ingredients"),
#         "Product Link": enrichment.get("buy_url"),
#         "Product Image Link": enrichment.get("image_info", {}).get("primary_image", {}).get("url"),
#         "Price": node.get("price", {}).get("formatted_current_price") or node.get("price", {}).get("current_retail"),
#         "Breadcrumbs": breadcrumb_path,
#         "Is Variant": is_variant
#     }
    
#     nutrition_data = extract_nutrients(enrichment.get("nutrition_facts", {}))
#     return {**base_data, **nutrition_data}




def parse_item_data(node, breadcrumb_path, is_variant="No", inherited_rating=None, inherited_count=None):
    """Fungsi inti untuk parsing data produk/varian dengan kolom spesifik"""
    item = node.get("item", {})
    enrichment = item.get("enrichment", {})
    desc = item.get("product_description", {})
    
    # Ambil bullet descriptions dari enrichment
    bullets = enrichment.get("product_description", {}).get("bullet_descriptions", [])
    
    # Fungsi helper untuk mencari teks berdasarkan label (misal: "Form:")
    def get_bullet_value(label):
        for b in bullets:
            clean_b = re.sub(r'<[^>]+>', '', b) # Hapus tag <b>
            if clean_b.startswith(label):
                return clean_b.replace(label, "").strip()
        return ""

    raw_upc = item.get("primary_barcode", "")
    upc_formatted = f"'{raw_upc}" if raw_upc else ""

    node_rating, node_count = get_rating_data(node)
    final_rating = node_rating if node_rating else inherited_rating
    final_count = node_count if node_count else inherited_count
    rounded_rating = round(float(final_rating), 1) if final_rating else ""

    # Mapping variabel sesuai permintaan Komandan
    base_data = {
        "Title": desc.get("title"),
        "TCIN": node.get("tcin"),
        "UPC": upc_formatted,
        "DPCI": item.get("dpci"),
        "Primary Brand": item.get("primary_brand", {}).get("name"),
        "Rating": rounded_rating,
        "Total Review Count": final_count,
        
        # Data dari Bullets (Kolom Terpisah)
        "Features": get_bullet_value("Features:"),
        "Form": get_bullet_value("Form:"),
        "State of Readiness": get_bullet_value("State of Readiness:"),
        "Package Quantity": get_bullet_value("Package Quantity:"),
        "Pre-package preparation": get_bullet_value("Pre-package preparation:"),
        "Net weight": get_bullet_value("Net weight:"),
        "Country of Origin": get_bullet_value("Country of Origin:"),
        "Origin": get_bullet_value("Origin:"),
        
        "Description": desc.get("downstream_description"),
        "Grocery Disclaimer": desc.get("disclaimer"), # Target biasanya taruh di field disclaimer
        "Ingredients": enrichment.get("nutrition_facts", {}).get("ingredients"),
        "Product Link": enrichment.get("buy_url"),
        "Product Image Link": enrichment.get("image_info", {}).get("primary_image", {}).get("url"),
        "Price": node.get("price", {}).get("formatted_current_price") or node.get("price", {}).get("current_retail"),
        "Breadcrumbs": breadcrumb_path,
        "Is Variant": is_variant
    }
    
    nutrition_data = extract_nutrients(enrichment.get("nutrition_facts", {}))
    return {**base_data, **nutrition_data}


# ---------- JALANKAN PROSES ----------
first_page = fetch_plp_page(0)
total_results = first_page.get("data", {}).get("search", {}).get("total_results", 10)
PER_PAGE = 24
total_pages = (total_results + PER_PAGE - 1) // PER_PAGE
global_counter = 0
products_data = []

for page_no in range(total_pages):
    offset = page_no * PER_PAGE
    plp_json = fetch_plp_page(offset)
    products = plp_json.get("data", {}).get("search", {}).get("products", [])

    for p in products:
        if NUM_PRODUCTS_TO_FETCH is not None and global_counter >= NUM_PRODUCTS_TO_FETCH:
            break

        buy_url = p.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url") or p.get("item", {}).get("enrichment", {}).get("buy_url")
        tcin = extract_tcin_from_buy_url(buy_url)
        if not tcin: continue

        detail_url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
            f"?tcin={tcin}&is_bot=false&pricing_store_id=3991&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
        )

        try:
            print("Membuka API PDP:", detail_url)
            dr = session.get(detail_url, timeout=REQUEST_TIMEOUT)
            dr.raise_for_status()
            detail_json = dr.json()
        except:
            continue

        product_node = detail_json.get("data", {}).get("product")
        if not product_node: continue

        # Ambil Breadcrumbs
        breadcrumbs = product_node.get("category", {}).get("breadcrumbs", [])
        breadcrumb_path = " > ".join([bc.get("name", "").title() if bc.get("name", "").lower() != "target" else "Target" for bc in breadcrumbs])

        # Cek Varian
        children = product_node.get("children", [])
        if not isinstance(children, list): children = []

        # Ambil rating awal dari parent
        p_rating, p_count = get_rating_data(product_node)

        # LOGIKA PERBAIKAN: Jika parent kosong, ambil rating dari anak pertama
        if (not p_rating or p_rating == 0) and children:
            p_rating, p_count = get_rating_data(children[0])

        # Simpan Produk Utama (Parent)
        parent_info = parse_item_data(product_node, breadcrumb_path, "No", p_rating, p_count)
        products_data.append(parent_info)

        # Simpan Semua Varian (Children)
        for child in children:
            # Varian biasanya sudah punya rating sendiri atau ikut parent
            child_info = parse_item_data(child, breadcrumb_path, "Yes", p_rating, p_count)
            products_data.append(child_info)

        global_counter += 1
        print(f"Berhasil: {tcin} | Rating: {parent_info.get('Rating')} | Reviews: {parent_info.get('Total Review Count')}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    if NUM_PRODUCTS_TO_FETCH is not None and global_counter >= NUM_PRODUCTS_TO_FETCH:
        break

# ---------- CSV SAVING ----------
if products_data:
    csv_filename = "Frozen_Foods_with_Reviews.csv"
    headers = list(products_data[0].keys())
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(products_data)
    print(f"\nSelesai! Data disimpan ke {csv_filename}")