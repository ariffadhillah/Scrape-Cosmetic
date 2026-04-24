import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import csv  # <-- TAMBAHKAN INI di bagian import paling atas

# --- KONFIGURASI TESTING ---
TARGET_ASIN = "B07CX3GRXV" 
BASE_URL = "https://www.amazon.com/dp/"


OUTPUT_CSV = "tes-amazon_products-utama.csv"

FIELDNAMES = [
    "Category","Product Name","Product_url","Item Model Number","Package Dimensions","UPC","ASIN","Manufacturer","Units","Brand","Size","Flavor",
    "Item Weight","Specialty","Unit Count","Weight","Number of Items","Volume","Item Form","Allergen Information",
    "Cuisine","Variety","Temperature Condition","Number of Pieces","Package Information",
    "Produce sold as","Region of Origin",
    "Nutrition information Serving Size","Calories",
    "Total Fat","Saturated Fat","Trans Fat","Monounsaturated Fat","Polyunsaturated Fat","Cholesterol","Sodium",
    "Total Carbohydrate","Dietary Fiber","Soluble Fiber","Insoluble Fiber","Sugars","Added Sugars",
    "Starch","Other Carbohydrate","Sugar Alcohol","Protein","Vitamin A","Vitamin C","Calcium","Iron","Potassium",
    "Ingredients","Legal Disclaimer","Disclaimer","Product Description","Image Url","Reviews","Stars"    
]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# ==========================================
# FUNGSI EKSTRAKSI DATA (MENGEMBALIKAN STRING)
# ==========================================



def write_row_csv(row: dict, output_csv: str, fieldnames: list):
    """
    Tulis 1 row ke CSV.
    - Auto bikin header kalau file belum ada / masih kosong
    - Pastikan semua FIELDNAMES terisi (yang tidak ada -> "")
    """
    # normalize row: semua kolom fieldnames harus ada
    safe_row = {fn: row.get(fn, "") for fn in fieldnames}

    # newline="" penting supaya tidak double blank line di Windows
    with open(output_csv, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        # kalau file kosong -> tulis header
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(safe_row)

def _clean_label(s: str) -> str:
    if not s: return ""
    s = s.replace("\u200e", " ").replace("\u200f", " ").replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"\s*:\s*$", "", s)
    return s

