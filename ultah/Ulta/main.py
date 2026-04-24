import requests
import json
import time
import csv # <--- IMPORT BARU UNTUK CSV
from search_url import get_all_urls
from queri import cari

BASE_GRAPHQL = "https://www.ulta.com/dxl/graphql"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "x-ulta-dxl-query-id": "Page",
    "x-ulta-client-locale": "en-US",
    "x-ulta-client-country": "US",
    "x-ulta-client-channel": "web",
    "x_ulta_site": "CA",
}

QUERY = """
query Page($url: JSON, $moduleParams: JSON) {
  Page(url: $url, moduleParams: $moduleParams) {
    content
    customResponseAttributes
    meta
    __typename
  }
}
"""

# Header kolom yang akan digunakan di file CSV
CSV_HEADERS = [
    "Product ID", "skuId", "Product Name", "Product Name Variant","shadeDescription", "Product Brand", "Category", "Ingredients", "description", "usage", "Product Url", "Product Image URL", "listPrice", "salePrice", "Rating", "Review Count",
]


def fetch_graphql(url_path):
    payload = {
        "operationName": "Page",
        "query": QUERY,
        "variables": {"url": {"path": url_path}, "moduleParams": {}}
    }
    
    try:
        r = requests.post(BASE_GRAPHQL, headers=HEADERS, json=payload, timeout=20) 
        r.raise_for_status() 
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"\n[❌ ERROR] Gagal mengambil data untuk path: {url_path}")
        return {} 


def extract_product_detail(data):
    """Find ProductDetail block."""
    def search(x):
        if isinstance(x, dict):
            if x.get("type") == "ProductDetail":
                return x
            for v in x.values():
                found = search(v)
                if found:
                    return found
        elif isinstance(x, list):
            for item in x:
                found = search(item)
                if found:
                    return found
        return None
    return search(data)


