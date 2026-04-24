
# import requests
# import time
# import json
# import random
# import re
# import csv  
# from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# # ... sisa kode Anda di bawah tetap sama ...

# # ---------- CONFIG PROXY TERBARU ----------
# # Menggunakan daftar proxy yang Anda berikan sebelumnya
# PROXIES_LIST = [
#     "191.96.254.80:6127:arssrhsq:x1vpi09f4v1g",
#     "45.61.122.149:6441:arssrhsq:x1vpi09f4v1g",
#     "45.61.124.153:6482:arssrhsq:x1vpi09f4v1g",
#     "64.64.110.63:6586:arssrhsq:x1vpi09f4v1g",
#     "145.223.58.21:6290:arssrhsq:x1vpi09f4v1g",
#     "82.23.206.96:5902:arssrhsq:x1vpi09f4v1g",
#     "38.154.233.46:5456:arssrhsq:x1vpi09f4v1g",
#     "45.61.118.128:5825:arssrhsq:x1vpi09f4v1g",
#     "191.96.202.229:6275:arssrhsq:x1vpi09f4v1g",
#     "23.27.196.145:6514:arssrhsq:x1vpi09f4v1g",
#     "154.6.126.37:6008:arssrhsq:x1vpi09f4v1g",
#     "89.249.195.211:6966:arssrhsq:x1vpi09f4v1g",
#     "147.124.198.69:5928:arssrhsq:x1vpi09f4v1g",
#     "82.24.238.65:6872:arssrhsq:x1vpi09f4v1g",
#     "38.154.217.34:7225:arssrhsq:x1vpi09f4v1g",
#     "174.140.200.142:6422:arssrhsq:x1vpi09f4v1g",
#     "46.202.224.238:5790:arssrhsq:x1vpi09f4v1g",
#     "31.57.87.145:5830:arssrhsq:x1vpi09f4v1g",
#     "38.154.233.181:5591:arssrhsq:x1vpi09f4v1g",
#     "198.46.241.143:6678:arssrhsq:x1vpi09f4v1g",
#     "23.27.203.134:6869:arssrhsq:x1vpi09f4v1g",
#     "104.168.118.219:6175:arssrhsq:x1vpi09f4v1g",
#     "152.232.14.43:7174:arssrhsq:x1vpi09f4v1g",
#     "82.26.238.68:6375:arssrhsq:x1vpi09f4v1g",
#     "89.249.194.231:6630:arssrhsq:x1vpi09f4v1g",
#     "104.232.211.0:5613:arssrhsq:x1vpi09f4v1g",
#     "38.154.217.123:7314:arssrhsq:x1vpi09f4v1g",
#     "67.227.14.204:6796:arssrhsq:x1vpi09f4v1g"
# ]

# def get_random_proxy_config():
#     """Mengambil proxy acak dan memformatnya untuk Playwright."""
#     proxy_str = random.choice(PROXIES_LIST)
#     ip, port, user, pw = proxy_str.split(':')
#     return {
#         "server": f"http://{ip}:{port}",
#         "username": user,
#         "password": pw
#     }


# # ---------- TARGET CONFIG ----------
# OUTPUT_FILE = "Frozen Single Serve Meals.csv"
# URL = "https://www.target.com/c/frozen-foods-grocery/-/N-5xszd"
# HEADLESS = False
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# ACCEPT_LANGS = "en-US,en;q=0.9"
# NAV_TIMEOUT_MS = 80000
# # ----------------------------

# INJECT_SCRIPT = """
# Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
# Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
# Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
# """

# # ---------- HELPERS ----------
# def auto_scroll_to_bottom(page, step=1000, max_wait=40):
#     """Scroll sampai tidak berubah lagi (lazy load)."""
#     print("\n🌀 Scrolling ke bawah untuk memuat semua produk...")
#     last_height = 0
#     same_height_count = 0
#     start_time = time.time()

#     while True:
#         page.evaluate(f"window.scrollBy(0, {step});")
#         time.sleep(2)
#         new_height = page.evaluate("document.body.scrollHeight")

#         if new_height == last_height:
#             same_height_count += 1
#         else:
#             same_height_count = 0
#         last_height = new_height

#         if same_height_count >= 3:
#             print("✅ Sudah mencapai bagian paling bawah halaman.")
#             break
#         if time.time() - start_time > max_wait:
#             print("⚠️ Waktu scroll habis (mungkin masih ada item belum muncul).")
#             break




# # ---------- HELPERS ----------

# def extract_tcin(href):
#     """Mengekstrak angka TCIN dari URL produk Target."""
#     if not href: return None
#     match = re.search(r'/A-(\d+)', href)
#     return match.group(1) if match else None

# # ---------- HELPERS ----------
# def auto_scroll_to_bottom(page, step=1000, max_wait=40):
#     """Scroll sampai tidak berubah lagi (lazy load)."""
#     print("\n🌀 Scrolling ke bawah untuk memuat semua produk...")
#     last_height = 0
#     same_height_count = 0
#     start_time = time.time()

