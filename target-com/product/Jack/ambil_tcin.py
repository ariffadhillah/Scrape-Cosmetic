import requests
import time
import json
import random
import re
import csv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------- CONFIG PROXY (Webshare/Lainnya) ----------
PROXIES_LIST = [
# "166.88.169.235:6842:arssrhsq:x1vpi09f4v1g",
# "154.6.129.57:5527:arssrhsq:x1vpi09f4v1g",
"23.236.196.126:6216:arssrhsq:x1vpi09f4v1g",
"50.114.93.3:5987:arssrhsq:x1vpi09f4v1g",
"198.37.121.19:6439:arssrhsq:x1vpi09f4v1g",
"216.173.76.1:6628:arssrhsq:x1vpi09f4v1g",
"173.211.68.189:6471:arssrhsq:x1vpi09f4v1g",
"191.101.181.87:6840:arssrhsq:x1vpi09f4v1g",
"206.206.119.148:6059:arssrhsq:x1vpi09f4v1g",
"206.232.103.193:6350:arssrhsq:x1vpi09f4v1g",
"45.39.4.47:5472:arssrhsq:x1vpi09f4v1g",
"23.236.182.223:5999:arssrhsq:x1vpi09f4v1g",
"23.27.210.194:6564:arssrhsq:x1vpi09f4v1g",
"82.26.238.173:6480:arssrhsq:x1vpi09f4v1g",
"104.245.244.64:6504:arssrhsq:x1vpi09f4v1g",
"192.3.48.45:6038:arssrhsq:x1vpi09f4v1g",
"185.216.105.98:6675:arssrhsq:x1vpi09f4v1g",
"45.59.161.140:5932:arssrhsq:x1vpi09f4v1g",
"148.135.151.115:8366:arssrhsq:x1vpi09f4v1g",
"23.229.125.93:5362:arssrhsq:x1vpi09f4v1g",
"104.239.78.204:6149:arssrhsq:x1vpi09f4v1g",
"192.3.48.38:6031:arssrhsq:x1vpi09f4v1g",
"64.64.118.136:6719:arssrhsq:x1vpi09f4v1g",
"23.236.255.5:6781:arssrhsq:x1vpi09f4v1g",
"107.172.116.178:5634:arssrhsq:x1vpi09f4v1g",
"179.61.245.31:6810:arssrhsq:x1vpi09f4v1g",
"23.94.138.138:6412:arssrhsq:x1vpi09f4v1g",
"216.173.76.95:6722:arssrhsq:x1vpi09f4v1g",
"192.186.151.66:8567:arssrhsq:x1vpi09f4v1g",
"45.41.169.251:6912:arssrhsq:x1vpi09f4v1g",
"31.58.26.18:6601:arssrhsq:x1vpi09f4v1g"
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
OUTPUT_FILE = "tcin_.csv"
# URL = "https://www.target.com/c/frozen-foods-grocery/-/N-5xszd"
URL = "https://www.target.com/c/frozen-bread-dough-foods-grocery/-/N-4tglw"
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