def find_key(data, target_key):
    """Mencari semua nilai dari kunci tertentu secara rekursif."""
    results = []
    def search(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k.lower() == target_key.lower():
                    results.append(v)
                search(v)
        elif isinstance(d, list):
            for v in d:
                search(v)
    search(data)
    return results


def scrape_ulta_product(product_url):
    # Fetch MAIN JSON (global)
    main_data = fetch_graphql(product_url)
    
    if not main_data:
        return []

    # ============ Extract all SKU IDs ============
    variant_lists = find_key(main_data, "variants")
    skus = []
    for lst in variant_lists:
        if isinstance(lst, list):
            for item in lst:
                if item.get("skuId"):
                    skus.append({
                        "Product ID": item.get("productId"),
                        "skuId": item.get("skuId"),
                        "Product Name Variant": item.get("name"),
                        "shadeDescription": item.get("shadeDescription"),
                        "Product Url": item.get("linkSelectAction", {}).get("url")
                    })

    # ============ Extract Global Details ============
    pd = extract_product_detail(main_data)
    global_description = pd.get("description") if pd else None
    global_usage = pd.get("usage") if pd else None
    global_ingredients = pd.get("ingredients") if pd else None

    brand_vals = find_key(main_data, "brandName")
    brand_name = brand_vals[0] if brand_vals else None

    rating_vals = find_key(main_data, "product_rating")
    rating = rating_vals[0] if rating_vals else None

    review_vals = find_key(main_data, "product_reviews_count")
    review_count = review_vals[0] if review_vals else None

    name_vals = find_key(main_data, "productName")
    product_name = name_vals[0] if name_vals else None

    cat_vals = find_key(main_data, "product_category")
    def get_last(cat):
        if isinstance(cat, list): cat = cat[0]
        if isinstance(cat, str): return cat.split(":")[-1].strip()
        return None
    category = get_last(cat_vals[0]) if cat_vals else None

    # ============ Fetch PER SKU JSON ============
    final = []

    product_base_url = product_url.split("?")[0]

    for item in skus:
        sku = item["skuId"]

        # ===========================
        # Fetch SKU JSON (per-variant)
        # ===========================
        sku_json = fetch_graphql(f"{product_base_url}?sku={sku}")
        
        if not sku_json:
             time.sleep(0.4)
             continue

        # ============= Extract price, description, usage, ingredients from SKU JSON =============
        sku_list_price = None
        sku_sale_price = None
        sku_description = None
        sku_usage = None
        sku_ingredients = None

        def search_all(d):
            nonlocal sku_list_price, sku_sale_price
            nonlocal sku_description, sku_usage, sku_ingredients

            if isinstance(d, dict):
                # --- PRICES ---
                if "listPrice" in d:
                    sku_list_price = d["listPrice"]
                if "salePrice" in d:
                    sku_sale_price = d["salePrice"]

                # --- DESCRIPTION BLOCKS (sometimes included per SKU) ---
                if "description" in d and isinstance(d["description"], str):
                    sku_description = d["description"]
                if "usage" in d and isinstance(d["usage"], str):
                    sku_usage = d["usage"]
                if "ingredients" in d and isinstance(d["ingredients"], str):
                    sku_ingredients = d["ingredients"]

                for v in d.values():
                    search_all(v)

            elif isinstance(d, list):
                for v in d:
                    search_all(v)

        search_all(sku_json)

        # Fallback ke global
        if not sku_description: sku_description = global_description
        if not sku_usage: sku_usage = global_usage
        if not sku_ingredients: sku_ingredients = global_ingredients

        # Image
        image_url = f"https://media.ulta.com/i/ulta/{sku}?w=1080&h=1080&fmt=auto"

        final.append({
            **item,
            "Product Name": product_name,
            "listPrice": sku_list_price,
            "salePrice": sku_sale_price,
            # Pastikan nilai string tunggal untuk CSV
            "description": sku_description, 
            "usage": sku_usage,
            "Ingredients": sku_ingredients,
            "Product Brand": brand_name,
            "Rating": rating,
            "Review Count": review_count,
            "Category": category,
            "Product Image URL": image_url
        })

        time.sleep(0.4) # Jeda per SKU

    return final


# ======================
# RUN (Menjalankan Scraping Penuh dan Menyimpan ke CSV)
# ======================
if __name__ == "__main__":
    
    # Dapatkan daftar semua URL produk
    all_product_urls = get_all_urls()
    all_results = [] # Untuk menyimpan semua hasil dari semua produk

    SEARCH_TERM = cari()
    SAFE_SEARCH_TERM = SEARCH_TERM.replace('/', '-')
    OUTPUT_FILE = f"ulta_products-{SAFE_SEARCH_TERM}.csv" # Nama file output
    
    # Mode 'w' (write) untuk membuat file baru, newline='' penting untuk CSV di Windows
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        
        # Inisialisasi CSV writer
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        writer.writeheader() # Tulis baris header
        print(f"\n[✅ CSV] File '{OUTPUT_FILE}' telah dibuat dan header telah ditulis.")

        # Loop melalui setiap URL produk yang didapat
        for i, product_url in enumerate(all_product_urls):
            print(f"\n--- MEMPROSES PRODUK {i+1}/{len(all_product_urls)}: {product_url} ---")
            
            # Panggil fungsi scraping untuk SATU URL produk
            results_for_one_product = scrape_ulta_product(product_url)
            
            # Tulis hasil ke CSV
            if results_for_one_product:
                writer.writerows(results_for_one_product)
                all_results.extend(results_for_one_product)
                
                print(f"[✅ SUKSES] Berhasil mendapatkan dan MENYIMPAN {len(results_for_one_product)} SKU.")
            else:
                print("[⚠️ PERINGATAN] Gagal mendapatkan detail produk (SKU) atau tidak ada SKU ditemukan.")

            # Jeda kecil setelah memproses satu produk untuk menghindari blocking
            time.sleep(.5) 

    # Contoh cara mencetak total data yang berhasil dikumpulkan
    print(f"\n========================================================")
    print(f"SCRAPING SELESAI!")
    print(f"Total URL Produk Diproses: {len(all_product_urls)}")
    print(f"Total SKU yang Berhasil Disimpan: {len(all_results)}")
    print(f"Data disimpan ke file: {OUTPUT_FILE}")
    print(f"========================================================")


# ======================================================================
# Untuk menguji satu produk saja (Hapus tanda pagar untuk mengaktifkan)
# ======================================================================
# if __name__ == "__main__":
#     TEST_PRODUCT_URL = "https://www.ulta.com/p/mini-macximal-silky-matte-lipstick-pimprod2045123?sku=2624227"
#     results_for_one_product = scrape_ulta_product(TEST_PRODUCT_URL)
    
#     if results_for_one_product:
#         print(f"SKU ditemukan: {len(results_for_one_product)}")
#         print(json.dumps(results_for_one_product[0], indent=2)) # Cetak SKU pertama saja
#     else:
#         print("Gagal mendapatkan data.")