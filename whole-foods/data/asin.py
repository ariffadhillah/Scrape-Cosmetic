import requests
from bs4 import BeautifulSoup
import json
import html
import re
import time
import random
import csv

# --- KONFIGURASI ---
url_storefront = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=18774136011&ref_=WF19425_12&pf_rd_r=K712X12MZHWW8C89TV1S&pf_rd_p=f21d6a0a-60ce-41bc-b730-53f6a145dbea&pf_rd_m=A2R2RITDJNW1Q6&pf_rd_s=zone-7-slot-7_2&pf_rd_t=&pf_rd_i=WAYSTOSHOP"
headers_base = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

session = requests.Session()
session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})


def get_soup(url):
    headers = headers_base.copy()
    headers["User-Agent"] = random.choice(user_agents)
    try:
        res = session.get(url, headers=headers, timeout=20)
        if res.status_code == 200:
            return BeautifulSoup(res.text, "html.parser")
        elif res.status_code == 404:
            print(f"  [404] Product not found: {url}")
        elif res.status_code == 503:
            print("  [503] Terdeteksi Bot oleh Amazon! Berhenti sejenak...")
            time.sleep(10)
    except Exception as e:
        print(f"  Error accessing {url}: {e}")
    return None


def extract_asin(text):
    match = re.search(r"([A-Z0-9]{10})", text)
    return match.group(1) if match else None


# ==========================================
# STEP 1: AMBIL SEMUA URL UNIK TERLEBIH DAHULU
# ==========================================
print("Sedang mengambil daftar produk dari storefront...")
soup_main = get_soup(url_storefront)
if not soup_main:
    print("Gagal memuat halaman utama.")
    raise SystemExit(1)

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

    # Ambil dari link <a>
    for a in sec.select("a[href*='/dp/']"):
        asin = extract_asin(a.get("href", ""))
        if asin and asin not in seen_asins:
            seen_asins.add(asin)
            urls_in_section.append(f"https://www.amazon.com/dp/{asin}")

    # Ambil dari Carousel JSON
    carousel_options = sec.get("data-a-carousel-options")
    if carousel_options:
        try:
            ajax_ids = json.loads(carousel_options).get("ajax", {}).get("id_list", [])
            for item_str in ajax_ids:
                asin = json.loads(item_str).get("id")
                if asin and asin not in seen_asins:
                    seen_asins.add(asin)
                    urls_in_section.append(f"https://www.amazon.com/dp/{asin}")
        except:
            pass

    if urls_in_section:
        all_data.append({"category": title_cat, "urls": urls_in_section})

print(f"\nTotal kategori ditemukan: {len(all_data)}")


# ==========================================
# STEP 2: KUNJUNGI SETIAP URL DAN AMBIL TITLE
# + SIMPAN KE CSV
# ==========================================
output_csv = "daftar_asin_Vitamins & Supplements.csv"
rows = []  # tempat nyimpen hasil

print("Memulai proses pengambilan judul produk...\n")

for item in all_data:
    category = item["category"]
    print(f"\n--- CATEGORY: {category} ---")

    for product_url in item["urls"]:
        time.sleep(random.uniform(1, 3))

        product_soup = get_soup(product_url)
        product_name = "Not Found"

        if product_soup:
            title_tag = product_soup.select_one("#productTitle")
            if title_tag:
                product_name = title_tag.get_text(strip=True)

        # print(f"TITLE: {product_name}")
        print(f"LINK : {product_url}\n")

        # simpan ke list rows
        rows.append({
            "asin": product_url.replace("https://www.amazon.com/dp/", "")
        })

# Tulis ke CSV (UTF-8)
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["asin"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Selesai! Data tersimpan ke: {output_csv}")