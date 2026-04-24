import requests
import re
import json
import time
from urllib.parse import urlparse, quote_plus
import random
import csv
import html 

# ---------- KONFIG ----------
# Tambahkan daftar proxy Anda di sini
PROXIES_LIST = [
    "191.96.254.80:6127:arssrhsq:x1vpi09f4v1g",
    "45.61.122.149:6441:arssrhsq:x1vpi09f4v1g",
    "45.61.124.153:6482:arssrhsq:x1vpi09f4v1g",
    "64.64.110.63:6586:arssrhsq:x1vpi09f4v1g",
    "145.223.58.21:6290:arssrhsq:x1vpi09f4v1g"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.target.com/",
    "Origin": "https://www.target.com",
}

TARGET_NUTRIENTS = [
    "Calories","Total Fat","Saturated Fat","Trans Fat","Cholesterol","Sodium","Total Carbohydrate","Dietary Fiber","Sugars","Added Sugars","Protein","Vitamin A", "Vitamin C", "Vitamin D","Calcium","Iron","Potassium"
]


REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_REQUESTS = 2.2 # Jeda agar tidak cepat kena blokir
STORE_ID = '2250'
INPUT_FILE = "Frozen Single Serve Meals.csv"
OUTPUT_FILE = "detail-Frozen Single Serve Meals.csv"

# ---------- UTIL ----------
def get_random_requests_proxy():
    """Mengambil proxy acak dan memformatnya untuk library requests."""
    proxy_str = random.choice(PROXIES_LIST)
    ip, port, user, pw = proxy_str.split(':')
    proxy_url = f"http://{user}:{pw}@{ip}:{port}"
    return {"http": proxy_url, "https": proxy_url}


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


# ---------- MAIN EXECUTION ----------




def main():
    products_data = []
    
    # 1. Baca TCIN dari CSV
    tcin_list = []
    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('tcin'):
                    tcin_list.append(row['tcin'])
    except FileNotFoundError:
        print(f"❌ File {INPUT_FILE} tidak ditemukan!")
        return

    print(f"🚀 Memproses {len(tcin_list)} TCIN...")

    session = requests.Session()
    session.headers.update(HEADERS)

    for i, tcin in enumerate(tcin_list):
        # 2. Rotasi Proxy setiap request agar stabil
        current_proxy = get_random_requests_proxy()
        session.proxies.update(current_proxy)
        
        detail_url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
            f"?tcin={tcin}&is_bot=false&pricing_store_id={STORE_ID}&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
        )

        try:
            print(f"[{i+1}/{len(tcin_list)}] Memproses TCIN: {tcin}")
            response = session.get(detail_url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 403:
                print("⚠️ Terdeteksi bot (403). Mengganti proxy...")
                continue
                
            response.raise_for_status()
            data = response.json()
            
            product_node = data.get("data", {}).get("product")
            if not product_node:
                continue

            # Ekstrak Breadcrumbs
            breadcrumbs = product_node.get("category", {}).get("breadcrumbs", [])
            breadcrumb_path = " > ".join([bc.get("name", "").title() for bc in breadcrumbs])

            # Ambil Rating & Parent Info
            p_rating, p_count = get_rating_data(product_node)
            
            # Simpan Parent
            parent_info = parse_item_data(product_node, breadcrumb_path, "No", p_rating, p_count)
            products_data.append(parent_info)

            # Simpan Variants (jika ada)
            children = product_node.get("children", [])
            for child in children:
                child_info = parse_item_data(child, breadcrumb_path, "Yes", p_rating, p_count)
                products_data.append(child_info)

            # Jeda untuk menghindari blokir
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        except Exception as e:
            print(f"❌ Gagal memproses {tcin}: {e}")
            continue

    # 3. Simpan Hasil ke CSV
    if products_data:
        keys = products_data[0].keys()
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(products_data)
        print(f"✅ Selesai! Data disimpan di {OUTPUT_FILE}")

if __name__ == "__main__":
    main()