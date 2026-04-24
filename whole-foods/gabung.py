import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import html
import csv
import os

# --- KONFIGURASI ---
url_storefront = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"
BASE_URL = "https://www.amazon.com/dp/"
FILENAME = "test-amazon_variants_complete_data.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

HEADERS_CSV = [
    "Category", "Product Name", "Price", "URL", "ASIN", "UPC", "Manufacturer", 
    "Item Weight", "Units", "Package Dimensions", "Serving Size", "Calories",
    "Total Fat", "Saturated Fat", "Cholesterol", "Sodium", "Total Carbohydrate", 
    "Dietary Fiber", "Sugars", "Protein", "Vitamin A", "Vitamin C", "Calcium", "Iron",
    "Brand", "Flavor", "Item Form", "Product Description", "Ingredients", "Image URL"
]

# ==========================================
# FUNGSI EKSTRAKSI (DATA MINING)
# ==========================================

def get_product_text(soup):    
    container_ = soup.find('div', id='productDescription')
    return container_.get_text(strip=True) if container_ else None

def get_product_table_value(soup, label):
    tables = soup.find_all("table", class_="a-normal a-spacing-micro")
    for table in tables:
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2: continue
            if cells[0].get_text(strip=True).lower() == label.lower():
                return cells[1].get_text(strip=True)
    return None

def get_nutrition_value(soup, label):
    table = soup.find("table", id="nic-nutrition-facts")
    if not table: return None
    spans = table.find_all("span")
    for sp in spans:
        if sp.get_text(strip=True).lower() == label.lower():
            parent = sp.find_parent("td")
            if parent:
                amount = parent.find("span", class_=lambda c: c and "nutrientAmountText" in c)
                if amount: return amount.get_text(strip=True)
    return None

def get_main_image(soup):
    img = soup.select_one("#imgTagWrapperId img")
    if not img: return None
    hires = img.get("data-old-hires")
    return hires.strip() if hires and hires.strip() else img.get("src")

def get_ingredients(soup):
    container = soup.find("div", id="important-information")
    if not container: return None
    header = container.find("span", string=lambda s: s and "ingredients" in s.lower())
    if not header: return None
    for p in header.find_all_next("p"):
        if container not in p.parents: break
        return p.get_text(strip=True)
    return None

def get_detail_by_label(soup, label_text):
    labels = soup.select("#detailBullets_feature_div .a-text-bold")
    for lab in labels:
        if label_text.lower() in lab.get_text(strip=True).lower():
            parent = lab.find_parent("span", class_="a-list-item")
            if parent:
                spans = parent.find_all("span")
                if len(spans) >= 2: return spans[-1].get_text(strip=True)
    return None

def get_value_from_row_by_text(soup, row_id, label_text):
    row = soup.find("tr", id=row_id)
    if not row: return None
    label = row.find("span", string=lambda x: x and label_text in x)
    if not label: return None
    value_td = label.find_parent("td").find_next_sibling("td")
    return value_td.get_text(strip=True) if value_td else None

def get_price(soup):
    selectors = ["#corePriceDisplay_desktop_feature_div span.a-offscreen", "#corePrice_feature_div span.a-offscreen", "span.a-price span.a-offscreen"]
    for sel in selectors:
        el = soup.select_one(sel)
        if el: return el.get_text(strip=True)
    return "N/A"

# ==========================================
# FUNGSI CORE (ASIN & VARIANT)
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
                    color_to_asin = data.get("colorToAsin", {})
                    for key in color_to_asin:
                        v_asin = color_to_asin[key].get("asin")
                        if v_asin: asins.add(v_asin)
                except: pass
    return list(asins)

def get_soup(url, session):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.amazon.com/"
    }
    try:
        time.sleep(random.uniform(3, 7)) # Jeda aman
        res = session.get(url, headers=headers, timeout=30)
        if res.status_code == 200:
            if "robot check" in res.text.lower(): return "CAPTCHA"
            return BeautifulSoup(res.text, "html.parser")
    except: pass
    return None

