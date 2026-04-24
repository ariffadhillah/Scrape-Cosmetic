import json
import re
import time
import random
import csv
import os
from bs4 import BeautifulSoup

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# KONFIGURASI UMUM
# =========================
namesave = 'Baby Care'
name_input = "daftar_Baby_Care_asin.csv"
BASE_URL = "https://www.amazon.com/dp/"
OUTPUT_CSV = f"{namesave}.csv"

FIELDNAMES = [
    "Main Category","Sub Category","Product Name","Product_url","Item Model Number","Package Dimensions","UPC","ASIN","Manufacturer","Units","Brand","Size","Flavor",
    "Item Weight","Specialty","Unit Count","Weight","Number of Items","Volume","Item Form","Allergen Information",
    "Cuisine","Variety","Temperature Condition","Number of Pieces","Package Information",
    "Produce sold as","Region of Origin",
    "Nutrition information Serving Size","Calories",
    "Total Fat","Saturated Fat","Trans Fat","Monounsaturated Fat","Polyunsaturated Fat","Cholesterol","Sodium",
    "Total Carbohydrate","Dietary Fiber","Soluble Fiber","Insoluble Fiber","Sugars","Added Sugars",
    "Starch","Other Carbohydrate","Sugar Alcohol","Protein","Vitamin A","Vitamin C","Calcium","Iron","Potassium",
    "Ingredients","Legal Disclaimer","Disclaimer","Product Description","Image Url","Reviews","Stars","Scent","Specific Uses For Product","Material Feature","Product Dimensions"
]

# =========================
# SELENIUM DRIVER SETUP
# =========================
def create_driver():
    options = Options()
    # options.add_argument("--headless") # Buka komentar ini jika ingin berjalan di background
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Menyamarkan Selenium agar tidak terdeteksi Amazon
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver

# =========================
# SEMUA FUNGSI EKSTRAKSI (DI-PERTAHANKAN)
# =========================


def load_asins_from_csv(path: str, asin_column: str = "ASIN") -> list[str]:
    if not os.path.exists(path):
        print(f"[!] File tidak ditemukan: {path}")
        return []

    asins = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        # Kalau file tidak punya header, DictReader akan gagal (fieldnames None)
        if reader.fieldnames is None:
            f.seek(0)
            raw = f.read()
            found = re.findall(r"\b[A-Z0-9]{10}\b", raw.upper())
            return list(dict.fromkeys(found))  # dedupe, keep order

        fieldnames_norm = [c.strip().lower() for c in reader.fieldnames if c]

        for row in reader:
            # 1) Prioritas: kolom ASIN jika ada
            asin_val = None
            if asin_column and asin_column.strip().lower() in fieldnames_norm:
                # cari key asli yang cocok (case-insensitive)
                for k in row.keys():
                    if k and k.strip().lower() == asin_column.strip().lower():
                        asin_val = row.get(k)
                        break

            # 2) Kalau tidak ada / kosong: scan seluruh value dalam row
            if asin_val and str(asin_val).strip():
                m = re.search(r"\b([A-Z0-9]{10})\b", str(asin_val).upper())
                if m:
                    asins.append(m.group(1))
                    continue

            for v in row.values():
                if not v:
                    continue
                m = re.search(r"\b([A-Z0-9]{10})\b", str(v).upper())
                if m:
                    asins.append(m.group(1))
                    break

    # dedupe preserve order
    return list(dict.fromkeys(asins))

