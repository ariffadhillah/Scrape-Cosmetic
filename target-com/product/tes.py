# import re
# import json
# import time
# import csv
# import html 
# import os
# import random
# from curl_cffi import requests # Ganti requests standar dengan curl_cffi

# # ---------- KONFIG ----------
# PROXIES_LIST = [
#     "http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127",
#     "http://arssrhsq:x1vpi09f4v1g@191.96.202.229:6275",
#     "http://arssrhsq:x1vpi09f4v1g@89.249.195.211:6966",
#     "http://arssrhsq:x1vpi09f4v1g@89.249.194.231:6630"
# ]

# HEADERS = {
#     "accept": "application/json",
#     "accept-language": "en-US,en;q=0.9",
#     "referer": "https://www.target.com/c/frozen-foods/-/N-5xszd",
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
# }

# CSV_FILENAME = "Frozen_Foods_Full_Data.csv"
# NUM_PRODUCTS_TO_FETCH = None 

# # ---------- CORE FUNCTIONS ----------

# def fetch_plp_page(offset):
#     # Menggunakan session curl_cffi dengan impersonate browser Chrome
#     proxy = random.choice(PROXIES_LIST)
    
#     url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
#     params = {
#         "category": "5xszd",
#         "count": "24",
#         "default_purchasability_filter": "false",
#         "include_sponsored": "true",
#         "include_review_summarization": "true",
#         "offset": str(offset),
#         "page": "/c/5xszd",
#         "platform": "desktop",
#         "pricing_store_id": "3991",
#         "visitor_id": "019A62A8EEE8020199CEE3E689734F84",
#         "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
#         "channel": "WEB",
#         "field_groups": "main,request_meta"
#     }

#     # impersonate="chrome110" akan meniru fingerprint TLS Chrome asli
#     r = requests.get(
#         url, 
#         params=params, 
#         headers=HEADERS, 
#         proxy=proxy, 
#         impersonate="chrome110", 
#         timeout=30
#     )
    
#     if r.status_code != 200:
#         print(f"DEBUG: Status {r.status_code} pada offset {offset}")
#         r.raise_for_status()
#     return r.json()

# def get_pdp_detail(tcin):
#     proxy = random.choice(PROXIES_LIST)
#     url = f"https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?tcin={tcin}&is_bot=false&pricing_store_id=3991&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
    
#     r = requests.get(url, headers=HEADERS, proxy=proxy, impersonate="chrome110", timeout=30)
#     return r.json()

# # ... (Fungsi extract_nutrients & parse_item_data tetap sama seperti sebelumnya) ...
# # (Saya ringkas untuk efisiensi pesan, gunakan fungsi parsing dari kode sebelumnya)

# def extract_nutrients(nutrition_node):
#     # (Gunakan logika extract_nutrients dari kode Komandan sebelumnya)
#     return {} # Placeholder

# def parse_item_data(node, path, is_variant="No"):
#     # (Gunakan logika parse_item_data dari kode Komandan sebelumnya)
#     return {"Title": "Contoh"} # Placeholder

# # ---------- MAIN LOOP ----------

# print("Mulai Scraping dengan TLS Bypass (curl_cffi)...")
# total_results = 1757 
# PER_PAGE = 24
# total_pages = (total_results + PER_PAGE - 1) // PER_PAGE

# global_counter = 0
# file_exists = os.path.isfile(CSV_FILENAME)

# for page_no in range(total_pages):
#     offset = page_no * PER_PAGE
#     print(f"\n>>> HALAMAN {page_no + 1}/{total_pages} (Offset: {offset})")

#     try:
#         plp_json = fetch_plp_page(offset)
#         products = plp_json.get("data", {}).get("search", {}).get("products", [])
#         if not products:
#             print("Peringatan: Tidak ada produk ditemukan di halaman ini.")
#             continue
            
#         for p in products:
#             # Ambil TCIN dan jalankan PDP detail seperti biasa...
#             # (Gunakan loop produk dari kode sebelumnya)
#             pass

#     except Exception as e:
#         print(f"Gagal di halaman {page_no}: {e}")
#         time.sleep(5)
#         continue

# print("Proses selesai.")

import requests
import re
import json
import time
import random
import csv
import html
from urllib.parse import quote_plus

# ---------- KONFIGURASI ----------
PROXIES = [
    {"server": "http://89.249.194.231:6630", "username": "arssrhsq", "password": "x1vpi09f4v1g"}
]

# Ambil User-Agent terbaru agar tidak dianggap bot lama
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.target.com/",
    "Origin": "https://www.target.com",
}

TARGET_NUTRIENTS = [
    "Calories","Total Fat","Saturated Fat","Trans Fat","Cholesterol","Sodium",
    "Total Carbohydrate","Dietary Fiber","Sugars","Added Sugars","Protein",
    "Vitamin A", "Vitamin C", "Vitamin D","Calcium","Iron","Potassium"
]

CSV_FILENAME = "Target_Frozen_Foods_Full.csv"
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96" # Jika 404, ganti key ini
STORE_ID = "1874"

# ---------- FUNGSI HELPER ----------

def get_session():
    s = requests.Session()
    p = PROXIES[0]
    user_enc = quote_plus(p["username"])
    pwd_enc = quote_plus(p["password"])
    proxy_url = p["server"].replace("http://", f"http://{user_enc}:{pwd_enc}@")
    s.proxies = {"http": proxy_url, "https": proxy_url}
    s.headers.update(HEADERS)
    return s

