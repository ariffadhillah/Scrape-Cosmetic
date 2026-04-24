
import requests
import json
from bs4 import BeautifulSoup
import time
import random
import csv

# --- KONFIGURASI ---
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/143.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
}

# Daftar proxy sesuai format Anda
PROXIES_LIST = [
    "166.88.169.235:6842:arssrhsq:x1vpi09f4v1g", "154.6.129.57:5527:arssrhsq:x1vpi09f4v1g",
    "23.236.196.126:6216:arssrhsq:x1vpi09f4v1g", "50.114.93.3:5987:arssrhsq:x1vpi09f4v1g",
    "198.37.121.19:6439:arssrhsq:x1vpi09f4v1g", "216.173.76.1:6628:arssrhsq:x1vpi09f4v1g",
    "173.211.68.189:6471:arssrhsq:x1vpi09f4v1g", "191.101.181.87:6840:arssrhsq:x1vpi09f4v1g",
    "206.206.119.148:6059:arssrhsq:x1vpi09f4v1g", "206.232.103.193:6350:arssrhsq:x1vpi09f4v1g",
    "45.39.4.47:5472:arssrhsq:x1vpi09f4v1g", "23.236.182.223:5999:arssrhsq:x1vpi09f4v1g",
    "23.27.210.194:6564:arssrhsq:x1vpi09f4v1g", "82.26.238.173:6480:arssrhsq:x1vpi09f4v1g",
    "104.245.244.64:6504:arssrhsq:x1vpi09f4v1g", "192.3.48.45:6038:arssrhsq:x1vpi09f4v1g",
    "185.216.105.98:6675:arssrhsq:x1vpi09f4v1g", "45.59.161.140:5932:arssrhsq:x1vpi09f4v1g",
    "148.135.151.115:8366:arssrhsq:x1vpi09f4v1g", "23.229.125.93:5362:arssrhsq:x1vpi09f4v1g",
    "104.239.78.204:6149:arssrhsq:x1vpi09f4v1g", "192.3.48.38:6031:arssrhsq:x1vpi09f4v1g",
    "64.64.118.136:6719:arssrhsq:x1vpi09f4v1g", "23.236.255.5:6781:arssrhsq:x1vpi09f4v1g",
    "107.172.116.178:5634:arssrhsq:x1vpi09f4v1g", "179.61.245.31:6810:arssrhsq:x1vpi09f4v1g",
    "23.94.138.138:6412:arssrhsq:x1vpi09f4v1g", "216.173.76.95:6722:arssrhsq:x1vpi09f4v1g",
    "192.186.151.66:8567:arssrhsq:x1vpi09f4v1g", "45.41.169.251:6912:arssrhsq:x1vpi09f4v1g",
    "31.58.26.18:6601:arssrhsq:x1vpi09f4v1g"
]

def format_proxy(raw_proxy):
    """Konversi format ip:port:user:pass ke dictionary requests"""
    try:
        ip, port, user, password = raw_proxy.split(':')
        formatted = f"http://{user}:{password}@{ip}:{port}"
        return {"http": formatted, "https": formatted}
    except Exception:
        return None

def _extract_itemlist(data, product_urls):
    """Ekstraksi URL dari JSON-LD ItemListElement"""
    if not isinstance(data, dict):
        return

    items = []
    # Jalur 1: Root adalah ItemList
    if data.get('@type') == 'ItemList':
        items = data.get('itemListElement', [])
    # Jalur 2: Di dalam mainEntity
    elif isinstance(data.get('mainEntity'), dict):
        me = data['mainEntity']
        if me.get('@type') == 'ItemList':
            items = me.get('itemListElement', [])

    if items and isinstance(items, list):
        for item in items:
            # Ambil URL (string atau nested dict)
            url = item.get('url') or (item.get('item', {}).get('url') if isinstance(item.get('item'), dict) else None)
            
            if url:
                if url.startswith('/'):
                    url = "https://www.walmart.com" + url
                # Hapus parameter query (?) agar tidak duplikat variant
                clean_url = url.split('?')[0]
                product_urls.add(clean_url)

def ambil_semua_url_produk_kategori(category_url, proxies=None):
    """Melakukan request ke Walmart dan memproses JSON-LD"""
    print(f"\n🔎 Scanning: {category_url}")
    try:
        session = requests.Session()
        response = session.get(category_url, headers=HEADERS, proxies=proxies, timeout=20)
        response.raise_for_status()

        if "px-captcha" in response.text or "Robot or Human" in response.text:
            print("❌ Proxy terdeteksi Anti-Bot (Captcha)! Mencoba halaman berikutnya...")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        product_urls = set()

        # Cari skrip JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        _extract_itemlist(item, product_urls)
                else:
                    _extract_itemlist(data, product_urls)
            except:
                continue

        print(f"✅ Berhasil menarik {len(product_urls)} URL produk.")
        return list(product_urls)

    except Exception as e:
        print(f"❌ Koneksi Error: {e}")
        return []

if __name__ == "__main__":
    # --- PENGATURAN TARGET ---
    BASE_URL = "https://www.walmart.com/browse/food/hummus-dips-salsa/"
    PARAMS = "976759_976789_7056897"
    SAVE_FILE = 'Url-.csv'
    MAX_PAGES = 25

    semua_produk = set() # Set otomatis mencegah duplikat

    for page_num in range(1, MAX_PAGES + 1):
        # Bangun URL halaman
        page_url = f"{BASE_URL}?{PARAMS}&page={page_num}"
        print(f"\n🚀 MEMPROSES HALAMAN {page_num} DARI {MAX_PAGES}")
        
        # Ambil proxy acak
        raw_proxy = random.choice(PROXIES_LIST)
        selected_proxy = format_proxy(raw_proxy)
        print(f"🌐 Proxy Aktif: {raw_proxy.split(':')[0]}")

        # Jalankan Scraper
        urls = ambil_semua_url_produk_kategori(page_url, proxies=selected_proxy)
        
        if urls:
            semua_produk.update(urls)
        
        # Jeda acak 5-10 detik agar tidak dicurigai
        delay = random.uniform(5, 10)
        print(f"⏳ Jeda {delay:.2f} detik... (Total Unik: {len(semua_produk)})")
        time.sleep(delay)

    # --- SIMPAN HASIL KE CSV ---
    print(f"\n🏁 SELESAI! Menyimpan data...")
    
    # Konversi set ke list yang terurut (A-Z)
    final_list = sorted(list(semua_produk))
    
    try:
        with open(SAVE_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header kolom
            writer.writerow(['url']) 
            
            # Data URL
            for item in final_list:
                writer.writerow([item])
                
        print(f"💾 File Tersimpan: '{SAVE_FILE}'")
        print(f"📊 Total URL Unik: {len(final_list)}")
    except Exception as e:
        print(f"❌ Gagal menulis CSV: {e}")