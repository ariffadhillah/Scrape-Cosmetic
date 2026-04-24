import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# =========================
# FUNGSI EKSTRAKSI
# =========================
def get_product_data(initial_config):
    """Mengambil list data produk dari config JSON"""
    product_list = []
    base_url = "https://www.nordstrom.com"
    
    product_results = initial_config.get("productResults", {})
    products = product_results.get("productsById", {})

    for product_id, info in products.items():
        path = info.get("productPageUrl")
        if path:
            product_list.append({
                "id": product_id,
                "name": info.get("name", "No Name"),
                "brand": info.get("brandName", "Unknown"),
                "url": base_url + path
            })
    return product_list

# =========================
# SETUP BROWSER
# =========================
options = webdriver.ChromeOptions()
# options.add_argument("--headless") # Aktifkan jika ingin jalan di background
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

# =========================
# PROSES SCRAPING PAGINATION
# =========================
all_extracted_products = []
TOTAL_PAGES = 9 # Jumlah halaman yang ingin diambil

try:
    for page in range(1, TOTAL_PAGES + 1):
        # Membuat URL dinamis berdasarkan nomor halaman
        if page == 1:
            url = "https://www.nordstrom.com/browse/beauty/hair/treatments"
        else:
            # Pola: offset biasanya bertambah (page-1 * jumlah_produk_per_hal)
            # Namun menggunakan parameter page=X saja biasanya sudah cukup kuat
            offset = (page - 1)# Contoh asumsi 24 produk per hal, sesuaikan jika perlu
            url = f"https://www.nordstrom.com/browse/beauty/hair/treatments?offset={offset}&page={page}&postalCodeAvailability=22153"
    # https://www.nordstrom.com/browse/beauty/fragrance/perfume?offset=9&page=2
        print(f"\n🚀 Memproses Halaman {page}...")
        print(f"🔗 URL: {url}")
        
        driver.get(url)
        time.sleep(10) # Tunggu loading

        # Ekstrak JSON
        config = driver.execute_script("return window.__INITIAL_CONFIG__ || null;")
        
        if config:
            products = get_product_data(config)
            if products:
                print(f"✅ Berhasil mengambil {len(products)} produk dari hal {page}")
                all_extracted_products.extend(products)
            else:
                print(f"⚠️ Halaman {page} kosong atau tidak ada produk.")
        else:
            print(f"❌ Gagal mendapatkan config di halaman {page}")

    # =========================
    # SIMPAN KE CSV
    # =========================
    if all_extracted_products:
        keys = all_extracted_products[0].keys()
        with open('Hair-Scalp-Treatments.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_extracted_products)

        print(f"\n✨ SELESAI! Total {len(all_extracted_products)} produk disimpan ke 'Hair-Scalp-Treatments.csv'")

finally:
    driver.quit()