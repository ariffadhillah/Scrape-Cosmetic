# from csv_manager import CSVManager
# csv_manager = CSVManager()

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import os
import csv

BASE_URL = "https://www.amazon.com/dp/"


OUTPUT_CSV = "amazon_products-utama.csv"

FIELDNAMES = [
    "Category","Brand","Product Name","Product_url","Package Dimensions", "Item Model Number","UPC","Manufacturer","ASIN","Units","Item Form","Item Weight","Number of Items","Unit Count","Weight","Volume","Allergen Information",
    "Specialty","Cuisine","Flavor",
    "Variety","Temperature Condition","Number of Pieces","Package Information","Size",
    "Produce sold as","Region of Origin","Nutrition information Serving Size","Calories",
    "Total Fat","Saturated Fat","Trans Fat","Monounsaturated Fat","Polyunsaturated Fat","Cholesterol","Sodium",
    "Total Carbohydrate","Dietary Fiber","Soluble Fiber","Insoluble Fiber","Sugars","Added Sugars",
    "Starch","Other Carbohydrate","Sugar Alcohol","Protein","Vitamin A","Vitamin C","Calcium","Iron","Potassium",
    "Ingredients","Legal Disclaimer","Disclaimer","Product Description","Image Url","Reviews","Stars"
]

def _clean_row_for_csv(row: dict) -> dict:
    # pastikan semua key ada + None jadi string kosong
    return {k: (row.get(k) if row.get(k) is not None else "") for k in FIELDNAMES}

