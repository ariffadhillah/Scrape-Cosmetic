import os
import time
import json
import csv
import random
# import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# # =========================
# # 1. SETUP DRIVER
# # =========================
# def get_driver():
#     options = uc.ChromeOptions()
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--incognito")
#     options.add_argument("--disable-gpu")
    
#     # Sesuai versi Chrome 143 Anda
#     user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
#     options.add_argument(f'--user-agent={user_agent}')
    
#     try:
#         driver = uc.Chrome(options=options) 
#     except Exception as e:
#         print(f"⚠️ Gagal inisiasi otomatis, mencoba paksa ke versi utama 143: {e}")
#         driver = uc.Chrome(options=options, version_main=143)
        
#     return driver


# import os
# import time
# from selenium import webdriver
# from selenium.webdriver.edge.service import Service
# from selenium.webdriver.edge.options import Options
# from selenium_stealth import stealth
# from webdriver_manager.microsoft import EdgeChromiumDriverManager

# def get_driver():
#     options = Options()
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("-inprivate")
#     options.add_argument("--disable-gpu")
    
#     # Path manual ke file msedgedriver.exe yang anda download tadi
#     # Jika ditaruh di folder yang sama dengan script:
#     path_driver = os.path.join(os.getcwd(), "msedgedriver.exe")
#     service = Service(path_driver) 
    
#     driver = webdriver.Edge(service=service, options=options)

#     stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#     )
#     return driver


import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium_stealth import stealth

def get_driver():
    options = Options()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("-inprivate") 
    options.add_argument("--disable-gpu")
    
    # User Agent Edge
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    options.add_argument(f'--user-agent={user_agent}')
    
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Menunjuk langsung ke file msedgedriver.exe di folder yang sama
    current_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(current_dir, "msedgedriver.exe")
    
    # Pastikan file ada sebelum dijalankan
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"File msedgedriver.exe tidak ditemukan di {driver_path}")

    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    # Trik menipu selenium-stealth agar mengira ini Chrome
    driver.__class__ = webdriver.Chrome 

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    # Balikkan ke Edge
    driver.__class__ = webdriver.Edge
    
    return driver

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
                "Major Category": "Hair Care",
                "Category": "Hair & Scalp Treatments",
                "Ingredients": ingredients_text,
                "Product Image URL": image_url,
                "Price": price_value, # <--- Kolom Baru
                "Total Review Count":num_reviews,
                "Rating": f"'{avg_rating}",

            })

    return results




# def save_to_csv(data, filename):
#     if not data: return
#     keys = data[0].keys()
#     with open(filename, 'w', newline='', encoding='utf-8') as f_out:
#         writer = csv.DictWriter(f_out, fieldnames=keys)
#         writer.writeheader()
#         writer.writerows(data)

# # =========================
# # 3. MAIN PROCESS WITH RETRY LOGIC
# # =========================
# INPUT_FILENAME = "Eye-Makeup.csv"
# OUTPUT_FILENAME = "Eye-Makeup-Detail-Final-2.csv"

# driver = get_driver()
# all_final_results = []
# MAX_RETRIES = 6 # Maksimal percobaan per URL

# try:
#     print("🌐 Melakukan 'Warm-up' sesi...")
#     driver.get("https://www.nordstrom.com")
#     time.sleep(random.uniform(5, 8))

#     with open(INPUT_FILENAME, mode='r', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         urls = [row['url'] for row in reader if 'url' in row]

#     for index, product_url in enumerate(urls, 1):
#         success = False
#         print(f"\n🚀 [{index}/{len(urls)}] Mengolah: {product_url}")

#         for attempt in range(1, MAX_RETRIES + 1):
#             try:
#                 if attempt > 1:
#                     print(f"🔄 Percobaan ulang ke-{attempt} untuk URL ini...")
                
#                 driver.get(product_url)
                
#                 # Tunggu loading
#                 WebDriverWait(driver, 15).until(
#                     lambda d: d.execute_script("return document.readyState") == "complete"
#                 )
                
#                 # Anti-bot injection
#                 driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
#                 # Simulasi interaksi
#                 driver.execute_script(f"window.scrollTo(0, {random.randint(300, 600)});")
#                 time.sleep(random.uniform(3, 5))

#                 initial_config = driver.execute_script("return window.__INITIAL_CONFIG__ || null;")

