import os
import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# =========================
# 2. PARSER DETAIL PRODUK
# =========================


def extract_skus_with_images(data, product_url):
    results = []

    # 1. Ambil Ingredients dan Price data dari root
    view_data = data.get("viewData", {})
    ingredients_text = view_data.get("ingredients", "No ingredients found")
    
    # Ambil seluruh objek price
    price_root = view_data.get("price", {})
    prices_by_sku = price_root.get("bySkuId", {})

    # Ambil Data Style dari sellingEssentials
    selling = data.get("sellingEssentials", {})
    styles_by_id = selling.get("stylesById", {})

    for style_id, style in styles_by_id.items():
        brand_info = style.get("brand", {})
        brand_name = brand_info.get("brandName", "No Brand")

        review_data = style.get("reviews", {})
        avg_rating = review_data.get("averageRating", 0)
        num_reviews = review_data.get("numberOfReviews", 0)

        media = style.get("mediaExperiences", {}) 
        carousels = media.get("carouselsByColor", [])
        
        color_image_map = {}
        for entry in carousels:
            color_name = entry.get("colorName", "").strip().upper()
            shots = entry.get("orderedShots", [])
            if shots:
                color_image_map[color_name] = shots[0].get("url")

        product_name = style.get("productName") or style.get("productTitle")
        skus_by_id = style.get("skus", {}).get("byId", {})

        for sku_id, sku in skus_by_id.items():
            color_val = sku.get("colorDisplayValue", "").strip().upper()
            image_url = color_image_map.get(color_val, "No Image Found")

            # --- AMBIL HARGA DARI bySkuId MENGGUNAKAN SKU_ID ---
            # Kita cari di objek prices_by_sku (Gunakan string karena key JSON adalah string)
            sku_price_info = prices_by_sku.get(str(sku_id), {})
            
            price_value = "N/A"
            if sku_price_info:
                # print("sku_price_info",sku_price_info)
                # Ambil tipe harga (REGULAR/CLEARANCE)
                p_type = sku_price_info.get("currentPriceType", "regular").lower()
                price_obj = sku_price_info.get(p_type) or sku_price_info.get("regular")
                
                if price_obj and "price" in price_obj:
                    # Ambil field 'units' (misal: 699)
                    price_value = price_obj["price"].get("units")

            results.append({
                "Product ID": style_id,
                "SKU ID": sku_id,
                "rmsSkuId": sku.get("rmsSkuId"),
                "Product Name": product_name,
                "Product Maker": brand_name,
                "Varian/color": sku.get("colorDisplayValue"),
                "size": sku.get("sizeDisplayValue"),
                "Product Url": product_url,  # <--- Menyimpan URL Produk
                "Major Category": "Makeup",
                "Category": "Face Makeup",
                "Ingredients": ingredients_text,
                "Product Image URL": image_url,
                "Price": price_value, # <--- Kolom Baru
                "Total Review Count":num_reviews,
                "Rating": f"'{avg_rating}",

            })

    return results




# def save_to_csv(sku_data, filename="Face-Makeup.csv"):
#     if not sku_data:
#         print("⚠️ No data to save.")
#         return

#     # Tentukan header berdasarkan key di dictionary
#     keys = sku_data[0].keys()
    
#     with open(filename, 'w', newline='', encoding='utf-8') as output_file:
#         dict_writer = csv.DictWriter(output_file, fieldnames=keys)
#         dict_writer.writeheader()
#         dict_writer.writerows(sku_data)
    
#     print(f"✅ Data successfully saved to {filename}")

# # =========================
# # SELENIUM + STEALTH SETUP
# # =========================
# options = webdriver.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--start-maximized")
# options.add_argument("--lang=en-US,en")
# options.add_argument("--headless") # Opsional: jalankan tanpa muncul jendela browser

# driver = webdriver.Chrome(
#     service=Service(ChromeDriverManager().install()),
#     options=options
# )

