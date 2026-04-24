import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import html

# --- KONFIGURASI TESTING ---
TARGET_ASIN = "B09DS5J8F9" 
BASE_URL = "https://www.amazon.com/dp/"

# List User-Agent agar tidak monoton
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def get_soup(url, session):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Device-Memory": "8",
    }
    
    try:
        # Jeda waktu lebih lama agar Amazon tidak curiga (Bot Detection)
        wait_time = random.uniform(5, 10)
        time.sleep(wait_time)
        
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            if "sorry, we just need to make sure you're not a robot" in response.text.lower():
                return "CAPTCHA", response.text
            return BeautifulSoup(response.text, "html.parser"), response.text
        return None, response.text
    except Exception as e:
        print(f"  [!] Request Error: {e}")
        return None, ""

def get_all_variant_asins(soup):
    """Mengekstrak daftar varian ASIN dari blok JavaScript Amazon"""
    asins = set()
    scripts = soup.find_all("script", type="text/javascript")
    for script in scripts:
        content = script.string
        if content and "colorToAsin" in content:
            # Mencari JSON di dalam jQuery.parseJSON
            match = re.search(r"jQuery\.parseJSON\('(.+?)'\)", content)
            if match:
                try:
                    raw_json = match.group(1).replace("\\'", "'").encode().decode('unicode_escape')
                    data = json.loads(raw_json)
                    color_to_asin = data.get("colorToAsin", {})
                    for key in color_to_asin:
                        v_asin = color_to_asin[key].get("asin")
                        if v_asin: asins.add(v_asin)
                except: pass
    return list(asins)

def extract_details(soup):
    """Fungsi ekstraksi data dasar untuk testing"""
    data = {}
    
    # Ambil Judul
    title = soup.select_one("#productTitle")
    data['name'] = title.get_text(strip=True) if title else "N/A"
    
    # Ambil Harga (Multiselector)
    price_el = soup.select_one("#corePriceDisplay_desktop_feature_div span.a-offscreen") or \
               soup.select_one("#corePrice_feature_div span.a-offscreen") or \
               soup.select_one("span.a-price span.a-offscreen")
    data['price'] = price_el.get_text(strip=True) if price_el else "Out of Stock / No Price"
    
    return data

def save_debug_file(asin, content):
    filename = f"debug_{asin}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

# ==========================================
# RUNNER UTAMA
# ==========================================

def main():
    print(f"--- MEMULAI PROSES TESTING VARIAN ASIN: {TARGET_ASIN} ---")
    
    # Sesi pertama untuk mencari daftar ASIN varian
    current_session = requests.Session()
    soup, raw_html = get_soup(f"{BASE_URL}{TARGET_ASIN}", current_session)
    
    if soup == "CAPTCHA":
        print(" [!] Gagal di awal: Terdeteksi CAPTCHA. Coba ganti koneksi/IP.")
        return
    
    if not soup:
        print(" [!] Gagal memuat halaman awal.")
        return

    # Cari varian
    variant_list = get_all_variant_asins(soup)
    if not variant_list:
        variant_list = [TARGET_ASIN] # Jika tidak ada varian, proses ASIN input saja
        print(" [i] Tidak ditemukan varian. Memproses ASIN tunggal.")
    else:
        print(f" [i] Ditemukan {len(variant_list)} varian ASIN.\n")

    # Loop setiap varian
    for i, v_asin in enumerate(variant_list):
        print(f"[{i+1}/{len(variant_list)}] Sedang memproses: {v_asin}...")
        
        # RESET SESI setiap 2 request agar tidak mudah dilacak sebagai bot yang sama
        if i > 0 and i % 2 == 0:
            current_session = requests.Session()
            print("     (Sesi di-reset untuk keamanan)")

        v_url = f"{BASE_URL}{v_asin}?th=1&psc=1"
        v_soup, v_raw = get_soup(v_url, current_session)
        
        if v_soup == "CAPTCHA":
            print(f"     > FAILED: Kena Robot Check (Captcha) pada {v_asin}")
            save_debug_file(v_asin, v_raw)
        elif v_soup:
            details = extract_details(v_soup)
            if details['name'] != "N/A":
                print(f"     > SUCCESS: {details['name'][:60]}...")
                print(f"     > HARGA  : {details['price']}")
            else:
                print(f"     > FAILED: Judul tidak ditemukan (Layout berbeda?)")
                save_debug_file(v_asin, v_raw)
        else:
            print(f"     > FAILED: Gagal mengambil data (Status error)")
        
        print("-" * 40)

if __name__ == "__main__":
    main()