def get_title(soup):
    # urutan dari yang paling umum -> fallback
    selectors = [
        "#productTitle",                          # paling umum
        "h1#title span#productTitle",             # variasi
        "h1#title span",                          # kadang title ada di span biasa
        "h1.a-size-large.a-spacing-none",         # template lain
        "#titleSection #title",                   # beberapa halaman lama
        "#centerCol #title",                      # fallback kasar
        "title",                                  # paling terakhir (tag <title>)
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            txt = el.get_text(" ", strip=True)
            txt = re.sub(r"\s+", " ", txt).strip()
            if txt:
                # kalau ambil dari <title>, biasanya ada "Amazon.com: ..."
                if sel == "title":
                    txt = re.sub(r"^Amazon\.com:\s*", "", txt).strip()
                    txt = re.sub(r"\s*:\s*Amazon\.com\s*$", "", txt).strip()
                return txt
    return None


def get_category_levels(soup):
    # beberapa kemungkinan container breadcrumb Amazon
    selector_candidates = [
        "#wayfinding-breadcrumbs_feature_div a",
        "#wayfinding-breadcrumbs_container a",
        "#wayfinding-breadcrumbs_feature_div ul.a-unordered-list a",
        "ul.a-unordered-list.a-horizontal.a-size-small a.a-link-normal.a-color-tertiary",
        "#wayfinding-breadcrumbs_feature_div li a.a-link-normal",
        "#wayfinding-breadcrumbs_container li a.a-link-normal",
    ]

    categories = []
    for sel in selector_candidates:
        anchors = soup.select(sel)
        if not anchors:
            continue

        tmp = []
        for a in anchors:
            t = a.get_text(" ", strip=True)
            if not t:
                continue
            # buang divider
            if t in {"›", ">"}:
                continue
            tmp.append(t)

        if tmp:
            categories = tmp
            break

    if not categories:
        return None, None

    main_category = categories[0]

    # gold rule: subcategory = sebelum terakhir (hindari variant paling spesifik)
    if len(categories) >= 3:
        sub_category = categories[-2]
    elif len(categories) >= 2:
        sub_category = categories[1]
    else:
        sub_category = None

    return main_category, sub_category

# =========================
# CLEANERS
# =========================
def _clean_label(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\u200e", " ").replace("\u200f", " ").replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"\s*:\s*$", "", s)
    return s

def _clean_value(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

# =========================
# ATTR EXTRACTION
# =========================
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

# =========================
# NUTRITION + OTHERS
# =========================
def get_product_text(soup):
    container_ = soup.find("div", id="productDescription")
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
    num = re.search(r"[\d,]+", text)
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

# def get_ingredients(soup):
#     container = soup.find("div", id="important-information")
#     if not container:
#         return None
#     header = container.find("span", string=lambda s: s and "Ingredients" in s.lower())
#     if not header:
#         return None
#     for p in header.find_all_next("p"):
#         if container not in p.parents:
#             break
#         text = p.get_text(strip=True)
#         if text:
#             return text
#     return None

import re

def get_ingredients(soup):
    container = soup.find("div", id="important-information")
    if not container:
        return None
    
    # 1. Cari header "Ingredients"
    header = container.find(["h4", "span", "h2","h3"], string=re.compile(r'Ingredients', re.I))
    
    if not header:
        return None

    # 2. Cari semua tag <p> SETELAH header tersebut
    # Kita cari yang teksnya tidak kosong (strip=True)
    next_ps = header.find_all_next("p")
    
    for p in next_ps:
        # Pastikan kita masih di dalam container yang sama
        if container not in p.parents:
            break
            
        text = p.get_text(strip=True)
        if text:  # Jika teks tidak kosong, ini adalah ingredient-nya
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


def get_all_variant_asins(soup):
    asins = set()
    scripts = soup.find_all("script", type="text/javascript")
    for script in scripts:
        content = script.string
        if content and "colorToAsin" in content:
            match = re.search(r"jQuery\.parseJSON\('(.+?)'\)", content)
            if match:
                try:
                    raw_json = match.group(1).replace("\\'", "'").encode().decode("unicode_escape")
                    data = json.loads(raw_json)
                    for key in data.get("colorToAsin", {}):
                        v_asin = data["colorToAsin"][key].get("asin")
                        if v_asin:
                            asins.add(v_asin)
                except Exception:
                    pass
    return list(asins)


def write_row_safe(writer, row: dict):
    safe = {}
    for k in FIELDNAMES:
        v = row.get(k, "")
        if isinstance(v, str): v = v.replace("\r", " ").replace("\n", " ").strip()
        safe[k] = v
    writer.writerow(safe)

# =========================
# UTILS (FILE LOADING)
# =========================
def load_asins_from_csv(path: str, asin_column: str = "ASIN") -> list[str]:
    if not os.path.exists(path): return []
    asins = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            f.seek(0)
            return list(dict.fromkeys(re.findall(r"\b[A-Z0-9]{10}\b", f.read().upper())))
        for row in reader:
            for v in row.values():
                m = re.search(r"\b([A-Z0-9]{10})\b", str(v).upper())
                if m: asins.append(m.group(1)); break
    return list(dict.fromkeys(asins))

def log_failed_asin(asin: str):
    failed_file = f"gagal_{namesave}-1.csv"
    exists = os.path.exists(failed_file)
    with open(failed_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists: writer.writerow(["ASIN"])
        writer.writerow([asin])

# =========================
# CORE LOGIC (SELENIUM REPLACES REQUESTS)
# =========================
def get_soup_via_selenium(driver, url):
    try:
        driver.get(url)
        # Tunggu sebentar agar JS render (3-6 detik)
        time.sleep(random.uniform(4, 7))
        
        # Scroll sedikit untuk memicu pemuatan elemen malas (lazy loading)
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(1)

        html = driver.page_source
        if "robot check" in html.lower() or "captcha" in html.lower():
            print("   [!] Terdeteksi CAPTCHA. Selesaikan di browser atau tunggu...")
            time.sleep(10) # Beri waktu user selesaikan manual jika tidak headless
            html = driver.page_source
            
        return BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"   [!] Gagal memuat URL: {e}")
        return None


def process_seed_asin(driver, seed_asin: str, writer, processed_asins: set):
    print(f"\n=== SEED ASIN: {seed_asin} ===")
    first_soup = get_soup_via_selenium(driver, f"{BASE_URL}{seed_asin}")
    
    if not first_soup:
        log_failed_asin(seed_asin)
        return

    variant_list = get_all_variant_asins(first_soup)
    if not variant_list: variant_list = [seed_asin]
    elif seed_asin not in variant_list: variant_list.insert(0, seed_asin)

    for i, v_asin in enumerate(variant_list):
        if v_asin in processed_asins: continue

        print(f"   -> [{i+1}/{len(variant_list)}] {v_asin}")
        v_soup = get_soup_via_selenium(driver, f"{BASE_URL}{v_asin}")
        
        if not v_soup:
            log_failed_asin(v_asin)
            continue

        # --- EKSTRAKSI DATA MENGGUNAKAN FUNGSI ASLI ANDA ---
        product_name = get_title(v_soup)
        if not product_name: continue

        # (Logika mapping row Anda tetap sama)
        _, seed_sub = get_category_levels(first_soup)
        _, sub_category = get_category_levels(v_soup)


        reviews = get_reviews_count(v_soup)
        upc = get_detail_by_label(v_soup, "UPC")
        manufacturer = get_detail_by_label(v_soup, "Manufacturer")
        asin_val = get_detail_by_label(v_soup, "ASIN") or v_asin
        units = get_detail_by_label(v_soup, "Units")
        # best_sellers_rank = get_detail_by_label(v_soup, "Best Sellers Rank")
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
            "Main Category": f"{namesave}",
            "Sub Category": sub_category,
            "Brand": get_product_value_universal(v_soup, "Brand"),
            "Product Name": product_name,
            "Product_url": f"{BASE_URL}{v_asin}",
            "Package Dimensions": package_Dimensions,
            "Item Model Number": item_model_number,
            "UPC": upc,
            "Manufacturer": manufacturer,
            "ASIN": asin_val,
            "Units": units,
            # "Best Sellers Rank": best_sellers_rank,
            "Item Form": get_product_value_universal(v_soup, "Item Form"),
            "Scent": get_product_value_universal(v_soup, "Scent"),
            "Specific Uses For Product": get_product_value_universal(v_soup, "Specific Uses For Product"),
            "Material Feature": get_product_value_universal(v_soup, "Material Feature"),
            "Product Dimensions": get_product_value_universal(v_soup, "Product Dimensions"),

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

        # Tambahkan sisa field nutrition yang Anda miliki di sini...
        # ... (Sama persis dengan kode lama Anda) ...

        write_row_safe(writer, row)
        processed_asins.add(v_asin)
        print(f"      ✅ Saved: {v_asin}")

def main():
    seed_asins = load_asins_from_csv(f"{name_input}")
    if not seed_asins: return

    driver = create_driver()
    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    processed_asins = set()

    try:
        with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if not file_exists: writer.writeheader()

            for idx, asin in enumerate(seed_asins, start=1):
                print(f"\nBULK [{idx}/{len(seed_asins)}] -> {asin}")
                process_seed_asin(driver, asin, writer, processed_asins)

    finally:
        driver.quit()
        print("\nDONE. Output:", OUTPUT_CSV)

if __name__ == "__main__":
    main()