#     while True:
#         page.evaluate(f"window.scrollBy(0, {step});")
#         time.sleep(2)
#         new_height = page.evaluate("document.body.scrollHeight")

#         if new_height == last_height:
#             same_height_count += 1
#         else:
#             same_height_count = 0
#         last_height = new_height

#         if same_height_count >= 3:
#             print("✅ Sudah mencapai bagian paling bawah halaman.")
#             break
#         if time.time() - start_time > max_wait:
#             print("⚠️ Waktu scroll habis (mungkin masih ada item belum muncul).")
#             break

# def scrape_tcin_from_page(page):
#     """Mengambil semua TCIN yang terlihat di halaman saat ini."""
#     tcin_found = []
#     # Selector spesifik untuk link judul produk
#     product_links = page.query_selector_all('a[data-test="@web/ProductCard/title"]')
    
#     for link in product_links:
#         href = link.get_attribute("href")
#         tcin = extract_tcin(href)
#         if tcin:
#             tcin_found.append(tcin)
    
#     return list(set(tcin_found)) # Menghapus duplikat di halaman yang sama

# # ---------- MAIN LOGIC ----------

# def main():
#     all_tcin = set() # Menggunakan set agar tidak ada TCIN ganda
    
#     with sync_playwright() as p:
#         proxy = get_random_proxy_config()
#         print(f"📡 Menggunakan Proxy: {proxy['server']}")

#         browser = p.chromium.launch(
#             headless=HEADLESS,
#             args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
#             proxy=proxy
#         )
        
#         context = browser.new_context(user_agent=USER_AGENT)
#         page = context.new_page()

#         try:
#             print(f"🌐 Menuju: {URL}")
#             page.goto(URL, wait_until="domcontentloaded", timeout=90000)
            
#             page_num = 1
#             while True:
#                 print(f"\n📄 Memproses Halaman {page_num}...")
                
#                 # Tunggu kontainer produk muncul
#                 try:
#                     page.wait_for_selector('a[data-test="@web/ProductCard/title"]', timeout=20000)
#                 except:
#                     print("⚠️ Kontainer produk tidak muncul, mencoba scroll...")

#                 auto_scroll_to_bottom(page)
                
#                 # Ambil TCIN
#                 found = scrape_tcin_from_page(page)
#                 for t in found:
#                     all_tcin.add(t)
                
#                 print(f"✅ Berhasil mengambil {len(found)} TCIN. Total terkumpul: {len(all_tcin)}")

#                 # Navigasi ke Halaman Berikutnya
#                 next_button = page.query_selector('button[data-test="next"]')
#                 if next_button and next_button.get_attribute("disabled") is None:
#                     print("➡️ Klik Next...")
#                     next_button.click()
#                     # Tunggu loading sebentar
#                     page.wait_for_timeout(3000)
#                     page_num += 1
#                 else:
#                     print("🏁 Sudah mencapai halaman terakhir.")
#                     break

#         except Exception as e:
#             print(f"❌ Terjadi kesalahan: {e}")
        
#         finally:
#             # Simpan ke CSV
#             if all_tcin:
#                 print(f"\n💾 Menyimpan {len(all_tcin)} TCIN ke {OUTPUT_FILE}...")
#                 with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
#                     writer = csv.writer(f)
#                     writer.writerow(["tcin"]) # Header
#                     for tcin in sorted(list(all_tcin)):
#                         writer.writerow([tcin])
#                 print("✨ Selesai!")
            
#             browser.close()

# if __name__ == "__main__":
#     main()



import requests
import time
import json
import random
import re
import csv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------- CONFIG PROXY (Webshare/Lainnya) ----------
PROXIES_LIST = [
    "191.96.254.80:6127:arssrhsq:x1vpi09f4v1g",
    "45.61.122.149:6441:arssrhsq:x1vpi09f4v1g",
    "45.61.124.153:6482:arssrhsq:x1vpi09f4v1g",
    "64.64.110.63:6586:arssrhsq:x1vpi09f4v1g",
    "145.223.58.21:6290:arssrhsq:x1vpi09f4v1g",
    "82.23.206.96:5902:arssrhsq:x1vpi09f4v1g",
    "38.154.233.46:5456:arssrhsq:x1vpi09f4v1g",
    "45.61.118.128:5825:arssrhsq:x1vpi09f4v1g",
    "191.96.202.229:6275:arssrhsq:x1vpi09f4v1g",
    "23.27.196.145:6514:arssrhsq:x1vpi09f4v1g",
    "154.6.126.37:6008:arssrhsq:x1vpi09f4v1g",
    "89.249.195.211:6966:arssrhsq:x1vpi09f4v1g",
    "147.124.198.69:5928:arssrhsq:x1vpi09f4v1g",
    "82.24.238.65:6872:arssrhsq:x1vpi09f4v1g",
    "38.154.217.34:7225:arssrhsq:x1vpi09f4v1g",
    "174.140.200.142:6422:arssrhsq:x1vpi09f4v1g",
    "46.202.224.238:5790:arssrhsq:x1vpi09f4v1g",
    "31.57.87.145:5830:arssrhsq:x1vpi09f4v1g",
    "38.154.233.181:5591:arssrhsq:x1vpi09f4v1g",
    "198.46.241.143:6678:arssrhsq:x1vpi09f4v1g",
    "23.27.203.134:6869:arssrhsq:x1vpi09f4v1g",
    "104.168.118.219:6175:arssrhsq:x1vpi09f4v1g",
    "152.232.14.43:7174:arssrhsq:x1vpi09f4v1g",
    "82.26.238.68:6375:arssrhsq:x1vpi09f4v1g",
    "89.249.194.231:6630:arssrhsq:x1vpi09f4v1g",
    "104.232.211.0:5613:arssrhsq:x1vpi09f4v1g",
    "38.154.217.123:7314:arssrhsq:x1vpi09f4v1g",
    "67.227.14.204:6796:arssrhsq:x1vpi09f4v1g"
]


