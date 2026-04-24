import json
import time
import random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

# =========================
# START BROWSER STEALTH
# =========================
def start_browser():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # PERBAIKAN: Tambahkan version_main agar sesuai dengan Chrome Anda (145)
    driver = uc.Chrome(options=options, version_main=145) 
    return driver


# =========================
# AMBIL URL PRODUK
# =========================
def ambil_semua_url_produk_kategori(driver, category_url):
    print(f"\n🔎 Memindai halaman kategori:")
    print(category_url)

    driver.get(category_url)
    time.sleep(random.uniform(5, 8))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_urls = set()

    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        print("❌ NEXT_DATA tidak ditemukan (Mungkin terblokir atau struktur berubah)")
        return []

    try:
        data = json.loads(script.string)
        # Struktur path Walmart kadang berubah, kita gunakan get() agar lebih aman
        item_results = data["props"]["pageProps"]["initialData"]["searchResult"].get("itemStacks", [])

        for stack in item_results:
            for item in stack.get("items", []):
                url = item.get("canonicalUrl")
                # Pastikan ini adalah URL produk (mengandung /ip/)
                if url and "/ip/" in url:
                    if not url.startswith("http"):
                        url = "https://www.walmart.com" + url
                    product_urls.add(url)

    except Exception as e:
        print("❌ Error parsing JSON:", e)

    print(f"✅ Total URL produk ditemukan: {len(product_urls)}")
    return list(product_urls)


# =========================
# MAIN
# =========================
save_file = "Url-Shellfish.csv"

if __name__ == "__main__":
    driver = start_browser()

    # PERBAIKAN: Cara menyusun URL yang benar untuk kategori
    # URL Asli: https://www.walmart.com/browse/food/packaged-meals-side-dishes/976759_976794_5614446
    BASE_URL = "https://www.walmart.com/browse/food/chai-tea/976759_976782_1001320_8658677"
    ADDITIONAL_PARAMS = "povid=976759_hubspoke_1001320_ShopByCategory_ChaiTea_Rweb_May_27"

    semua_produk = set()
    MAX_PAGES = 2  # Mulai dengan angka kecil dulu untuk testing

    print("🌐 Warmup homepage...")
    driver.get("https://www.walmart.com/")
    time.sleep(10)

    for page_num in range(1, MAX_PAGES + 1):
        # Struktur penggabungan URL yang benar untuk paginasi
        page_url = f"{BASE_URL}?{ADDITIONAL_PARAMS}&page={page_num}"
        time.sleep(10)

        print(f"\n🚀 MEMPROSES HALAMAN {page_num} DARI {MAX_PAGES}")
        urls = ambil_semua_url_produk_kategori(driver, page_url)

        if not urls:
            print(f"⚠️ Tidak ditemukan produk di halaman {page_num}. Berhenti...")
            break

        semua_produk.update(urls)
        print(f"⏳ Jeda keamanan... (Total terkumpul: {len(semua_produk)} URL)")
        time.sleep(random.uniform(10, 20))

    print(f"\n🏁 SELESAI! TOTAL PRODUK UNIK: {len(semua_produk)}")

    with open(save_file, "w", encoding="utf-8") as f:
        for url in semua_produk:
            f.write(url + "\n")

    print(f"💾 Semua URL disimpan ke '{save_file}'")
    driver.quit()



# import json
# import time
# import random
# import csv
# from playwright.sync_api import sync_playwright
# from playwright_stealth import stealth_sync

# def run():
#     # Gunakan nama folder baru agar benar-benar bersih
#     user_data_dir = "./walmart_emergency_reset"
    
#     with sync_playwright() as p:
#         browser_context = p.chromium.launch_persistent_context(
#             user_data_dir,
#             headless=False,
#             # Meniru browser asli Windows 10 dengan Chrome versi terbaru
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#             viewport={"width": 1280, "height": 720},
#             args=[
#                 "--disable-blink-features=AutomationControlled",
#                 "--start-maximized"
#             ]
#         )
        
#         page = browser_context.pages[0]
#         stealth_sync(page)

#         try:
#             # LANGKAH 1: Jangan langsung ke Walmart. Buka situs besar lain dulu.
#             print("🕒 Menunggu 5 detik sebelum mulai...")
#             time.sleep(5)
            
#             print("🌐 Mencoba masuk ke DuckDuckGo (Warmup)...")
#             page.goto("https://googlw.com/?q=walmart+crab", wait_until="networkidle")
#             time.sleep(random.uniform(3, 5))

#             # LANGKAH 2: Masuk ke Walmart Homepage dulu, jangan langsung kategori
#             print("🌐 Masuk ke Walmart Homepage...")
#             page.goto("https://www.walmart.com", wait_until="domcontentloaded", timeout=60000)
            
#             # Jika masih muncul "Sorry", stop di sini dan tunggu 1 jam.
#             if "technical issues" in page.content().lower():
#                 print("❌ IP kamu masih diblokir (Throttled).")
#                 print("Saran: Gunakan koneksi internet lain (Tethering HP) atau tunggu 1-2 jam.")
#             else:
#                 print("✅ Masuk Homepage Berhasil! Menuju kategori...")
#                 time.sleep(random.uniform(4, 7))
                
#                 url_kategori = "https://www.walmart.com/browse/food/crab-other-shellfish/976759_9569500_1001442_2756662"
#                 page.goto(url_kategori, wait_until="domcontentloaded")
                
#                 # --- Jeda untuk kamu scroll manual jika perlu ---
#                 print("🖱️ Silakan scroll halaman sebentar agar terlihat natural...")
#                 time.sleep(10)

#         finally:
#             print("\n🏁 Browser tetap terbuka selama 5 menit.")
#             print("Jika kamu berhasil masuk, biarkan saja sebentar agar cookie tersimpan.")
#             time.sleep(300)
#             browser_context.close()

# if __name__ == "__main__":
#     run()