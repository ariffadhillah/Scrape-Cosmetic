import requests
from bs4 import BeautifulSoup
import json
import html
import re
import time
import random

# --- KONFIGURASI ---
url_storefront = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=6506977011"
headers_base = {
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Upgrade-Insecure-Requests": "1"
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

session = requests.Session()
# session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

session.cookies.update({
    "i18n-prefs": "USD",
    "lc-main": "en_US"
})



# ==========================================
# FUNGSI UTAMA SCRAPER
# ==========================================

def get_detail_by_label(soup, label_text):
    labels = soup.select("#detailBullets_feature_div .a-text-bold")
    for lab in labels:
        text = lab.get_text(strip=True)
        if label_text.lower() in text.lower():
            parent = lab.find_parent("span", class_="a-list-item")
            if parent:
                spans = parent.find_all("span")
                if len(spans) >= 2:
                    return spans[-1].get_text(strip=True)
    return None


def get_soup(url):
    headers = headers_base.copy()
    headers["User-Agent"] = random.choice(user_agents)
    headers["Referer"] = "https://www.amazon.com/"
    try:
        res = session.get(url, headers=headers, timeout=40)
        if res.status_code == 200:
            return BeautifulSoup(res.text, "html.parser")
        elif res.status_code == 503:
            print("  [503] Terdeteksi Bot! Menunggu 15 detik...")
            time.sleep(15)
    except Exception as e:
        print(f"  Error: {e}")
    return None

def extract_asin(text):
    match = re.search(r"([A-Z0-9]{10})", text)
    return match.group(1) if match else None

# STEP 1: AMBIL SEMUA URL UNIK
print("Sedang mengambil daftar produk dari storefront...")
soup_main = get_soup(url_storefront)
if not soup_main:
    print("Gagal memuat halaman utama.")
    exit()

all_data = []
sections = soup_main.find_all("div", attrs={"data-carouselheadingattributesstring": True})

for sec in sections:
    try:
        heading_json = html.unescape(sec["data-carouselheadingattributesstring"])
        title_cat = json.loads(heading_json).get("headingText", "Unknown").strip()
    except:
        title_cat = "Unknown"

    seen_asins = set()
    urls_in_section = []

    for a in sec.select("a[href*='/dp/']"):
        asin = extract_asin(a.get("href"))
        if asin and asin not in seen_asins:
            seen_asins.add(asin)
            urls_in_section.append(f"https://www.amazon.com/dp/{asin}")

    carousel_options = sec.get("data-a-carousel-options")
    if carousel_options:
        try:
            ajax_ids = json.loads(carousel_options).get("ajax", {}).get("id_list", [])
            for item_str in ajax_ids:
                asin = json.loads(item_str).get("id")
                if asin and asin not in seen_asins:
                    seen_asins.add(asin)
                    urls_in_section.append(f"https://www.amazon.com/dp/{asin}")
        except: pass

    if urls_in_section:
        all_data.append({"category": title_cat, "urls": urls_in_section})

# STEP 2: KUNJUNGI DAN AMBIL DETAIL LENGKAP
print(f"\nTotal kategori ditemukan: {len(all_data)}")
print("Memulai proses pengambilan detail produk...\n")

for item in all_data:
    print(f"\n--- CATEGORY: {item['category']} ---")
    
    for product_url in item['urls']:
        time.sleep(random.uniform(2, 5))
        
        soup = get_soup(product_url)
        if soup:
            # Menggunakan multiple selector agar meminimalkan 'Not Found'
            title_tag = soup.select_one("#productTitle") or soup.select_one(".qa-title-text")
            
            if title_tag:
                # Ambil Semua Data Berdasarkan Fungsi Anda
                product_name = title_tag.get_text(strip=True)

                upc = get_detail_by_label(soup, "UPC")
                
                print("Product Name:", product_name)
                print("Product_url:", product_url)
                print("UPC:", upc)

                print("-" * 30)
                print("-" * 20)
                # break
            
            else:
                print(f"TITLE: Not Found (Captcha/OOS) -> {product_url}")