#                 if initial_config:
#                     sku_details = extract_skus_with_images(initial_config, product_url)
#                     all_final_results.extend(sku_details)
#                     print(f"✅ Berhasil mengambil {len(sku_details)} SKU.")
#                     success = True
#                     break # Keluar dari loop retry jika sukses
#                 else:
#                     # Cek blokir Akamai
#                     page_source = driver.page_source.lower()
#                     if "access denied" in page_source:
#                         print(f"❌ Akses Ditolak (Attempt {attempt})")
#                         time.sleep(10) # Tunggu sebentar sebelum refresh/retry
#                     else:
#                         print(f"⚠️ __INITIAL_CONFIG__ tidak ditemukan (Attempt {attempt})")
                
#             except Exception as e:
#                 print(f"❌ Error pada percobaan {attempt}: {e}")
            
#             # Jika belum sukses, beri jeda sebelum retry berikutnya
#             time.sleep(random.uniform(5, 10))

#         if not success:
#             print(f"⏭️ Gagal setelah {MAX_RETRIES} kali percobaan. Melewati URL ini.")

#         # Cooling down setiap 5 produk
#         if index % 5 == 0:
#             save_to_csv(all_final_results, OUTPUT_FILENAME)
#             wait_long = random.uniform(15, 30)
#             print(f"😴 Jeda istirahat: {wait_long:.2f}s...")
#             time.sleep(wait_long)

# finally:
#     save_to_csv(all_final_results, OUTPUT_FILENAME)
#     print("\n✨ SELESAI! Driver ditutup.")
#     driver.quit()




def human_interaction(driver):
    """Simulasi interaksi manusia untuk memancing rendering halaman"""
    try:
        # 1. Scroll sedikit demi sedikit
        for _ in range(3):
            scroll_amt = random.randint(200, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amt});")
            time.sleep(random.uniform(1.5, 2.2))
            # time.sleep(random.uniform(10, 25))
        
        # 2. Klik pada area kosong (misal pinggir body) untuk memicu event listener
        actions = webdriver.ActionChains(driver)
        actions.move_by_offset(random.randint(10, 50), random.randint(10, 50)).click().perform()
        
        # 3. Kembali ke atas sedikit
        driver.execute_script("window.scrollBy(0, -200);")
        time.sleep(1)
    except Exception:
        pass

def save_to_csv(data, filename):
    if not data: return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


# =========================
# 3. MAIN PROCESS
# =========================
INPUT_FILENAME = "urls-Hair-Scalp-Treatments.csv"
OUTPUT_FILENAME = "Hair-Scalp-Treatments-detail.csv"

# Inisiasi driver (Pastikan msedgedriver.exe sudah ada di folder)
driver = get_driver()
all_final_results = []
MAX_RETRIES = 6 

try:
    print("🌐 Melakukan 'Warm-up' sesi...")
    driver.get("https://www.nordstrom.com")
    time.sleep(random.uniform(5, 8))
    # time.sleep(random.uniform(10, 25))

    with open(INPUT_FILENAME, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        urls = [row['url'] for row in reader if 'url' in row]

    for index, product_url in enumerate(urls, 1):
        success = False
        print(f"\n🚀 [{index}/{len(urls)}] Mengolah: {product_url}")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if attempt > 1:
                    print(f"🔄 Percobaan ulang ke-{attempt}...")
                
                driver.get(product_url)
                
                # Tunggu elemen utama produk muncul (misal judul produk)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # --- TAMBAHAN: INTERAKSI MANUSIA ---
                print("🖱️ Menyimulasikan interaksi manusia...")
                human_interaction(driver)
                # time.sleep(random.uniform(2, 4))
                time.sleep(random.uniform(3, 5))
                
                # Ambil data
                initial_config = driver.execute_script("return window.__INITIAL_CONFIG__ || null;")

                if initial_config:
                    sku_details = extract_skus_with_images(initial_config, product_url)
                    all_final_results.extend(sku_details)
                    print(f"✅ Berhasil mengambil {len(sku_details)} SKU.")
                    success = True
                    break 
                else:
                    # Cek blokir
                    if "access denied" in driver.page_source.lower():
                        print(f"❌ Akses Ditolak Akamai (Attempt {attempt})")
                        # Ganti User Agent secara halus jika memungkinkan atau tunggu lebih lama
                        time.sleep(20) 
                    else:
                        print(f"⚠️ __INITIAL_CONFIG__ kosong. Mencoba refresh/interaksi lagi...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(random.uniform(5, 10))
            # time.sleep(random.uniform(10, 25))

        if not success:
            print(f"⏭️ Melewati URL ini.")

        # Save berkala
        if index % 5 == 0:
            save_to_csv(all_final_results, OUTPUT_FILENAME)
            wait_long = random.uniform(20, 40)
            print(f"😴 Cooling down: {wait_long:.2f}s...")
            time.sleep(wait_long)

finally:
    save_to_csv(all_final_results, OUTPUT_FILENAME)
    print("\n✨ SELESAI!")
    driver.quit()