def _clean_value(s: str) -> str:
    if not s: return ""
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_amazon_attributes(soup) -> dict:
    attrs = {}

    def put(k, v):
        k = _clean_label(k)
        v = _clean_value(v)
        if k and v and k not in attrs:
            attrs[k] = v

    for row in soup.select("table tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            put(th.get_text(" ", strip=True), td.get_text(" ", strip=True))

    for row in soup.select("table.a-normal.a-spacing-micro tr"):
        tds = row.find_all("td")
        if len(tds) >= 2:
            put(tds[0].get_text(" ", strip=True), tds[1].get_text(" ", strip=True))

    for li in soup.select("#detailBullets_feature_div li"):
        b = li.select_one("span.a-text-bold")
        if b:
            key = b.get_text(" ", strip=True)
            b.extract()
            val = li.get_text(" ", strip=True).lstrip(":").strip()
            put(key, val)
        else:
            txt = li.get_text(" ", strip=True)
            if ":" in txt:
                k, v = txt.split(":", 1)
                put(k, v)

    for row in soup.select("#productOverview_feature_div tr"):
        tds = row.find_all(["td", "th"])
        if len(tds) >= 2:
            put(tds[0].get_text(" ", strip=True), tds[1].get_text(" ", strip=True))

    return attrs

def get_product_value_universal(soup, label):
    attrs = extract_amazon_attributes(soup)
    key = _clean_label(label)

    synonyms = {
        "weight": ["weight", "item weight", "package weight", "shipping weight", "net weight", "product weight"],
        "volume": ["volume", "item volume", "package volume"],
        "ingredient type": ["ingredient type", "ingredients", "ingredient", "special ingredients"],
        "cuisine": ["cuisine", "cuisine type"],
        "specialty": ["specialty", "speciality", "diet type", "dietary information"],
    }

    candidates = synonyms.get(key, [key])

    for c in candidates:
        c = _clean_label(c)
        if c in attrs:
            return attrs[c]

    for k, v in attrs.items():
        for c in candidates:
            c = _clean_label(c)
            if c in k or k in c:
                return v

    return None
# --- FUNGSI KHUSUS UNTUK DATA NUTRISI (MENGEMBALIKAN STRING) ---


def get_product_text(soup):
    container_ = soup.find('div', id='productDescription')
    return container_.get_text(strip=True) if container_ else None

def get_nutrition_value(soup, label):
    table = soup.find("table", id="nic-nutrition-facts")
    if not table:
        return None

    for sp in table.find_all("span"):
        text = sp.get_text(strip=True)
        if text.lower() == label.lower():
            parent = sp.find_parent("td")
            if parent:
                amount = parent.find("span", class_=lambda c: c and "nutrientAmountText" in c)
                if amount:
                    return amount.get_text(strip=True)
    return None

def get_reviews_count(soup):
    el = soup.select_one("#acrCustomerReviewText")
    if not el:
        return None
    text = el.get_text(strip=True)
    num = re.search(r'[\d,]+', text)
    if not num:
        return None
    return int(num.group(0).replace(",", ""))

def get_main_image(soup):
    img = soup.select_one("#imgTagWrapperId img")
    if not img:
        return None
    hires = img.get("data-old-hires")
    if hires and hires.strip():
        return hires.strip()
    src = img.get("src")
    return src.strip() if src else None

def get_ingredients(soup):
    container = soup.find("div", id="important-information")
    if not container:
        return None
    header = container.find("span", string=lambda s: s and "ingredients" in s.lower())
    if not header:
        return None
    for p in header.find_all_next("p"):
        if container not in p.parents:
            break
        text = p.get_text(strip=True)
        if text:
            return text
    return None

def get_Legal_Disclaimer(soup):
    container = soup.find("div", id="important-information")
    if not container:
        return None
    header = container.find("span", string=lambda s: s and "legal disclaimer" in s.lower())
    if not header:
        return None
    for p in header.find_all_next("p"):
        if container not in p.parents:
            break
        text = p.get_text(strip=True)
        if text:
            return text
    return None

def get_disclaimer(soup):
    container = soup.find("div", id="storeDisclaimer_feature_div")
    if not container:
        return None
    label = container.find("strong", string=lambda s: s and "disclaimer" in s.lower())
    if not label:
        return None
    p = label.find_parent("p")
    if not p:
        return None
    text = p.get_text(" ", strip=True)
    return text.replace("Disclaimer:", "").strip()

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
    if not row:
        return None
    label = row.find("span", string=lambda x: x and label_text in x)
    if not label:
        return None
    value_td = label.find_parent("td").find_next_sibling("td")
    if not value_td:
        return None
    return value_td.get_text(strip=True)


# ==========================================
# LOGIKA CRAWLER & VARIAN
# ==========================================

def get_soup(url, session):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.amazon.com/"
    }
    try:
        # Delay testing: 5-8 detik agar aman
        time.sleep(random.uniform(5, 8))
        res = session.get(url, headers=headers, timeout=30)
        if res.status_code == 200:
            if "robot check" in res.text.lower():
                return "CAPTCHA"
            return BeautifulSoup(res.text, "html.parser")
    except: pass
    return None

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

