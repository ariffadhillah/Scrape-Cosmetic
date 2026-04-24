import requests
from bs4 import BeautifulSoup
import json
import html
import re
import time
import random
import csv
import os

# --- KONFIGURASI ---
url_storefront = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=6506977011"
filename = "amazon_wholefoods_data.csv"

headers_base = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Upgrade-Insecure-Requests": "1"
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

# Kolom CSV (Header)
headers_csv = [
    "Category", "Product Name", "Price", "URL", "ASIN", "UPC", "Manufacturer", 
    "Item Weight", "Units", "Package Dimensions", "Serving Size", "Calories",
    "Total Fat", "Saturated Fat", "Cholesterol", "Sodium", "Total Carbohydrate", 
    "Dietary Fiber", "Sugars", "Protein", "Brand", "Flavor", "Item Form", 
    "Product Description", "Ingredients", "Legal Disclaimer", "Image URL"
]

session = requests.Session()
session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

# ==========================================
# FUNGSI-FUNGSI SCRAPER
# ==========================================

# def get_product_text(soup, label=None):    
#     container_ = soup.find('div', id='productDescription')
#     if container_:
#         return container_.get_text(strip=True)
#     return None

# def get_product_table_value(soup, label):
#     tables = soup.find_all("table", class_="a-normal a-spacing-micro")
#     for table in tables:
#         for row in table.find_all("tr"):
#             cells = row.find_all("td")
#             if len(cells) < 2: continue
#             name = cells[0].get_text(strip=True)
#             value = cells[1].get_text(strip=True)
#             if name.lower() == label.lower():
#                 return value
#     return None

# def get_nutrition_value(soup, label):
#     table = soup.find("table", id="nic-nutrition-facts")
#     if not table: return None
#     spans = table.find_all("span")
#     for sp in spans:
#         if sp.get_text(strip=True).lower() == label.lower():
#             parent = sp.find_parent("td")
#             if parent:
#                 amount = parent.find("span", class_=lambda c: c and "nutrientAmountText" in c)
#                 if amount: return amount.get_text(strip=True)
#     return None

# def get_main_image(soup):
#     img = soup.select_one("#imgTagWrapperId img")
#     if not img: return None
#     hires = img.get("data-old-hires")
#     return hires.strip() if hires and hires.strip() else img.get("src")

# def get_ingredients(soup):
#     container = soup.find("div", id="important-information")
#     if not container: return None
#     header = container.find("span", string=lambda s: s and "ingredients" in s.lower())
#     if not header: return None
#     for p in header.find_all_next("p"):
#         if container not in p.parents: break
#         return p.get_text(strip=True)
#     return None

# def get_Legal_Disclaimer(soup):
#     container = soup.find("div", id="important-information")
#     if not container: return None
#     header = container.find("span", string=lambda s: s and "legal disclaimer" in s.lower())
#     if not header: return None
#     for p in header.find_all_next("p"):
#         if container not in p.parents: break
#         return p.get_text(strip=True)
#     return None

# def get_detail_by_label(soup, label_text):
#     labels = soup.select("#detailBullets_feature_div .a-text-bold")
#     for lab in labels:
#         if label_text.lower() in lab.get_text(strip=True).lower():
#             parent = lab.find_parent("span", class_="a-list-item")
#             if parent:
#                 spans = parent.find_all("span")
#                 if len(spans) >= 2: return spans[-1].get_text(strip=True)
#     return None

# def get_value_from_row_by_text(soup, row_id, label_text):
#     row = soup.find("tr", id=row_id)
#     if not row: return None
#     label = row.find("span", string=lambda x: x and label_text in x)
#     if not label: return None
#     value_td = label.find_parent("td").find_next_sibling("td")
#     return value_td.get_text(strip=True) if value_td else None

# def get_price(soup):
#     selectors = [
#         "#corePriceDisplay_desktop_feature_div span.a-price span.a-offscreen",
#         "#corePrice_feature_div span.a-price span.a-offscreen",
#         "span.a-price span.a-offscreen"
#     ]
#     for sel in selectors:
#         el = soup.select_one(sel)
#         if el: return el.get_text(strip=True)
#     return None















# Berikan nilai default = None
def get_product_text(soup, label=None):    
    container_ = soup.find('div', id='productDescription')
    
    if container_:
        return container_.get_text(strip=True)
    
    return None

# ==========================================
# FUNGSI-FUNGSI TAMBAHAN ANDA
# ==========================================

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



def get_nutrition_value(soup, label):

    table = soup.find("table", id="nic-nutrition-facts")
    if not table:
        return None

    # cari semua span yang mengandung text label
    spans = table.find_all("span")

    for sp in spans:
        text = sp.get_text(strip=True)

        # cocokkan label (exact atau contains)
        if text.lower() == label.lower():

            # cari sibling berikutnya yang berisi amount
            parent = sp.find_parent("td")

            if parent:
                amount = parent.find(
                    "span",
                    class_=lambda c: c and "nutrientAmountText" in c
                )

                if amount:
                    return amount.get_text(strip=True)

    return None


def get_reviews_count(soup):
    el = soup.select_one("#acrCustomerReviewText")
    if not el: return None
    text = el.get_text(strip=True)
    num = re.search(r'[\d,]+', text)
    if not num: return None
    count = num.group(0).replace(",", "")
    return int(count)

def get_main_image(soup):
    img = soup.select_one("#imgTagWrapperId img")
    if not img: return None
    hires = img.get("data-old-hires")
    if hires and hires.strip(): return hires.strip()
    src = img.get("src")
    if src: return src.strip()
    return None