def append_row_to_csv(row: dict, filename: str = OUTPUT_CSV):
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

        if not file_exists:
            writer.writeheader()

        writer.writerow(_clean_row_for_csv(row))
        f.flush()


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"
]






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

    # A) th/td tables (product details / tech spec / general keyvalue)
    for row in soup.select("table tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            put(th.get_text(" ", strip=True), td.get_text(" ", strip=True))

    # B) old td/td table
    for row in soup.select("table.a-normal.a-spacing-micro tr"):
        tds = row.find_all("td")
        if len(tds) >= 2:
            put(tds[0].get_text(" ", strip=True), tds[1].get_text(" ", strip=True))

    # C) detail bullets (span.a-text-bold + value)
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

    # D) productOverview_feature_div (kadang Amazon pakai ini)
    for row in soup.select("#productOverview_feature_div tr"):
        tds = row.find_all(["td", "th"])
        if len(tds) >= 2:
            put(tds[0].get_text(" ", strip=True), tds[1].get_text(" ", strip=True))

    return attrs

def get_product_value_universal(soup, label):
    attrs = extract_amazon_attributes(soup)

    # synonyms biar "Weight" ketemu walau labelnya beda
    key = _clean_label(label)
    synonyms = {
        "weight": ["weight", "item weight", "package weight", "shipping weight", "net weight", "product weight"],
        "volume": ["volume", "item volume", "package volume"],
        "ingredient type": ["ingredient type", "ingredients", "ingredient", "special ingredients"],
        "cuisine": ["cuisine", "cuisine type"],
        "specialty": ["specialty", "speciality", "diet type", "dietary information"],
    }

    candidates = synonyms.get(key, [key])

    # exact lookup dulu
    for c in candidates:
        c = _clean_label(c)
        if c in attrs:
            return attrs[c]

    # fallback: contains match
    for k, v in attrs.items():
        for c in candidates:
            c = _clean_label(c)
            if c in k or k in c:
                return v

    return None





# Berikan nilai default = None
def get_product_text(soup, label=None):    
    container_ = soup.find('div', id='productDescription')
    
    if container_:
        return container_.get_text(strip=True)
    
    return None

# ==========================================
# FUNGSI-FUNGSI TAMBAHAN ANDA
# ==========================================

# def get_product_table_value(soup, label):

#     tables = soup.find_all("table", class_="a-normal a-spacing-micro")

#     for table in tables:
#         for row in table.find_all("tr"):

#             cells = row.find_all("td")
#             if len(cells) < 2:
#                 continue

#             name = cells[0].get_text(strip=True)
#             value = cells[1].get_text(strip=True)

#             if name.lower() == label.lower():
#                 return value

#     return None


# def get_product_table_value(soup, label):
#     label = label.lower().strip()

#     # ---------- 1️⃣ Cari di table lama (td - td) ----------
#     tables1 = soup.find_all("table", class_="a-normal a-spacing-micro")

#     for table in tables1:
#         for row in table.find_all("tr"):
#             cells = row.find_all("td")
#             if len(cells) >= 2:
#                 name = cells[0].get_text(strip=True).lower()
#                 value = cells[1].get_text(strip=True)

#                 if name == label:
#                     return value

#     # ---------- 2️⃣ Cari di productDetails table (th - td) ----------
#     tables2 = soup.find_all("table", class_="prodDetTable")

#     for table in tables2:
#         for row in table.find_all("tr"):
#             th = row.find("th")
#             td = row.find("td")

#             if th and td:
#                 name = th.get_text(strip=True).lower()
#                 value = td.get_text(strip=True)

#                 if name == label:
#                     return value

#     return None


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

def get_price(soup):
    selectors = [
        "#corePriceDisplay_desktop_feature_div span.a-price span.a-offscreen",
        "#corePrice_feature_div span.a-price span.a-offscreen",
        "#apex_desktop span.a-price span.a-offscreen",
        "span.a-price span.a-offscreen"
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el: return el.get_text(strip=True)
    return None


# def get_price(soup):

#     selectors = [
#         "#corePriceDisplay_desktop_feature_div span.a-price span.a-offscreen",
#         "#corePrice_feature_div span.a-price span.a-offscreen",
#         "#apex_desktop span.a-price span.a-offscreen",
#         "span.a-price span.a-offscreen"
#     ]

#     for sel in selectors:
#         el = soup.select_one(sel)
#         if el:
#             return el.get_text(strip=True)

#     return None



# ==========================================
# REQUEST
# ==========================================

def get_soup(url, session):

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        time.sleep(random.uniform(5, 10))

        response = session.get(url, headers=headers, timeout=30)

        if response.status_code == 200:

            if "sorry, we just need to make sure you're not a robot" in response.text.lower():
                return "CAPTCHA", response.text

            return BeautifulSoup(response.text, "html.parser"), response.text

        return None, response.text

    except Exception as e:
        print("[!] Request Error:", e)
        return None, ""


# ==========================================
# PARSE VARIANTS
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
                        if v_asin:
                            asins.add(v_asin)

                except:
                    pass

    return list(asins)


# ==========================================
# EXTRACT BASIC DATA
# ==========================================

def extract_details(soup):

    data = {}

    title = soup.select_one("#productTitle")
    data['name'] = title.get_text(strip=True) if title else "N/A"

    price_el = (
        soup.select_one("#corePriceDisplay_desktop_feature_div span.a-offscreen")
        or soup.select_one("#corePrice_feature_div span.a-offscreen")
        or soup.select_one("span.a-price span.a-offscreen")
    )

    data['price'] = price_el.get_text(strip=True) if price_el else "Out of Stock / No Price"

    return data


def save_debug_file(asin, content):

    filename = f"debug_{asin}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return filename


# ==========================================
# CORE FUNCTION → DIPAKAI MAIN
# ==========================================

# def process_asin(target_asin):
def process_asin(target_asin, category=None):

    # print(f"\n--- PROCESS ASIN: {target_asin} ---")


    print(f"\n--- PROCESS ASIN: {target_asin} ---")
    if category:
        print("CATEGORY:", category)

    session = requests.Session()

    soup, raw_html = get_soup(f"{BASE_URL}{target_asin}", session)

    if soup == "CAPTCHA":
        print("Captcha detected:", target_asin)
        return

    if not soup:
        print("Load gagal:", target_asin)
        return

    variant_list = get_all_variant_asins(soup)

    if not variant_list:
        variant_list = [target_asin]
        print("Tidak ada varian → ASIN tunggal")
    else:
        print(f"Ditemukan {len(variant_list)} varian")

    for i, v_asin in enumerate(variant_list, 1):

        print(f"[{i}/{len(variant_list)}] {v_asin}")

        # reset session tiap 2 request
        if i > 1 and i % 2 == 0:
            session = requests.Session()
            print("   reset session")

        v_url = f"{BASE_URL}{v_asin}?th=1&psc=1"

        v_soup, v_raw = get_soup(v_url, session)

        if v_soup:
            # Menggunakan multiple selector agar meminimalkan 'Not Found'
            title_tag = v_soup.select_one("#productTitle") or v_soup.select_one(".qa-title-text")
            
            if title_tag:
                # Ambil Semua Data Berdasarkan Fungsi Anda
                product_name = title_tag.get_text(strip=True)
                reviews = get_reviews_count(soup)


                # item_weight = get_detail_by_label(soup, "Item Weight")
                upc = get_detail_by_label(soup, "UPC")
                manufacturer = get_detail_by_label(soup, "Manufacturer")
                asin_val = get_detail_by_label(soup, "ASIN")
                units = get_detail_by_label(soup, "Units")
                item_model_number = get_detail_by_label(soup, "Item model number")
                package_Dimensions = get_detail_by_label(soup, "Package Dimensions")
                calories = get_value_from_row_by_text(soup,"nic-nutrition-facts-energy","Calories")
                serving_size = get_value_from_row_by_text(soup,"nic-nutrition-facts-serving-size","Serving size")
                ingredients = get_ingredients(soup)
                legal_disclaimer = get_Legal_Disclaimer(soup)
                disclaimer = get_disclaimer(soup)
                price = get_price(soup)
                image_url = get_main_image(soup)
                product_description = get_product_text(soup)
                stars = soup.select_one("#acrPopover span.a-size-small").get_text(strip=True) if soup.select_one("#acrPopover span.a-size-small") else None
                

                row = {
                    "Category": category,
                    "Brand": get_product_value_universal(soup, "Brand"),
                    "Product Name": product_name,
                    "Product_url": v_url,
                    "Package Dimensions": package_Dimensions,
                    "Item Model Number": item_model_number,
                    "UPC": upc,
                    "Manufacturer": manufacturer,
                    "ASIN": asin_val,
                    "Units": units,
                    "Item Form": get_product_value_universal(soup, "Item Form"),

                    "Nutrition information Serving Size": serving_size,
                    "Calories": calories,

                    "Total Fat": get_nutrition_value(soup, "Total Fat"),
                    "Saturated Fat": get_nutrition_value(soup, "Saturated Fat"),
                    "Trans Fat": get_nutrition_value(soup, "Trans Fat"),
                    "Monounsaturated Fat": get_nutrition_value(soup, "Monounsaturated Fat"),
                    "Polyunsaturated Fat": get_nutrition_value(soup, "Polyunsaturated Fat"),
                    "Cholesterol": get_nutrition_value(soup, "Cholesterol"),
                    "Sodium": get_nutrition_value(soup, "Sodium"),
                    "Total Carbohydrate": get_nutrition_value(soup, "Total Carbohydrate"),
                    "Dietary Fiber": get_nutrition_value(soup, "Dietary Fiber"),
                    "Soluble Fiber": get_nutrition_value(soup, "Soluble Fiber"),
                    "Insoluble Fiber": get_nutrition_value(soup, "Insoluble Fiber"),
                    "Sugars": get_nutrition_value(soup, "Sugars"),
                    "Added Sugars": get_nutrition_value(soup, "Added Sugars"),
                    "Starch": get_nutrition_value(soup, "Starch"),
                    "Other Carbohydrate": get_nutrition_value(soup, "Other Carbohydrate"),
                    "Sugar Alcohol": get_nutrition_value(soup, "Sugar Alcohol"),
                    "Protein": get_nutrition_value(soup, "Protein"),
                    "Vitamin A": get_nutrition_value(soup, "Vitamin A"),
                    "Vitamin C": get_nutrition_value(soup, "Vitamin C"),
                    "Calcium": get_nutrition_value(soup, "Calcium"),
                    "Iron": get_nutrition_value(soup, "Iron"),
                    "Potassium": get_nutrition_value(soup, "Potassium"),
                    
                    "Item Weight": get_product_value_universal(soup, "Item Weight"),
                    "Weight": get_product_value_universal(soup, "Weight"),
                    "Volume": get_product_value_universal(soup, "Volume"),
                    "Allergen Information": get_product_value_universal(soup, "Allergen Information"),
                    "Package Information": get_product_value_universal(soup, "Package Information"),
                    "Specialty": get_product_value_universal(soup, "Specialty"),
                    "Temperature Condition": get_product_value_universal(soup, "Temperature Condition"),
                    "Number of Pieces": get_product_value_universal(soup, "Number of Pieces"),
                    "Region of Origin": get_product_value_universal(soup, "Region of Origin"),
                    "Cuisine": get_product_value_universal(soup, "Cuisine"),
                    "Variety": get_product_value_universal(soup, "Variety"),
                    "Number of Items": get_product_value_universal(soup, "Number of Items"),
                    "Unit Count": get_product_value_universal(soup, "Unit Count"),
                    "Size": get_product_value_universal(soup, "Size"),

                    "Flavor": get_product_value_universal(soup, "Flavor"),
                    "Produce sold as": get_product_value_universal(soup, "Produce sold as"),

                    "Ingredients": ingredients,
                    "Legal Disclaimer": legal_disclaimer,
                    "Disclaimer": disclaimer,
                    "Product Description": product_description,
                    "Image Url": image_url,
                    "Reviews": reviews,
                    "Stars": stars
                    
                }
                append_row_to_csv(row)
                print("✅ saved:", asin_val)


                print("-" * 30)



        else:
            print("   REQUEST FAILED")

        print("-" * 40)


# ==========================================
# STANDALONE TEST
# ==========================================

# if __name__ == "__main__":

#     # untuk testing manual
#     TEST_ASIN = "B09DS5J8F9"

#     process_asin(TEST_ASIN)


# (env) PS E:\Scraping\Weather Station Metadata\Doctor\unrealbali\logo\new> py .\index.py
# E:\Scraping\Weather Station Metadata\env\lib\site-packages\PIL\Image.py:1034: UserWarning: Palette images with Transparency expressed in bytes should be converted to RGBA images
#   warnings.warn(
# ✅ processed Hijau LOFTS
# ✅ processed UBR993
# ✅ processed UR0255
# ✅ processed UR0301
# ✅ processed UR0302
# ✅ processed UR0303
# ✅ processed UR0304
# ✅ processed UR0305




# ✅ processed UBR993
# ✅ processed UR0255
# ✅ processed UR0301
# ✅ processed UR0302
# ✅ processed UR0303
# ✅ processed UR0304
# ✅ processed UR0305
# ✅ processed UR0309
# ✅ processed UR0311
# ✅ processed UR0312
# ✅ processed UR0318
# ✅ processed UR0319
# ✅ processed UR0320
# ✅ processed UR0322
# ✅ processed UR0325
# ✅ processed UR0329
# ✅ processed UR0336
# ✅ processed UR0343
# ✅ processed UR0344
# ✅ processed UR0345
# ✅ processed UR0346
# ✅ processed UR0350
# ✅ processed UR0351
# ✅ processed UR0352
# ✅ processed UR0353
# ✅ processed UR0354
# ✅ processed UR0355
# ✅ processed UR0356
# ✅ processed UR0357
# ✅ processed UR0358
# ✅ processed UR0359
# ✅ processed UR0361
# ✅ processed UR0362
# ✅ processed UR0370
# ✅ processed UR0374
# ✅ processed UR0375
# ✅ processed UR0376
# ✅ processed UR0377
# ✅ processed UR0398
# ✅ processed UR0399
# ✅ processed UR0408
# ✅ processed UR0410
# ✅ processed UR0428
# ✅ processed UR0429
# ✅ processed UR0449
# ✅ processed UR0451
# ✅ processed UR0459
# ✅ processed UR0473
# ✅ processed UR0476
# ✅ processed UR0477
# ✅ processed UR0479
# ✅ processed UR0485
# ✅ processed UR0489
# ✅ processed UR0490
# ✅ processed UR0501
# ✅ processed UR0502
# ✅ processed UR0503
# ✅ processed UR0504
# ✅ processed UR0507
# ✅ processed UR0510
# ✅ processed UR0511
# ✅ processed UR0514
# ✅ processed UR0515
# ✅ processed UR0516
# ✅ processed UR0517
# ✅ processed UR0520
# ✅ processed UR0521
# ✅ processed UR0522
# ✅ processed UR0527
# ✅ processed UR0530
# ✅ processed UR0536
# ✅ processed UR0538
# ✅ processed UR0539
# ✅ processed UR0541
# ✅ processed UR0542
# ✅ processed UR0544
# ✅ processed UR0546
# ✅ processed UR0547
# ✅ processed UR0548
# ✅ processed UR0549
# ✅ processed UR0551
# ✅ processed UR0553
# ✅ processed UR0554
# ✅ processed UR0555
# ✅ processed UR0556
# ✅ processed UR0558
# ✅ processed UR0559
# ✅ processed UR0560
# ✅ processed UR0564
# ✅ processed UR0565
# ✅ processed UR0567
# ✅ processed UR0568
# ✅ processed UR0570
# ✅ processed UR0572
# ✅ processed UR0573
# ✅ processed UR0574
# ✅ processed UR0575
# ✅ processed UR0577
# ✅ processed UR0578
# ✅ processed UR0579
# ✅ processed UR0580
# ✅ processed UR0581
# ✅ processed UR0582
# ✅ processed UR0583
# ✅ processed UR0584
# ✅ processed UR0585
# ✅ processed UR0586
# ✅ processed UR0589
# ✅ processed UR0590
# ✅ processed UR0591
# ✅ processed UR0592
# ✅ processed UR0594
# ✅ processed UR0595
# ✅ processed UR0597
# ✅ processed UR0599
# ✅ processed UR0601
# ✅ processed UR06011
# ✅ processed UR0602
# ✅ processed UR06022
# ✅ processed UR0603
# ✅ processed UR0611
# ✅ processed UR0696
# ✅ processed UR0698
# ✅ processed UR0700
# ✅ processed UR0701
# ✅ processed UR0702
# ✅ processed UR0703
# ✅ processed UR0704
# ✅ processed UR0705
# ✅ processed UR0706
# ✅ processed UR0708
# ✅ processed UR0709
# ✅ processed UR0711
# ✅ processed UR0712
# ✅ processed UR0713
# ✅ processed UR0714
# ✅ processed UR0715
# ✅ processed UR0716
# ✅ processed UR0717
# ✅ processed UR0718
# ✅ processed UR0719
# ✅ processed UR0720
# ✅ processed UR0722
# ✅ processed UR0723
# ✅ processed UR0724
# ✅ processed UR0725
# ✅ processed UR0726
# ✅ processed UR0727
# ✅ processed UR0728
# ✅ processed UR0729
# ✅ processed UR0730
# ✅ processed UR0732
# ✅ processed UR0750
# ✅ processed UR0751
# ✅ processed UR0752
# ✅ processed UR0756
# ✅ processed UR0801
# ✅ processed UR0802
# ✅ processed UR0803
# ✅ processed UR0805
# ✅ processed UR0888
# ✅ processed UR0889
# ✅ processed UR0912
# ✅ processed UR0922
# ✅ processed UR0945
# ✅ processed UR0946
# ✅ processed UR0986
# ✅ processed UR0987
# ✅ processed UR0989
# ✅ processed UR0995
# ✅ processed UR0998
# ✅ processed UR0999
# ✅ processed UR1003
# ✅ processed UR1004
# ✅ processed UR1006
# ✅ processed UR1010
# ✅ processed UR1011
# ✅ processed UR1012
# ✅ processed UR1023
# ✅ processed UR1026
# ✅ processed UR1028
# ✅ processed UR1029
# ✅ processed UR1030
# ✅ processed UR1032
# ✅ processed UR1033
# ✅ processed UR1034
# ✅ processed UR1035
# ✅ processed UR1036
# ✅ processed UR1037
# ✅ processed UR1038
# ✅ processed UR1039
# ✅ processed UR1042
# ✅ processed UR1043
# ✅ processed UR1044
# ✅ processed UR1045
# ✅ processed UR1100
# ✅ processed UR1101
# ✅ processed UR1500
# ✅ processed UR1501
# ✅ processed UR2000
# ✅ processed UR2001
# ✅ processed UR2002
# ✅ processed UR2003
# ✅ processed UR2004
# ✅ processed UR2005
# ✅ processed UR2006
# ✅ processed UR2007
# ✅ processed UR2008
# ✅ processed UR2010
# ✅ processed UR2011
# ✅ processed UR2012
# ❌ Failed processing UR2013/UR2013_7.jpg -> cannot identify image file 'images\\UR2013\\UR2013_7.jpg'
# ✅ processed UR2013
# ✅ processed UR2014
# ✅ processed UR2015
# ✅ processed UR2016
# ✅ processed UR2018
# ✅ processed UR2019
# ✅ processed UR2021
# ✅ processed UR2022
# ✅ processed UR2023
# ✅ processed UR2028
# ✅ processed UR2029
# ✅ processed UR2030
# ✅ processed UR2031
# ✅ processed UR2035
# ✅ processed UR2036
# ✅ processed UR2038
# ✅ processed UR2039
# ✅ processed UR2040
# ✅ processed UR2041
# ✅ processed UR2042
# ✅ processed UR2043
# ✅ processed UR2045
# ✅ processed UR2046
# ✅ processed UR2047
# ✅ processed UR2048
# ✅ processed UR2049
# ✅ processed UR2050
# ✅ processed UR2051
# ✅ processed UR2052
# ✅ processed UR2053
# ✅ processed UR2054A
# ✅ processed UR2054B
# ✅ processed UR2055A
# ✅ processed UR2055B
# ✅ processed UR2056
# ✅ processed UR2057
# ✅ processed UR2058
# ✅ processed UR2059
# ✅ processed UR2060
# ✅ processed UR2061
# ✅ processed UR2062
# ✅ processed UR2063
# ✅ processed UR2067
# ✅ processed UR2068
# ✅ processed UR2069
# ✅ processed UR2070
# ✅ processed UR2071
# ✅ processed UR2072
# ✅ processed UR2073
# ✅ processed UR2075
# ✅ processed UR2076
# ✅ processed UR2077
# ✅ processed UR2078
# ✅ processed UR2083
# ✅ processed UR2086
# ✅ processed UR2088
# ✅ processed UR2092
# ✅ processed UR3034
# ✅ processed UR518
# ✅ processed URB 995
# ✅ processed URB0001
# ✅ processed URB0002
# ✅ processed URB0003
# ✅ processed URB0004
# ✅ processed URB0005
# ✅ processed URB0006
# ✅ processed URB0007
# ✅ processed URB0008
# ✅ processed URB0009
# ✅ processed URB0010
# ✅ processed URB0011
# ✅ processed URB0012
# ✅ processed URB0016
# ✅ processed URB0017
# ✅ processed URB0018
# ✅ processed URB0019
# ✅ processed URB0020
# ✅ processed URB0021
# ✅ processed URB0022
# ✅ processed URB0023
# ✅ processed URB0024
# ✅ processed URB0026
# ✅ processed URB0027
# ✅ processed URB0028
# ✅ processed URB0029
# ✅ processed URB0030
# ✅ processed URB0031
# ✅ processed URB0033
# ✅ processed URB0034
# ✅ processed URB0036
# ✅ processed URB0037
# ✅ processed URB0038
# ✅ processed URB0040
# ✅ processed URB0041
# ✅ processed URB0042
# ✅ processed URB0043
# ✅ processed URB0044
# ✅ processed URB0045
# ✅ processed URB0046
# ✅ processed URB0047
# ✅ processed URB0048
# ✅ processed URB0049
# ✅ processed URB0050
# ✅ processed URB0051
# ✅ processed URB0052
# ✅ processed URB0053
# ✅ processed URB0054
# ✅ processed URB0055
# ✅ processed URB0056
# ✅ processed URB0057
# ✅ processed URB0058
# ✅ processed URB0060
# ✅ processed URB0061
# ✅ processed URB0063
# ✅ processed URB0064
# ✅ processed URB0065
# ✅ processed URB0066
# ✅ processed URB0067
# ✅ processed URB0068
# ✅ processed URB0069
# ✅ processed URB0070
# ✅ processed URB0071
# ✅ processed URB0072
# ✅ processed URB0073
# ✅ processed URB0074
# ✅ processed URB0075
# ✅ processed URB0076
# ✅ processed URB0077
# ✅ processed URB0078
# ✅ processed URB0079
# ✅ processed URB0080
# ✅ processed URB0081
# ✅ processed URB0082
# ✅ processed URB0083
# ✅ processed URB0084
# ✅ processed URB0085
# ✅ processed URB0086
# ✅ processed URB0088
# ✅ processed URB0090
# ✅ processed URB0091
# ✅ processed URB0092
# ✅ processed URB0093
# ✅ processed URB0094
# ✅ processed URB0095
# ✅ processed URB0096
# ✅ processed URB0097
# ✅ processed URB0098
# ✅ processed URB0099
# ✅ processed URB0100
# ✅ processed URB0101
# ✅ processed URB0102
# ✅ processed URB0103
# ✅ processed URB0104
# ✅ processed URB0105
# ✅ processed URB0106
# ✅ processed URB0107
# ✅ processed URB0108
# ✅ processed URB0109
# ✅ processed URB0110
# ✅ processed URB0111
# ✅ processed URB0112
# ✅ processed URB0113
# ✅ processed URB0115
# ✅ processed URB0116
# ✅ processed URB0117
# ✅ processed URB0118
# ✅ processed URB0119
# ✅ processed URB0120
# ✅ processed URB0121
# ✅ processed URB0122
# ✅ processed URB0123
# ✅ processed URB0124
# ✅ processed URB0125
# ✅ processed URB0126
# ✅ processed URB0127
# ✅ processed URB0128
# ✅ processed URB0129
# ✅ processed URB0130
# ✅ processed URB0131
# ✅ processed URB0132
# ✅ processed URB0133
# ✅ processed URB0134
# ✅ processed URB0135
# ✅ processed URB0136
# ✅ processed URB0137
# ✅ processed URB0138
# ✅ processed URB0139
# ✅ processed URB0140
# ✅ processed URB0141
# ✅ processed URB0142
# ✅ processed URB0143
# ✅ processed URB0144
# ✅ processed URB0145
# ✅ processed URB0146
# ✅ processed URB0147
# ✅ processed URB0148
# ✅ processed URB0149
# ✅ processed URB0150
# ✅ processed URB0156
# ✅ processed URB0157
# ✅ processed URB0158
# ✅ processed URB0159
# ✅ processed URB0160
# ✅ processed URB0161
# ✅ processed URB0162
# ✅ processed URB0163
# ✅ processed URB0164
# ✅ processed URB0165
# ✅ processed URB0166
# ✅ processed URB0167
# ✅ processed URB0169
# ✅ processed URB0170
# ✅ processed URB0171
# ✅ processed URB0172
# ✅ processed URB0173
# ✅ processed URB0175
# ✅ processed URB0177
# ✅ processed URB0178
# ✅ processed URB0179
# ✅ processed URB0180
# ✅ processed URB0181
# ✅ processed URB0182
# ✅ processed URB0183
# ✅ processed URB0184
# ✅ processed URB0185
# ✅ processed URB0186
# ✅ processed URB0187
# ✅ processed URB0188
# ✅ processed URB0189
# ✅ processed URB0190
# ✅ processed URB0191
# ✅ processed URB0192
# ✅ processed URB0193
# ✅ processed URB0194
# ✅ processed URB0195
# ✅ processed URB0196
# ✅ processed URB0197
# ✅ processed URB0198
# ✅ processed URB0199
# ✅ processed URB0200
# ✅ processed URB1000
# ✅ processed URB1001
# ✅ processed URB1002
# ✅ processed URB1003
# ✅ processed URB201
# ✅ processed URB202
# ✅ processed URB203
# ✅ processed URB204
# ✅ processed URB205
# ✅ processed URB206
# ✅ processed URB207
# ✅ processed URB208
# ✅ processed URB209
# ✅ processed URB210
# ✅ processed URB211
# ✅ processed URB212
# ✅ processed URB213
# ✅ processed URB214
# ✅ processed URB215
# ✅ processed URB216
# ✅ processed URB217
# ✅ processed URB218
# ✅ processed URB219
# ✅ processed URB220
# ✅ processed URB221
# ✅ processed URB222
# ✅ processed URB223
# ✅ processed URB224
# ✅ processed URB225
# ✅ processed URB226
# ✅ processed URB227
# ✅ processed URB228
# ✅ processed URB229
# ✅ processed URB230
# ✅ processed URB231
# ✅ processed URB232
# ✅ processed URB233
# ✅ processed URB234
# ✅ processed URB235
# ✅ processed URB236
# ✅ processed URB237
# ✅ processed URB238
# ✅ processed URB239
# ✅ processed URB240
# ✅ processed URB241
# ✅ processed URB242
# ✅ processed URB243
# ✅ processed URB244
# ✅ processed URB245
# ✅ processed URB246
# ✅ processed URB247
# ✅ processed URB248
# ✅ processed URB249
# ✅ processed URB9000
# ✅ processed URB9001
# ✅ processed URB9003
# ✅ processed URB9004
# ✅ processed URB9005
# ✅ processed URB9007
# ✅ processed URB9008
# ✅ processed URB9009
# ✅ processed URB901
# ✅ processed URB902
# ✅ processed URB904
# ✅ processed URB905
# ✅ processed URB907
# ✅ processed URB908
# ✅ processed URB909
# ✅ processed URB910
# ✅ processed URB912
# ✅ processed URB913
# ✅ processed URB914
# E:\Scraping\Weather Station Metadata\env\lib\site-packages\PIL\Image.py:3451: DecompressionBombWarning: Image size (96548782 pixels) exceeds limit of 89478485 pixels, could be decompression bomb DOS attack.
#   warnings.warn(
# ✅ processed URB915
# ✅ processed URB916
# ✅ processed URB917
# ✅ processed URB918
# ✅ processed URB919
# ✅ processed URB920
# ✅ processed URB921
# ✅ processed URB922
# ✅ processed URB923
# ✅ processed URB924
# ✅ processed URB925
# ✅ processed URB926
# ✅ processed URB927
# ✅ processed URB929
# ✅ processed URB931
# ✅ processed URB932
# ✅ processed URB933
# ✅ processed URB934
# ✅ processed URB935
# ✅ processed URB936
# ✅ processed URB937
# ✅ processed URB938
# ✅ processed URB939
# ✅ processed URB940
# ✅ processed URB941
# ✅ processed URB942
# ✅ processed URB943
# ✅ processed URB944
# ✅ processed URB945
# ✅ processed URB946
# ✅ processed URB947
# ✅ processed URB948
# ✅ processed URB949
# ✅ processed URB950
# ✅ processed URB951
# ✅ processed URB952
# ✅ processed URB953
# ✅ processed URB954
# ✅ processed URB955
# ✅ processed URB957
# ✅ processed URB958
# ✅ processed URB959
# ✅ processed URB960
# ✅ processed URB961
# ✅ processed URB962
# ✅ processed URB963
# ✅ processed URB964
# ✅ processed URB965
# ✅ processed URB966
# ✅ processed URB969
# ✅ processed URB970
# ✅ processed URB971
# ✅ processed URB972
# ✅ processed URB973
# ✅ processed URB974
# ✅ processed URB975
# ✅ processed URB976
# ✅ processed URB977
# ✅ processed URB978
# ✅ processed URB979
# ✅ processed URB980
# ✅ processed URB981
# ✅ processed URB982
# ✅ processed URB983
# ✅ processed URB984
# ✅ processed URB985
# ✅ processed URB986
# ✅ processed URB989
# ✅ processed URB990
# ✅ processed URB991
# ✅ processed URB992
# ✅ processed URB993
# ✅ processed URB994
# ✅ processed URB995
# ✅ processed URB996
# ✅ processed URB997
# ✅ processed URB998
# ✅ processed URB999
# ✅ processed URD0420
# 🎉 ALL DONE
# (env) PS E:\Scraping\Weather Station Metadata\Doctor\unrealbali\logo\new> de