def get_random_proxy_config():
    proxy_str = random.choice(PROXIES_LIST)
    ip, port, user, pw = proxy_str.split(':')
    return {
        "server": f"http://{ip}:{port}",
        "username": user,
        "password": pw
    }

# ---------- TARGET CONFIG ----------
OUTPUT_FILE = "Snacks.csv"
# URL = "https://www.target.com/c/frozen-foods-grocery/-/N-5xszd"
URL = "https://www.target.com/c/snacks-grocery/-/N-5xsy9"
HEADLESS = False
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Variabel global untuk menampung hasil
all_tcin = set()

# ---------- HELPERS ----------
def extract_tcin(href):
    if not href: return None
    match = re.search(r'/A-(\d+)', href)
    return match.group(1) if match else None

def auto_scroll_to_bottom(page, step=1000, max_wait=40):
    print("🌀 Scrolling...")
    last_height = 0
    same_height_count = 0
    start_time = time.time()
    while True:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(1.5)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            same_height_count += 1
        else:
            same_height_count = 0
        last_height = new_height
        if same_height_count >= 3 or (time.time() - start_time > max_wait):
            break

def go_through_pagination(page):
    """Logika navigasi halaman demi halaman."""
    page_num = 1
    while True:
        print(f"\n📄 Memproses Halaman {page_num}...")
        
        # Tunggu produk muncul
        try:
            page.wait_for_selector('a[data-test="@web/ProductCard/title"]', timeout=20000)
        except:
            print("⚠️ Produk tidak muncul, mencoba lanjut...")

        auto_scroll_to_bottom(page)
        
        # Ambil TCIN dari halaman saat ini
        product_links = page.query_selector_all('a[data-test="@web/ProductCard/title"]')
        found_before = len(all_tcin)
        
        for link in product_links:
            tcin = extract_tcin(link.get_attribute("href"))
            if tcin:
                all_tcin.add(tcin)
        
        print(f"✅ Halaman {page_num}: +{len(all_tcin) - found_before} TCIN baru. Total: {len(all_tcin)}")

        # Cek tombol Next
        next_button = page.query_selector('button[data-test="next"]')
        if next_button and next_button.is_enabled():
            print("➡️ Pindah ke halaman berikutnya...")
            next_button.click()
            page.wait_for_timeout(4000) # Tunggu loading
            page_num += 1
        else:
            print("🏁 Mencapai halaman terakhir.")
            break

# ---------- MAIN LOGIC ----------
def main():
    print("🚀 Starting Playwright dengan Rotasi Proxy...")
    
    with sync_playwright() as p:
        proxy_config = get_random_proxy_config()
        print(f"📡 Menggunakan Proxy: {proxy_config['server']}")

        browser = p.chromium.launch(
            headless=HEADLESS, 
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"], 
            proxy=proxy_config
        )
        
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US",
            viewport={"width": 1366, "height": 900},
        )
        
        # --- OPTIMASI: BLOKIR GAMBAR (Hemat Kuota Proxy) ---
        page = context.new_page()
        page.route("**/*", lambda route: route.abort() 
                   if route.request.resource_type in ["image", "media", "font"] 
                   else route.continue_())

        # Hide automation
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            print(f"🌐 Menuju: {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=90000)
            
            # Jalankan pagination
            go_through_pagination(page)

        except PlaywrightTimeoutError:
            print("⚠️ Timeout: Koneksi lambat, mencoba berhenti dan simpan data...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            # Simpan data yang berhasil didapat sebelum browser ditutup
            if all_tcin:
                print(f"\n💾 Menyimpan {len(all_tcin)} TCIN ke {OUTPUT_FILE}...")
                with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["tcin"])
                    for tcin in sorted(list(all_tcin)):
                        writer.writerow([tcin])
                print("✨ Berhasil disimpan!")

            print("\n✅ Proses selesai.")
            if not HEADLESS:
                time.sleep(5) 
            browser.close()

if __name__ == "__main__":
    main()