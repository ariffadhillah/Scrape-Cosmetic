import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random

# --- KONFIGURASI TESTING ---
TARGET_ASIN = "B0CD7TDBDC" 
BASE_URL = "https://www.amazon.com/dp/"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# ==========================================
# FUNGSI EKSTRAKSI DATA (MENGEMBALIKAN STRING)
# ==========================================



def get_reviews_count(soup):
    el = soup.select_one("#acrCustomerReviewText")
    if not el:
        return None

    text = el.get_text(strip=True)

    # ambil angka saja
    num = re.search(r'[\d,]+', text)
    if not num:
        return None

    count = num.group(0).replace(",", "")
    return int(count)   # return angka murni


def get_main_image(soup):

    img = soup.select_one("#imgTagWrapperId img")

    if not img:
        return None

    # prioritas gambar resolusi tinggi
    hires = img.get("data-old-hires")
    if hires and hires.strip():
        return hires.strip()

    # fallback ke src
    src = img.get("src")
    if src:
        return src.strip()

    return None


def get_ingredients(soup):

    # 1️⃣ masuk ke container penting dulu
    container = soup.find("div", id="important-information")
    if not container:
        return None

    # 2️⃣ cari label Ingredients di dalam container saja
    header = container.find(
        "span",
        string=lambda s: s and "ingredients" in s.lower()
    )

    if not header:
        return None

    # 3️⃣ ambil semua <p> setelah header
    for p in header.find_all_next("p"):

        # stop kalau sudah keluar dari container
        if container not in p.parents:
            break

        text = p.get_text(strip=True)

        # skip kosong
        if text:
            return text

    return None

def get_Legal_Disclaimer(soup):

    # 1️⃣ masuk ke container penting dulu
    container = soup.find("div", id="important-information")
    if not container:
        return None

    # 2️⃣ cari label Ingredients di dalam container saja
    header = container.find(
        "span",
        string=lambda s: s and "legal disclaimer" in s.lower()
    )

    if not header:
        return None

    # 3️⃣ ambil semua <p> setelah header
    for p in header.find_all_next("p"):

        # stop kalau sudah keluar dari container
        if container not in p.parents:
            break

        text = p.get_text(strip=True)

        # skip kosong
        if text:
            return text

    return None

def get_disclaimer(soup):

    container = soup.find("div", id="storeDisclaimer_feature_div")
    if not container:
        return None

    label = container.find(
        "strong",
        string=lambda s: s and "disclaimer" in s.lower()
    )

    if not label:
        return None

    # teks ada di parent <p>
    p = label.find_parent("p")
    if not p:
        return None

    text = p.get_text(" ", strip=True)

    # buang kata "Disclaimer:"
    text = text.replace("Disclaimer:", "").strip()

    return text



def get_detail_by_label(soup, label_text):
    labels = soup.select("#detailBullets_feature_div .a-text-bold")

    for lab in labels:
        text = lab.get_text(strip=True)

        if label_text.lower() in text.lower():

            # ambil parent span a-list-item
            parent = lab.find_parent("span", class_="a-list-item")

            if parent:
                spans = parent.find_all("span")

                # value biasanya span terakhir
                if len(spans) >= 2:
                    value = spans[-1].get_text(strip=True)
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