def get_ingredients(soup):
    container = soup.find("div", id="important-information")
    if not container: return None
    header = container.find("span", string=lambda s: s and "ingredients" in s.lower())
    if not header: return None
    for p in header.find_all_next("p"):
        if container not in p.parents: break
        text = p.get_text(strip=True)
        if text: return text
    return None

def get_Legal_Disclaimer(soup):
    container = soup.find("div", id="important-information")
    if not container: return None
    header = container.find("span", string=lambda s: s and "legal disclaimer" in s.lower())
    if not header: return None
    for p in header.find_all_next("p"):
        if container not in p.parents: break
        text = p.get_text(strip=True)
        if text: return text
    return None

def get_disclaimer(soup):
    container = soup.find("div", id="storeDisclaimer_feature_div")
    if not container: return None
    label = container.find("strong", string=lambda s: s and "disclaimer" in s.lower())
    if not label: return None
    p = label.find_parent("p")
    if not p: return None
    text = p.get_text(" ", strip=True)
    text = text.replace("Disclaimer:", "").strip()
    return text

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

def get_value_from_row_by_text(soup, row_id, label_text):
    row = soup.find("tr", id=row_id)
    if not row: return None
    label = row.find("span", string=lambda x: x and label_text in x)
    if not label: return None
    value_td = label.find_parent("td").find_next_sibling("td")
    if not value_td: return None
    return value_td.get_text(strip=True)

# def get_price(soup):
#     selectors = [
#         "#corePriceDisplay_desktop_feature_div span.a-price span.a-offscreen",
#         "#corePrice_feature_div span.a-price span.a-offscreen",
#         "#apex_desktop span.a-price span.a-offscreen",
#         "span.a-price span.a-offscreen"
#     ]
#     for sel in selectors:
#         el = soup.select_one(sel)
#         if el: return el.get_text(strip=True)
#     return None


def get_price(soup):

    selectors = [
        "#corePriceDisplay_desktop_feature_div span.a-price span.a-offscreen",
        "#corePrice_feature_div span.a-price span.a-offscreen",
        "#apex_desktop span.a-price span.a-offscreen",
        "span.a-price span.a-offscreen"
    ]

    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return el.get_text(strip=True)

    return None



def get_soup(url):
    headers = headers_base.copy()
    headers["User-Agent"] = random.choice(user_agents)
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






# ==========================================
# PROSES UTAMA
# ==========================================

# Persiapan CSV
if not os.path.exists(filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers_csv)

print("Sedang mengambil daftar produk dari storefront...")
soup_main = get_soup(url_storefront)
if not soup_main:
    print("Gagal memuat halaman utama."); exit()

all_categories = []
sections = soup_main.find_all("div", attrs={"data-carouselheadingattributesstring": True})

for sec in sections:
    try:
        heading_json = html.unescape(sec["data-carouselheadingattributesstring"])
        title_cat = json.loads(heading_json).get("headingText", "Unknown").strip()
    except: title_cat = "Unknown"

    seen_asins = set()
    urls_in_section = []
    for a in sec.select("a[href*='/dp/']"):
        asin = extract_asin(a.get("href"))
        if asin and asin not in seen_asins:
            seen_asins.add(asin); urls_in_section.append(f"https://www.amazon.com/dp/{asin}")
    
    if urls_in_section:
        all_categories.append({"category": title_cat, "urls": urls_in_section})

print(f"\nTotal kategori ditemukan: {len(all_categories)}")
print(f"Menyimpan hasil ke: {filename}\n")

for cat_item in all_categories:
    print(f"\n--- CATEGORY: {cat_item['category']} ---")
    
    for product_url in cat_item['urls']:
        print(f"Processing: {product_url}")
        time.sleep(random.uniform(2, 5))
        
        soup = get_soup(product_url)
        if not soup: continue
        
        title_tag = soup.select_one("#productTitle") or soup.select_one(".qa-title-text")
        if title_tag:
            product_name = title_tag.get_text(strip=True)
            
            # Susun baris data
            row_data = [
                cat_item['category'],
                product_name,
                get_price(soup),
                product_url,
                get_detail_by_label(soup, "ASIN"),
                get_detail_by_label(soup, "UPC"),
                get_detail_by_label(soup, "Manufacturer"),
                get_detail_by_label(soup, "Item Weight"),
                get_detail_by_label(soup, "Units"),
                get_detail_by_label(soup, "Package Dimensions"),
                get_value_from_row_by_text(soup, "nic-nutrition-facts-serving-size", "Serving size"),
                get_value_from_row_by_text(soup, "nic-nutrition-facts-energy", "Calories"),
                get_nutrition_value(soup, "Total Fat"),
                get_nutrition_value(soup, "Saturated Fat"),
                get_nutrition_value(soup, "Cholesterol"),
                get_nutrition_value(soup, "Sodium"),
                get_nutrition_value(soup, "Total Carbohydrate"),
                get_nutrition_value(soup, "Dietary Fiber"),
                get_nutrition_value(soup, "Sugars"),
                get_nutrition_value(soup, "Protein"),
                get_product_table_value(soup, "Brand"),
                get_product_table_value(soup, "Flavor"),
                get_product_table_value(soup, "Item Form"),
                get_product_text(soup), # HASIL TEXT PRODUK
                get_ingredients(soup),
                get_Legal_Disclaimer(soup),
                get_main_image(soup)
            ]

            # Simpan ke CSV
            with open(filename, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row_data)

            print(f"  [SUCCESS] {product_name[:40]}...")
        else:
            print(f"  [SKIPPED] Title not found.")

print("\nSelesai! Semua data telah tersimpan.")