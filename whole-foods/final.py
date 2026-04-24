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


# ==========================================
# FUNGSI UTAMA SCRAPER
# ==========================================

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
                    print(urls_in_section)
                    print(asin)

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
                # item_weight = get_detail_by_label(soup, "Item Weight")
                # upc = get_detail_by_label(soup, "UPC")
                # manufacturer = get_detail_by_label(soup, "Manufacturer")
                # asin_val = get_detail_by_label(soup, "ASIN")
                # units = get_detail_by_label(soup, "Units")
                # item_model_number = get_detail_by_label(soup, "Item model number")
                # package_Dimensions = get_detail_by_label(soup, "Package Dimensions")
                # calories = get_value_from_row_by_text(soup,"nic-nutrition-facts-energy","Calories")
                # serving_size = get_value_from_row_by_text(soup,"nic-nutrition-facts-serving-size","Serving size")
                # ingredients = get_ingredients(soup)
                # legal_disclaimer = get_Legal_Disclaimer(soup)
                # disclaimer = get_disclaimer(soup)
                # price = get_price(soup)
                # image_url = get_main_image(soup)
                # reviews = get_reviews_count(soup)


                item_weight = get_detail_by_label(soup, "Item Weight")
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

                # print("PRICE:", price)
                print("Product Name:", product_name)
                print("Product_url:", product_url)
                # print("Package Dimensions:", package_Dimensions)
                # print("UPC:", upc)
                # print("Manufacturer:", manufacturer)
                # print("ASIN:", asin_val)
                # print("Units:", units)

                # print("Serving Size:", serving_size)
                # print("Calories:", calories)

                # print("Total Fat:", get_nutrition_value(soup, "Total Fat"))
                # print("Saturated Fat:", get_nutrition_value(soup, "Saturated Fat"))
                # print("Monounsaturated Fat:", get_nutrition_value(soup, "Monounsaturated Fat"))
                # print("Polyunsaturated Fat:", get_nutrition_value(soup, "Polyunsaturated Fat"))
                # print("Cholesterol:", get_nutrition_value(soup, "Cholesterol"))
                # print("Sodium:", get_nutrition_value(soup, "Sodium"))
                # print("Total Carbohydrate:", get_nutrition_value(soup, "Total Carbohydrate"))
                # print("Dietary Fiber:", get_nutrition_value(soup, "Dietary Fiber"))
                # print("Soluble Fiber:", get_nutrition_value(soup, "Soluble Fiber"))
                # print("Insoluble Fiber:", get_nutrition_value(soup, "Insoluble Fiber"))
                # print("Sugars:", get_nutrition_value(soup, "Sugars"))
                # print("Added Sugars:", get_nutrition_value(soup, "Added Sugars"))
                # print("Starch:", get_nutrition_value(soup, "Starch"))
                # print("Other Carbohydrate:", get_nutrition_value(soup, "Other Carbohydrate"))
                # print("Sugar Alcohol:", get_nutrition_value(soup, "Sugar Alcohol"))
                # print("Protein:", get_nutrition_value(soup, "Protein"))
                # print("Vitamin A:", get_nutrition_value(soup, "Vitamin A"))
                # print("Vitamin C:", get_nutrition_value(soup, "Vitamin C"))
                # print("Calcium:", get_nutrition_value(soup, "Calcium"))
                # print("Iron:", get_nutrition_value(soup, "Iron"))


                # print("Brand:", get_product_table_value(soup, "Brand"))
                # print("Item Weight:", get_product_table_value(soup, "Item Weight"))
                # print("Specialty:", get_product_table_value(soup, "Specialty"))
                # print("Temperature Condition:", get_product_table_value(soup, "Temperature Condition"))
                # print("Number of Pieces:", get_product_table_value(soup, "Number of Pieces"))
                # print("Region of Origin:", get_product_table_value(soup, "Region of Origin"))
                # print("Cuisine:", get_product_table_value(soup, "Cuisine"))
                # print("Variety:", get_product_table_value(soup, "Variety"))
                # print("Number of Items:", get_product_table_value(soup, "Number of Items"))
                # print("Size:", get_product_table_value(soup, "Size"))

                # print("Flavor:", get_product_table_value(soup, "Flavor"))
                # print("Produce sold as:", get_product_table_value(soup, "Produce sold as"))
                # print("Item Form:", get_product_table_value(soup, "Item Form"))

                # print("INGREDIENTS:", ingredients)
                # print("LEGAL DISCLAIMER:", legal_disclaimer)
                # print("DISCLAIMER:", disclaimer)
                # print("Product Description:", product_description)
                # print("IMAGE:", image_url)
                
                print("-" * 30)
                print("-" * 20)
                # break
            
            else:
                print(f"TITLE: Not Found (Captcha/OOS) -> {product_url}")