# stealth(
#     driver,
#     languages=["en-US", "en"],
#     vendor="Google Inc.",
#     platform="Win32",
#     webgl_vendor="Intel Inc.",
#     renderer="Intel Iris OpenGL Engine",
#     fix_hairline=True,
# )

# # =========================
# # TARGET PRODUCT URL
# # =========================
# PRODUCT_URL = "https://www.nordstrom.com/s/maison-francis-kurkdjian-paris-baccarat-rouge-540-extrait-de-parfum/5495553?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FFragrance&color=000"

# try:
#     print(f"🔄 Opening product page: {PRODUCT_URL}")
#     driver.get(PRODUCT_URL)
#     time.sleep(8) # Beri waktu untuk load __INITIAL_CONFIG__

#     # =========================
#     # EXTRACT __INITIAL_CONFIG__
#     # =========================
#     print("📦 Extracting __INITIAL_CONFIG__ ...")
#     initial_config = driver.execute_script("return window.__INITIAL_CONFIG__ || null;")

#     if not initial_config:
#         print("❌ __INITIAL_CONFIG__ NOT found")
#     else:
#         print("✅ __INITIAL_CONFIG__ found!")
        
#         # Jalankan parser
#         final_results = extract_skus_with_images(initial_config, PRODUCT_URL)
        
#         # Simpan ke CSV
#         save_to_csv(final_results)

# finally:
#     print("🚪 Closing browser...")
#     driver.quit()




# =========================
# 2. SELENIUM SETUP
# =========================

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--lang=en-US,en")
    # options.add_argument("--headless") # Aktifkan jika ingin tanpa jendela
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    stealth(driver, languages=["en-en", "us"], vendor="Google Inc.", platform="Win32",
            webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
    return driver

# =========================
# 3. MAIN PROCESS (LOOPING CSV)
# =========================

INPUT_FILENAME = "Eye-Makeup.csv"
OUTPUT_FILENAME = "Eye-Makeup-Detail-11.csv"

if not os.path.exists(INPUT_FILENAME):
    print(f"❌ File {INPUT_FILENAME} tidak ditemukan!")
    exit()

driver = get_driver()
all_final_results = []

try:
    # Membaca URL dari file CSV input
    with open(INPUT_FILENAME, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        urls = [row['url'] for row in reader if 'url' in row]

    print(f"📂 Ditemukan {len(urls)} URL untuk diproses.")

    for index, product_url in enumerate(urls, 1):
        try:
            print(f"\n🚀 [{index}/{len(urls)}] Mengolah: {product_url}")
            driver.get(product_url)
            time.sleep(7) # Tunggu load

            initial_config = driver.execute_script("return window.__INITIAL_CONFIG__ || null;")

            if not initial_config:
                print(f"⚠️ __INITIAL_CONFIG__ tidak ditemukan untuk URL ini.")
                break

            # Parse detail produk (bisa menghasilkan banyak SKU per 1 URL)
            sku_details = extract_skus_with_images(initial_config, product_url)
            
            if sku_details:
                all_final_results.extend(sku_details)
                print(f"✅ Berhasil mengambil {len(sku_details)} SKU.")
            
            # (Opsional) Simpan berkala setiap 5 URL agar data tidak hilang jika crash
            if index % 5 == 0:
                print("💾 Menyimpan progress sementara...")
                keys = all_final_results[0].keys()
                with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f_out:
                    writer = csv.DictWriter(f_out, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(all_final_results)

        except Exception as e:
            print(f"❌ Error pada URL {product_url}: {e}")
            continue

    # Simpan hasil akhir
    if all_final_results:
        keys = all_final_results[0].keys()
        with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_final_results)
        print(f"\n✨ SELESAI! Total {len(all_final_results)} SKU disimpan ke {OUTPUT_FILENAME}")

finally:
    print("🚪 Closing browser...")
    driver.quit()