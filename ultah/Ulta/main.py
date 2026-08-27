import requests
import json
import time
import csv # <--- IMPORT BARU UNTUK CSV
from search_url import get_all_urls
from queri import cari
import re
from datetime import datetime, timezone

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
    "retailer", "product_group_id", "brand", "product_name","variant", "shade_description", "size", "product_url", "skuId", "category", "ingredients_raw" ,"image_url" ,"description", "details", "how_to_usage", "price","sale_price", "rating", "review_count", "scraped_at"
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


def get_size_for_sku(data, sku_id):
    """
    Cari Size berdasarkan skuId yang sedang diproses.
    Tidak mengambil size dari variant/SKU lain.
    """

    def search(d):
        if isinstance(d, dict):

            # Pastikan kita berada pada block variant
            if "variants" in d and isinstance(d["variants"], list):

                # Cek apakah block ini memang Size
                is_size_block = (
                    d.get("variantType") == "Size"
                    or d.get("typeLabel") == "Size"
                    or d.get("dimensionsLabel") == "Size"
                )


                if is_size_block:
                    for variant in d["variants"]:
                        if str(variant.get("skuId")) == str(sku_id):
                            name = variant.get("name")

                            if name and str(name).strip():
                                return str(name).strip()

                    dimensions_value = d.get("dimensionsValue")

                    if dimensions_value and str(dimensions_value).strip():
                        return str(dimensions_value).strip()


                    # 2. Kalau dimensionsValue kosong,
                    #    ambil name dari variant SKU yang sama
                    for variant in d["variants"]:
                        if str(variant.get("skuId")) == str(sku_id):
                            name = variant.get("name")

                            if name and str(name).strip():
                                return str(name).strip()

            # lanjut cari ke dalam JSON
            for value in d.values():
                result = search(value)
                if result:
                    return result

        elif isinstance(d, list):
            for item in d:
                result = search(item)
                if result:
                    return result

        return None

    return search(data)



def find_first_message_in_modules(data):
    """
    Mencari message pertama yang berada di dalam key 'modules'.
    Tidak peduli module-nya memiliki type apa.
    """

    def search_modules(obj):
        if isinstance(obj, dict):

            # Jika menemukan key "modules"
            if "modules" in obj and isinstance(obj["modules"], list):
                modules = obj["modules"]

                # Cari message pertama di dalam modules
                for module in modules:
                    message = search_message(module)

                    if message:
                        return message

                # Jika belum ditemukan, lanjut cari modules
                # yang lebih dalam
                for module in modules:
                    result = search_modules(module)

                    if result:
                        return result

            # Cari modules di key lain
            for value in obj.values():
                result = search_modules(value)

                if result:
                    return result

        elif isinstance(obj, list):
            for item in obj:
                result = search_modules(item)

                if result:
                    return result

        return None


    def search_message(obj):
        if isinstance(obj, dict):

            # PRIORITAS: message pertama
            if "message" in obj:
                value = obj["message"]

                if isinstance(value, str) and value.strip():
                    return value.strip()

            for value in obj.values():
                result = search_message(value)

                if result:
                    return result

        elif isinstance(obj, list):
            for item in obj:
                result = search_message(item)

                if result:
                    return result

        return None

    return search_modules(data)


def extract_details_for_sku(data, sku_id):
    """
    Mengambil isi Details yang benar-benar milik SKU tertentu.

    Target:
        #### Benefits
        ...
        #### Features
        ...
        Item 2503388

    Hanya mengembalikan block yang mengandung
    Item <sku_id>.
    """

    sku_id = str(sku_id)

    candidates = []

    def search(obj):
        if isinstance(obj, dict):

            # Cari semua string dalam object
            for key, value in obj.items():

                if isinstance(value, str):
                    text = value.strip()

                    if (
                        f"Item {sku_id}" in text
                        or f"Item {sku_id}<" in text
                        or f"Item {sku_id} " in text
                    ):
                        candidates.append(text)

                elif isinstance(value, (dict, list)):
                    search(value)

        elif isinstance(obj, list):
            for item in obj:
                search(item)

    search(data)

    if not candidates:
        return None

    # Pilih candidate yang paling panjang.
    # Biasanya ini adalah full Details block.
    details = max(candidates, key=len)

    return details.strip()


