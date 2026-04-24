import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random

# --- KONFIGURASI TESTING ---
TARGET_ASIN = "B09DS5J8F9" 
BASE_URL = "https://www.amazon.com/dp/"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# ==========================================
# FUNGSI EKSTRAKSI DATA (MENGEMBALIKAN STRING)
# ==========================================

def get_price(soup):
    """
    Ekstraksi harga dengan Multi-Layer Selector.
    Memprioritaskan class spesifik dari HTML Accordion.
    """
    # 1. Prioritas Utama: Class yang Anda temukan di HTML Accordion
    # <span class="... apex-pricetopay-value">
    price_pay = soup.select_one("span.apex-pricetopay-value .a-offscreen")
    if price_pay:
        return price_pay.get_text(strip=True)

    # 2. Alternatif: Jika a-offscreen di dalam apex-pricetopay-value tidak ada
    # Kita ambil teks langsung dari kontainer harganya
    price_pay_raw = soup.select_one("span.apex-pricetopay-value")
    if price_pay_raw:
        # Kita ambil teks, tapi kita bersihkan jika ada teks tambahan
        raw_text = price_pay_raw.get_text(strip=True)
        # Ambil pola harga seperti $8.31
        match = re.search(r"\$\d+\.\d{2}", raw_text)
        if match:
            return match.group(0)

    # 3. Struktur umum Amazon untuk 'Price to Pay' (Core Price)
    core_price = soup.select_one("#corePrice_desktop .a-offscreen") or \
                 soup.select_one("#corePrice_feature_div .a-offscreen")
    if core_price:
        return core_price.get_text(strip=True)

    # 4. Struktur khusus Grocery/Whole Foods
    grocery_price = soup.select_one("#alm-container-with-almlogo .a-price .a-offscreen")
    if grocery_price:
        return grocery_price.get_text(strip=True)

    return "Price Not Found"

def get_product_table_value(soup, label):

    tables = soup.find_all("table", class_="a-normal a-spacing-micro")

    for table in tables:
        for row in table.find_all("tr"):

            cells = row.find_all("td")
            if len(cells) < 2:
                continue

            name = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)

            if name.lower() == label.lower():
                return value

    return None



# ==========================================
# LOGIKA CRAWLER & VARIAN
# ==========================================



def get_all_variant_asins(soup):
    asins = set()
    scripts = soup.find_all("script", type="text/javascript")
    for script in scripts:
        content = script.string
        if content and "colorToAsin" in content:
            match = re.search(r"jQuery\.parseJSON\('(.+?)'\)", content)
            if match:
                try:
                    raw_json = match.group(1).replace("\\'", "'").encode().decode('unicode_escape')
                    data = json.loads(raw_json)
                    for key in data.get("colorToAsin", {}):
                        v_asin = data["colorToAsin"][key].get("asin")
                        if v_asin: asins.add(v_asin)
                except: pass
    return list(asins)

# ==========================================
# MAIN TESTING LOOP
# ==========================================



def get_soup(url, session, current_asin=None):
    # Header yang lebih lengkap untuk mensimulasikan browser asli
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "authority": "www.amazon.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "device-memory": "8",
        "downlink": "10",
        "referer": f"https://www.amazon.com/dp/{TARGET_ASIN}",
        # "user-agent": random.choice(USER_AGENTS),
    }
    
    try:
        # Tambahkan jeda acak agar tidak terdeteksi bot
        time.sleep(random.uniform(3, 6))
        
        # Tambahkan parameter psc=1 dan th=1 secara paksa
        clean_url = url.split('?')[0]
        params = {"th": "1", "psc": "1"}
        
        res = session.get(clean_url, headers=headers, params=params, timeout=30)
        
        if res.status_code == 200:
            if "robot check" in res.text.lower():
                return "CAPTCHA"
            # Verifikasi apakah Amazon benar-benar memberikan halaman ASIN yang diminta
            if current_asin and current_asin not in res.text:
                # Jika Amazon redirect ke ASIN lain, kita coba paksa ambil harganya dari JSON
                pass 
            return BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print(f"Error: {e}")
    return None

def main():
    # Gunakan session tunggal di awal, tapi bersihkan cookies di tengah loop
    session = requests.Session()
    session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
    
    print(f"--- MENCARI VARIAN UNTUK ASIN: {TARGET_ASIN} ---")
    
    first_soup = get_soup(f"{BASE_URL}{TARGET_ASIN}", session)
    if not first_soup or first_soup == "CAPTCHA": return
    
    variant_list = get_all_variant_asins(first_soup)
    if not variant_list: variant_list = [TARGET_ASIN]
    
    print(f"Ditemukan {len(variant_list)} varian.\n")

    for i, v_asin in enumerate(variant_list):
        print(f"TESTING ASIN [{i+1}/{len(variant_list)}]: {v_asin}")
        
        # TRIK: Setiap ganti ASIN, kita hapus cookies tertentu agar tidak 'nyangkut'
        session.cookies.set("session-id", "", domain=".amazon.com")
        session.cookies.set("session-id-time", "", domain=".amazon.com")
        
        v_url = f"https://www.amazon.com/dp/{v_asin}"
        v_soup = get_soup(v_url, session, current_asin=v_asin)
        
        if v_soup and v_soup != "CAPTCHA":
            # 1. Ambil Harga dari input hidden (Sesuai ide Anda sebelumnya)
            price = get_price(v_soup)
            
            # 2. Ambil Nama
            title_el = v_soup.select_one("#productTitle")
            name = title_el.get_text(strip=True) if title_el else "Unknown"
            
            # 3. Ambil Kalori (Kita perbaiki agar tidak mengambil angka acak)
            # Kita hanya ambil angka jika panjangnya masuk akal (1-4 digit)
            cal_tag = v_soup.find(id="nic-nutrition-facts-energy")
            if cal_tag:
                raw_cal = "".join(filter(str.isdigit, cal_tag.get_text()))
            else:
                # Cari pola "Calories 10" di teks
                match_cal = re.search(r'Calories\s*(\d+)', v_soup.get_text())
                raw_cal = match_cal.group(1) if match_cal else "N/A"
            
            calories = raw_cal if (raw_cal.isdigit() and len(raw_cal) < 5) else "N/A"

            print(f"      NAME        : {name[:60]}...")
            print(f"      PRICE       : {price}")
            print(f"      CALORIES    : {calories}")
        
        print("-" * 55)


if __name__ == "__main__":
    main()