# ==========================================
# RUNNER UTAMA
# ==========================================

def main():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode='w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(HEADERS_CSV)

    session = requests.Session()
    session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

    print("--- MENGAMBIL DAFTAR PRODUK DARI STOREFRONT ---")
    main_soup = get_soup(url_storefront, session)
    if not main_soup or main_soup == "CAPTCHA":
        print("Gagal akses storefront."); return

    sections = main_soup.find_all("div", attrs={"data-carouselheadingattributesstring": True})
    
    for sec in sections:
        try:
            cat_json = json.loads(html.unescape(sec["data-carouselheadingattributesstring"]))
            category = cat_json.get("headingText", "Unknown")
        except: category = "Unknown"

        # Cari ASIN utama di kategori ini
        parent_asins = set()
        for a in sec.select("a[href*='/dp/']"):
            match = re.search(r"([A-Z0-9]{10})", a.get("href"))
            if match: parent_asins.add(match.group(1))

        print(f"\nKategori: {category} ({len(parent_asins)} Produk Utama)")

        for p_asin in parent_asins:
            print(f">> Membongkar Varian dari Parent ASIN: {p_asin}")
            p_soup = get_soup(f"{BASE_URL}{p_asin}", session)
            
            if not p_soup or p_soup == "CAPTCHA":
                print("   [!] Skip: Captcha/Error"); continue

            # Dapatkan semua varian ASIN
            variants = get_all_variant_asins(p_soup)
            if not variants: variants = [p_asin]
            
            print(f"   Ditemukan {len(variants)} varian.")

            for idx, v_asin in enumerate(variants):
                # Reset sesi sesekali
                if idx > 0 and idx % 3 == 0: session = requests.Session()

                v_url = f"{BASE_URL}{v_asin}?th=1&psc=1"
                v_soup = get_soup(v_url, session)

                if v_soup and v_soup != "CAPTCHA":
                    title_tag = v_soup.select_one("#productTitle")
                    if not title_tag: continue
                    
                    product_name = title_tag.get_text(strip=True)
                    
                    # Simpan data ke list untuk CSV
                    row = [
                        category, product_name, get_price(v_soup), v_url, v_asin,
                        get_detail_by_label(v_soup, "UPC"),
                        get_detail_by_label(v_soup, "Manufacturer"),
                        get_detail_by_label(v_soup, "Item Weight"),
                        get_detail_by_label(v_soup, "Units"),
                        get_detail_by_label(v_soup, "Package Dimensions"),
                        get_value_from_row_by_text(v_soup, "nic-nutrition-facts-serving-size", "Serving size"),
                        get_value_from_row_by_text(v_soup, "nic-nutrition-facts-energy", "Calories"),
                        get_nutrition_value(v_soup, "Total Fat"),
                        get_nutrition_value(v_soup, "Saturated Fat"),
                        get_nutrition_value(v_soup, "Cholesterol"),
                        get_nutrition_value(v_soup, "Sodium"),
                        get_nutrition_value(v_soup, "Total Carbohydrate"),
                        get_nutrition_value(v_soup, "Dietary Fiber"),
                        get_nutrition_value(v_soup, "Sugars"),
                        get_nutrition_value(v_soup, "Protein"),
                        get_product_table_value(v_soup, "Brand"),
                        get_product_table_value(v_soup, "Flavor"),
                        get_product_table_value(v_soup, "Item Form"),
                        get_product_text(v_soup),
                        get_ingredients(v_soup),
                        get_main_image(v_soup)
                    ]

                    # Append ke CSV
                    with open(FILENAME, mode='a', newline='', encoding='utf-8') as f:
                        csv.writer(f).writerow(row)
                    
                    print(f"      [{idx+1}/{len(variants)}] SAVED: {v_asin} - {product_name[:30]}...")
                else:
                    print(f"      [{idx+1}/{len(variants)}] FAILED: {v_asin}")

if __name__ == "__main__":
    main()