def extract_nutrients(nutrition_node):
    nut_dict = {"Serving Size": "", "Serving Size Unit": "", "Servings Per Container": ""}
    for name in TARGET_NUTRIENTS:
        nut_dict[f"{name} quantity"] = ""
        nut_dict[f"{name} unit"] = ""
        nut_dict[f"{name} percentage"] = ""
    
    prepared_list = nutrition_node.get("value_prepared_list", [])
    if prepared_list:
        p_node = prepared_list[0]
        nut_dict["Serving Size"] = p_node.get("serving_size", "")
        nut_dict["Serving Size Unit"] = p_node.get("serving_size_unit_of_measurement", "")
        nut_dict["Servings Per Container"] = p_node.get("servings_per_container", "")

        for n in p_node.get("nutrients", []):
            name = n.get("name")
            if name in TARGET_NUTRIENTS:
                try:
                    qty = n.get("quantity")
                    nut_dict[f"{name} quantity"] = f"{float(qty):g}" if qty else ""
                    nut_dict[f"{name} unit"] = n.get("unit_of_measurement", "")
                    pct = n.get("percentage")
                    nut_dict[f"{name} percentage"] = f"{float(pct):g}%" if pct else ""
                except: pass
    return nut_dict

def parse_item(node, bc_path, is_variant="No"):
    item = node.get("item", {})
    enrichment = item.get("enrichment", {})
    desc = item.get("product_description", {})
    
    # Rating extraction
    stats = node.get("ratings_and_reviews", {}).get("statistics", {}).get("rating", {})
    
    base_data = {
        "Title": html.unescape(desc.get("title", "")),
        "TCIN": node.get("tcin"),
        "UPC": f"'{item.get('primary_barcode', '')}",
        "DPCI": item.get("dpci"),
        "Brand": item.get("primary_brand", {}).get("name"),
        "Rating": stats.get("average", ""),
        "Review Count": stats.get("count", ""),
        "Ingredients": enrichment.get("nutrition_facts", {}).get("ingredients"),
        "Price": node.get("price", {}).get("formatted_current_price"),
        "Link": enrichment.get("buy_url"),
        "Breadcrumbs": bc_path,
        "Is Variant": is_variant
    }
    
    nut_data = extract_nutrients(enrichment.get("nutrition_facts", {}))
    return {**base_data, **nut_data}

# ---------- MAIN RUNNER ----------

def run_scraper():
    session = get_session()
    processed_tcins = set()
    is_first_write = True
    
    # 1. Dapatkan Total Results
    init_url = f"https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?category=5xszd&count=24&offset=0&pricing_store_id={STORE_ID}&key={API_KEY}&channel=WEB"
    
    try:
        resp = session.get(init_url, timeout=15)
        resp.raise_for_status()
        total_results = resp.json()["data"]["search"]["total_results"]
        print(f"Ditemukan total {total_results} produk.")
    except Exception as e:
        print(f"Gagal inisialisasi: {e}")
        return

    # 2. Loop per halaman (offset 24)
    for offset in range(0, total_results, 24):
        print(f"\n--- Scraping Offset: {offset} ---")
        plp_url = f"https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?category=5xszd&count=24&offset={offset}&pricing_store_id={STORE_ID}&key={API_KEY}&channel=WEB"
        
        try:
            r = session.get(plp_url, timeout=15)
            if r.status_code != 200:
                print(f"Error {r.status_code} pada offset {offset}. Melewati...")
                continue
                
            products = r.json().get("data", {}).get("search", {}).get("products", [])
            
            for p in products:
                tcin = p.get("tcin")
                if not tcin or tcin in processed_tcins: continue
                
                # Buka Detail Produk (PDP)
                pdp_url = f"https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?tcin={tcin}&is_bot=false&pricing_store_id={STORE_ID}&key={API_KEY}"
                
                try:
                    time.sleep(random.uniform(0.5, 1.2)) # Jeda agar tidak diblokir
                    rd = session.get(pdp_url, timeout=15)
                    product_data = rd.json().get("data", {}).get("product", {})
                    
                    if not product_data: continue
                    
                    # Breadcrumbs
                    bc = " > ".join([b.get("name") for b in product_data.get("category", {}).get("breadcrumbs", [])])
                    
                    # Parse Parent
                    row = parse_item(product_data, bc, "No")
                    
                    # Simpan Langsung ke CSV
                    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=row.keys())
                        if is_first_write:
                            writer.writeheader()
                            is_first_write = False
                        writer.writerow(row)
                    
                    processed_tcins.add(tcin)
                    print(f"Berhasil simpan: {tcin} ({len(processed_tcins)} data)")
                    
                    # Cek Children (Varian)
                    children = product_data.get("children", [])
                    for child in children:
                        child_row = parse_item(child, bc, "Yes")
                        with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=child_row.keys())
                            writer.writerow(child_row)

                except Exception as e:
                    print(f"Gagal mengambil detail {tcin}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error pada halaman offset {offset}: {e}")
            time.sleep(5) # Istirahat jika error koneksi

    print(f"\nSelesai! Total data unik: {len(processed_tcins)}")

if __name__ == "__main__":
    run_scraper()