def scrape_ulta_product(product_url):
    # Fetch MAIN JSON (global)
    main_data = fetch_graphql(product_url)
    
    # with open("2634398.json", "a", encoding="utf-8") as f:
    #     json.dump(main_data, f, ensure_ascii=False, indent=2)
    #     f.write("\n")
        
    if not main_data:
        return []

    # ============ Extract all SKU IDs ============
    variant_lists = find_key(main_data, "variants")
    # print(f"Variant Lists Found: {variant_lists}")  # Debugging line


    skus = []
    for lst in variant_lists:
        if isinstance(lst, list):
            for item in lst:
                if item.get("skuId"):
                    skus.append({
                        "product_group_id": item.get("productId"),
                        "skuId": item.get("skuId"),
                        "variant": item.get("name"),
                        "shade_description": item.get("shadeDescription"),
                        "product_url": item.get("linkSelectAction", {}).get("url")
                    })

    # ============ Extract Global Details ============

    summary = find_first_message_in_modules(main_data)
    
    pd = extract_product_detail(main_data)
    global_description = pd.get("description") if pd else None
    # print(f"Global Description: {global_description}")  # Debugging line
    

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
    # print(f"Category Values Found: {cat_vals}")


    def get_category(cat_vals):
        if not cat_vals:
            return None

        categories = []

        for item in cat_vals:
            if isinstance(item, list):
                item = item[0] if item else None

            if isinstance(item, str) and item.strip():
                categories.append(item.strip())

        if not categories:
            return None

        # Pilih hierarchy yang paling lengkap
        category = max(categories, key=lambda x: len(x.split(":")))

        # Convert:
        # makeup:face:setting spray & powder
        # ->
        # Makeup > Face > Setting Spray & Powder
        parts = [
            part.strip().title()
            for part in category.split(":")
            if part.strip()
        ]

        return " > ".join(parts)


    category = get_category(cat_vals)

    # print(f"Category: {category}")


    # ============ Fetch PER SKU JSON ============
    final = []

    product_base_url = product_url.split("?")[0]

    scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for item in skus:
        sku = item["skuId"]

        size_ = get_size_for_sku(main_data, sku)

        # ===========================
        # Fetch SKU JSON (per-variant)
        # ===========================
        # sku_json = fetch_graphql(f"{product_base_url}?sku={sku}")
        
        
        # if not sku_json:
        #      time.sleep(0.4)
        #      continue


        # ===========================
        # Fetch SKU JSON
        # ===========================
        sku_json = fetch_graphql(f"{product_base_url}?sku={sku}")

        if not sku_json:
            time.sleep(0.4)
            continue


        # ===========================
        # Extract SKU Details
        # ===========================
        sku_details = extract_details_for_sku(
            sku_json,
            sku
        )

        # print(f"\nSKU: {sku}")
        # print(f"Details ditemukan: {bool(sku_details)}")

        if sku_details:
            print(f"Details Item: Item {sku}")

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
            "retailer": "Ulta",
            "product_name": product_name,
            "price": sku_list_price,
            "sale_price": sku_list_price,
            "description": summary if isinstance(summary, str) else None,

            # PENTING:
            "details": sku_details,

            "how_to_usage": sku_usage,
            "ingredients_raw": sku_ingredients,
            "brand": brand_name,
            "size": size_,
            "rating": f"'{rating}" if rating is not None else None,
            "review_count": review_count,
            "category": category,
            "image_url": image_url,
            "scraped_at": scraped_at,
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


# # # ======================================================================
# # # Untuk menguji satu produk saja (Hapus tanda pagar untuk mengaktifkan)
# # # ======================================================================
# if __name__ == "__main__":
#     TEST_PRODUCT_URL = "https://www.ulta.com/p/hydrating-facial-cleanser-xlsImpprod4190255?sku=2634398"
#     # TEST_PRODUCT_URL = "https://www.ulta.com/p/hydrating-glow-mist-setting-spray-spf-50-pimprod2046014?sku=2629771"
#     # TEST_PRODUCT_URL = "https://www.ulta.com/p/mini-macximal-silky-matte-lipstick-pimprod2045123?sku=2624227"
#     # TEST_PRODUCT_URL = "https://www.ulta.com/p/sun-cover-mineral-sunscreen-spf-30-pimprod2057101?sku=2651683"
#     # TEST_PRODUCT_URL = "https://www.ulta.com/p/urban-environment-oil-control-sunscreen-spf-40-pimprod2030941?sku=2592486"
#     results_for_one_product = scrape_ulta_product(TEST_PRODUCT_URL)
    
#     if results_for_one_product:
#         print(f"SKU ditemukan: {len(results_for_one_product)}")
#         print(json.dumps(results_for_one_product[0], indent=2)) # Cetak SKU pertama saja
#     else:
#         print("Gagal mendapatkan data.")