def get_price(soup):
    """
    Ekstraksi harga HANYA dari Accordion Header (One-time purchase).
    Metode ini mengunci elemen spesifik agar tidak mengambil harga sampah.
    """
    # 1. Kunci area Accordion penawaran utama
    accordion_header = soup.find("div", {"data-csa-c-content-id": "offer_display_desktop_accordion_header"})
    
    if accordion_header:
        # 2. Cari kontainer harga di dalam accordion tersebut
        # Target: <div class="a-spacing-top-mini apex-core-price-identifier">
        price_identifier = accordion_header.select_one(".apex-core-price-identifier")
        
        if price_identifier:
            # 3. Ambil data dari a-offscreen di dalam kontainer tersebut
            price_element = price_identifier.select_one(".a-offscreen")
            if price_element:
                return price_element.get_text(strip=True)
            
            # 4. Jika a-offscreen tidak ada, rakit secara manual dari simbol, whole, dan fraction
            symbol = price_identifier.select_one(".a-price-symbol")
            whole = price_identifier.select_one(".a-price-whole")
            fraction = price_identifier.select_one(".a-price-fraction")
            
            if whole and fraction:
                s = symbol.get_text(strip=True) if symbol else "$"
                # Bersihkan titik dari 'whole' jika ada
                w = whole.get_text(strip=True).replace(".", "")
                f = fraction.get_text(strip=True)
                return f"{s}{w}.{f}"

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
                price = get_price(v_soup)
                name = title_el.get_text(strip=True)
                # brand = get_product_table_value(v_soup, "Brand")
                # ingred = get_ingredients(v_soup)
                
                # # Nutrition Check
                # cal_tag = v_soup.find(id="nic-nutrition-facts-energy")
                # calories = cal_tag.get_text(strip=True) if cal_tag else get_nutrition_value(v_soup, "Calories")
                # fat = get_nutrition_value(v_soup, "Total Fat")
                # protein = get_nutrition_value(v_soup, "Protein")

                # # TAMPILKAN DATA MENTAH KE TERMINAL
                # print(f"      PRICE       : {price}")
                # print(f"      BRAND       : {brand}")
                # print(f"      INGREDIENTS : {ingred[:100]}...")
                # print(f"      CALORIES    : {calories}")
                # print(f"      TOTAL FAT   : {fat}")
                # print(f"      PROTEIN     : {protein}")


                item_weight = get_detail_by_label(v_soup, "Item Weight")
                upc = get_detail_by_label(v_soup, "UPC")
                manufacturer = get_detail_by_label(v_soup, "Manufacturer")
                asin_val = get_detail_by_label(v_soup, "ASIN")
                units = get_detail_by_label(v_soup, "Units")
                item_model_number = get_detail_by_label(v_soup, "Item model number")
                package_Dimensions = get_detail_by_label(v_soup, "Package Dimensions")
                calories = get_value_from_row_by_text(v_soup,"nic-nutrition-facts-energy","Calories")
                serving_size = get_value_from_row_by_text(v_soup,"nic-nutrition-facts-serving-size","Serving size")
                ingredients = get_ingredients(v_soup)
                legal_disclaimer = get_Legal_Disclaimer(v_soup)
                disclaimer = get_disclaimer(v_soup)
                # price = get_price(v_soup)
                image_url = get_main_image(v_soup)


                print("PRICE:", price)
                print(f"NAME        : {name[:70]}...")
                print("Package Dimensions:", package_Dimensions)
                print("UPC:", upc)
                print("Manufacturer:", manufacturer)
                print("ASIN:", asin_val)
                print("Units:", units)
                print("-" * 30)

                print("Serving Size:", serving_size)
                print("Calories:", calories)

                print("Total Fat:", get_nutrition_value(v_soup, "Total Fat"))
                print("Saturated Fat:", get_nutrition_value(v_soup, "Saturated Fat"))
                print("Monounsaturated Fat:", get_nutrition_value(v_soup, "Monounsaturated Fat"))
                print("Polyunsaturated Fat:", get_nutrition_value(v_soup, "Polyunsaturated Fat"))
                print("Cholesterol:", get_nutrition_value(v_soup, "Cholesterol"))
                print("Sodium:", get_nutrition_value(v_soup, "Sodium"))
                print("Total Carbohydrate:", get_nutrition_value(v_soup, "Total Carbohydrate"))
                print("Dietary Fiber:", get_nutrition_value(v_soup, "Dietary Fiber"))
                print("Soluble Fiber:", get_nutrition_value(v_soup, "Soluble Fiber"))
                print("Insoluble Fiber:", get_nutrition_value(v_soup, "Insoluble Fiber"))
                print("Sugars:", get_nutrition_value(v_soup, "Sugars"))
                print("Added Sugars:", get_nutrition_value(v_soup, "Added Sugars"))
                print("Starch:", get_nutrition_value(v_soup, "Starch"))
                print("Other Carbohydrate:", get_nutrition_value(v_soup, "Other Carbohydrate"))
                print("Sugar Alcohol:", get_nutrition_value(v_soup, "Sugar Alcohol"))
                print("Protein:", get_nutrition_value(v_soup, "Protein"))
                print("Vitamin A:", get_nutrition_value(v_soup, "Vitamin A"))
                print("Vitamin C:", get_nutrition_value(v_soup, "Vitamin C"))
                print("Calcium:", get_nutrition_value(v_soup, "Calcium"))
                print("Iron:", get_nutrition_value(v_soup, "Iron"))


                print("Brand:", get_product_table_value(v_soup, "Brand"))
                print("Item Weight:", get_product_table_value(v_soup, "Item Weight"))
                print("Specialty:", get_product_table_value(v_soup, "Specialty"))
                print("Temperature Condition:", get_product_table_value(v_soup, "Temperature Condition"))
                print("Number of Pieces:", get_product_table_value(v_soup, "Number of Pieces"))
                print("Region of Origin:", get_product_table_value(v_soup, "Region of Origin"))
                print("Cuisine:", get_product_table_value(v_soup, "Cuisine"))
                print("Variety:", get_product_table_value(v_soup, "Variety"))
                print("Number of Items:", get_product_table_value(v_soup, "Number of Items"))
                print("Size:", get_product_table_value(v_soup, "Size"))
                print("-" * 30)

                print("Flavor:", get_product_table_value(v_soup, "Flavor"))
                print("Produce sold as:", get_product_table_value(v_soup, "Produce sold as"))
                print("Item Form:", get_product_table_value(v_soup, "Item Form"))

                print("INGREDIENTS:", ingredients)
                print("LEGAL DISCLAIMER:", legal_disclaimer)
                print("DISCLAIMER:", disclaimer)
                print("IMAGE:", image_url)
            else:
                print(f"      >>> [!] GAGAL: Judul tidak ditemukan (Struktur HTML mungkin berubah)")
        
        print("-" * 60)

if __name__ == "__main__":
    main()