def main():
    session = requests.Session()
    # Paksa region US untuk testing
    session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
    
    print(f"--- MENCARI VARIAN UNTUK ASIN: {TARGET_ASIN} ---")
    
    first_soup = get_soup(f"{BASE_URL}{TARGET_ASIN}", session)
    if first_soup == "CAPTCHA":
        print("Kena Block/Captcha di awal. Berhenti.")
        return
    if not first_soup: return
    
    variant_list = get_all_variant_asins(first_soup)
    if not variant_list:
        variant_list = [TARGET_ASIN]
        print("Tidak ada varian, memproses ASIN tunggal.")
    else:
        print(f"Ditemukan {len(variant_list)} varian. Memulai testing data mentah...\n")

    for i, v_asin in enumerate(variant_list):
        print(f"DEBUGGING ASIN [{i+1}/{len(variant_list)}]: {v_asin}")
        
        # Reset session setiap 2 request
        if i > 0 and i % 2 == 0:
            session = requests.Session()
            session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
        
        v_url = f"{BASE_URL}{v_asin}?th=1&psc=1"
        v_soup = get_soup(v_url, session)
        
        if v_soup == "CAPTCHA":
            print(f"      >>> [!] TERDETEKSI CAPTCHA PADA {v_asin}")
            continue

        if v_soup:
            title_el = v_soup.select_one("#productTitle")
            if title_el:
                # Ambil data satu per satu untuk diprint mentah

                product_name = title_el.get_text(strip=True)


                # IMPORTANT: gunakan v_soup (bukan soup)
                reviews = get_reviews_count(v_soup)

                upc = get_detail_by_label(v_soup, "UPC")
                manufacturer = get_detail_by_label(v_soup, "Manufacturer")
                asin_val = get_detail_by_label(v_soup, "ASIN") or v_asin  # fallback
                units = get_detail_by_label(v_soup, "Units")
                item_model_number = get_detail_by_label(v_soup, "Item model number")
                package_Dimensions = get_detail_by_label(v_soup, "Package Dimensions")
                calories = get_value_from_row_by_text(v_soup, "nic-nutrition-facts-energy", "Calories")
                serving_size = get_value_from_row_by_text(v_soup, "nic-nutrition-facts-serving-size", "Serving size")
                ingredients = get_ingredients(v_soup)
                legal_disclaimer = get_Legal_Disclaimer(v_soup)
                disclaimer = get_disclaimer(v_soup)
                image_url = get_main_image(v_soup)
                product_description = get_product_text(v_soup)
                stars = v_soup.select_one("#acrPopover span.a-size-small").get_text(strip=True) if v_soup.select_one("#acrPopover span.a-size-small") else None





                row = {
                    # "Category": category,
                    "Brand": get_product_value_universal(v_soup, "Brand"),
                    "Product Name": product_name,
                    "Product_url": v_url,
                    "Package Dimensions": package_Dimensions,
                    "Item Model Number": item_model_number,
                    "UPC": upc,
                    "Manufacturer": manufacturer,
                    "ASIN": asin_val,
                    "Units": units,
                    "Item Form": get_product_value_universal(v_soup, "Item Form"),

                    "Nutrition information Serving Size": serving_size,
                    "Calories": calories,

                    "Total Fat": get_nutrition_value(v_soup, "Total Fat"),
                    "Saturated Fat": get_nutrition_value(v_soup, "Saturated Fat"),
                    "Trans Fat": get_nutrition_value(v_soup, "Trans Fat"),
                    "Monounsaturated Fat": get_nutrition_value(v_soup, "Monounsaturated Fat"),
                    "Polyunsaturated Fat": get_nutrition_value(v_soup, "Polyunsaturated Fat"),
                    "Cholesterol": get_nutrition_value(v_soup, "Cholesterol"),
                    "Sodium": get_nutrition_value(v_soup, "Sodium"),
                    "Total Carbohydrate": get_nutrition_value(v_soup, "Total Carbohydrate"),
                    "Dietary Fiber": get_nutrition_value(v_soup, "Dietary Fiber"),
                    "Soluble Fiber": get_nutrition_value(v_soup, "Soluble Fiber"),
                    "Insoluble Fiber": get_nutrition_value(v_soup, "Insoluble Fiber"),
                    "Sugars": get_nutrition_value(v_soup, "Sugars"),
                    "Added Sugars": get_nutrition_value(v_soup, "Added Sugars"),
                    "Starch": get_nutrition_value(v_soup, "Starch"),
                    "Other Carbohydrate": get_nutrition_value(v_soup, "Other Carbohydrate"),
                    "Sugar Alcohol": get_nutrition_value(v_soup, "Sugar Alcohol"),
                    "Protein": get_nutrition_value(v_soup, "Protein"),
                    "Vitamin A": get_nutrition_value(v_soup, "Vitamin A"),
                    "Vitamin C": get_nutrition_value(v_soup, "Vitamin C"),
                    "Calcium": get_nutrition_value(v_soup, "Calcium"),
                    "Iron": get_nutrition_value(v_soup, "Iron"),
                    "Potassium": get_nutrition_value(v_soup, "Potassium"),

                    "Item Weight": get_product_value_universal(v_soup, "Item Weight"),
                    "Weight": get_product_value_universal(v_soup, "Weight"),
                    "Volume": get_product_value_universal(v_soup, "Volume"),
                    "Allergen Information": get_product_value_universal(v_soup, "Allergen Information"),
                    "Package Information": get_product_value_universal(v_soup, "Package Information"),
                    "Specialty": get_product_value_universal(v_soup, "Specialty"),
                    "Temperature Condition": get_product_value_universal(v_soup, "Temperature Condition"),
                    "Number of Pieces": get_product_value_universal(v_soup, "Number of Pieces"),
                    "Region of Origin": get_product_value_universal(v_soup, "Region of Origin"),
                    "Cuisine": get_product_value_universal(v_soup, "Cuisine"),
                    "Variety": get_product_value_universal(v_soup, "Variety"),
                    "Number of Items": get_product_value_universal(v_soup, "Number of Items"),
                    "Unit Count": get_product_value_universal(v_soup, "Unit Count"),
                    "Size": get_product_value_universal(v_soup, "Size"),

                    "Flavor": get_product_value_universal(v_soup, "Flavor"),
                    "Produce sold as": get_product_value_universal(v_soup, "Produce sold as"),

                    "Ingredients": ingredients,
                    "Legal Disclaimer": legal_disclaimer,
                    "Disclaimer": disclaimer,
                    "Product Description": product_description,
                    "Image Url": image_url,
                    "Reviews": reviews,
                    "Stars": stars
                }
                print(f"      ✅ Extracted data for ASIN {v_url}:")
                print(f"      ✅ Extracted data for Name {product_name}:")
                


                # ... setelah row = {...}
                write_row_csv(row, OUTPUT_CSV, FIELDNAMES)
                print(f"      ✅ Saved to CSV: {v_asin}")
        
        print("-" * 60)

if __name__ == "__main__":
    main()