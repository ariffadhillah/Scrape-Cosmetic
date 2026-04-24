import csv
import os
import requests
from bs4 import BeautifulSoup
import json
import html
import time
import re
# url = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Connection": "keep-alive"
# }

# session = requests.Session()
# session.headers.update(headers)

# session.cookies.update({
#     "i18n-prefs": "USD",
#     "lc-main": "en_US"
# })

# res = session.get(url, timeout=30)
# soup = BeautifulSoup(res.text, "html.parser")


url = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Upgrade-Insecure-Requests": "1"
}





session = requests.Session()
session.headers.update(headers)

# ⭐ paksa US locale + USD currency
session.cookies.update({
    "i18n-prefs": "USD",
    "lc-main": "en_US"
})

res = session.get(url, timeout=30)

print("STATUS:", res.status_code)

soup = BeautifulSoup(res.text, "lxml")


# csv_file = "amazon_products.csv"
headers = [
    "Category","Manufacturer", "Brand","ASIN","UPC","Item model number", 
    "Package Dimensions","Units","Product Url", "Item Weight",
    "Serving Size","Calories",
    "Total Fat","Saturated Fat","Monounsaturated Fat","Polyunsaturated Fat",
    "Cholesterol","Sodium","Total Carbohydrate","Dietary Fiber","Soluble Fiber",
    "Insoluble Fiber","Sugars","Added Sugars","Starch","Other Carbohydrate",
    "Sugar Alcohol","Protein","Vitamin A","Vitamin C","Calcium","Iron",
    "Flavor","Size","Item Weight Table","Cuisine","Variety",
    "Number of Items","Produce sold as","Temperature Condition","Item Form",
    "Ingredients","Legal Disclaimer","Disclaimer","Image Url","Price",
    "Stars","Reviews"
]

# buat file + header kalau belum ada
# if not os.path.exists(csv_file):
#     with open(csv_file, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=headers)
#         writer.writeheader()



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

def get_product_table_value(soup, label):
    label = label.lower().strip()

    # ---------- 1️⃣ Cari di table lama (td - td) ----------
    tables1 = soup.find_all("table", class_="a-normal a-spacing-micro")

    for table in tables1:
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                name = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                if name == label:
                    return value

    # ---------- 2️⃣ Cari di productDetails table (th - td) ----------
    tables2 = soup.find_all("table", class_="prodDetTable")

    for table in tables2:
        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")

            if th and td:
                name = th.get_text(strip=True).lower()
                value = td.get_text(strip=True)

                if name == label:
                    return value

    return None

target_div = None

for div in soup.find_all("div", attrs={"data-carouselheadingattributesstring": True}):
    heading_json = html.unescape(div["data-carouselheadingattributesstring"])
    heading = json.loads(heading_json)

    if heading.get("headingText") == "Lunar New Year favorites":
        target_div = div
        break

if not target_div:
    print("Target section not found")
    exit()

raw = html.unescape(target_div["data-a-carousel-options"])
carousel = json.loads(raw)

id_list = carousel.get("ajax", {}).get("id_list", [])

asins = []
for item in id_list:
    obj = json.loads(item)
    asins.append(obj["id"])

urls = [f"https://www.amazon.com/dp/{a}" for a in asins]

print("Found:", len(urls))
print("\nOpening products...\n")

for i, product_url in enumerate(urls, 1):

    print(f"[{i}/{len(urls)}] Opening:", product_url)

    try:
        r = session.get(product_url, timeout=30)

        if "captcha" in r.text.lower():
            print("Blocked by Amazon CAPTCHA")
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.select_one("#productTitle")

        # if title:
        #     print("TITLE:", title.get_text(strip=True))
        # else:
        #     print("Title not found")

        if title:
            print("TITLE:", title.get_text(strip=True))
        else:
            print("Title not found")

        # =========================
        # DETAIL BULLETS PARSER
        # =========================
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


        # print("PRICE:", price)
        print("Package Dimensions:", package_Dimensions)
        print("UPC:", upc)
        print("Manufacturer:", manufacturer)
        print("ASIN:", asin_val)
        print("Units:", units)
        print("-" * 30)

        print("Serving Size:", serving_size)
        print("Calories:", calories)

        print("Total Fat:", get_nutrition_value(soup, "Total Fat"))
        print("Saturated Fat:", get_nutrition_value(soup, "Saturated Fat"))
        print("Monounsaturated Fat:", get_nutrition_value(soup, "Monounsaturated Fat"))
        print("Polyunsaturated Fat:", get_nutrition_value(soup, "Polyunsaturated Fat"))
        print("Cholesterol:", get_nutrition_value(soup, "Cholesterol"))
        print("Sodium:", get_nutrition_value(soup, "Sodium"))
        print("Total Carbohydrate:", get_nutrition_value(soup, "Total Carbohydrate"))
        print("Dietary Fiber:", get_nutrition_value(soup, "Dietary Fiber"))
        print("Soluble Fiber:", get_nutrition_value(soup, "Soluble Fiber"))
        print("Insoluble Fiber:", get_nutrition_value(soup, "Insoluble Fiber"))
        print("Sugars:", get_nutrition_value(soup, "Sugars"))
        print("Added Sugars:", get_nutrition_value(soup, "Added Sugars"))
        print("Starch:", get_nutrition_value(soup, "Starch"))
        print("Other Carbohydrate:", get_nutrition_value(soup, "Other Carbohydrate"))
        print("Sugar Alcohol:", get_nutrition_value(soup, "Sugar Alcohol"))
        print("Protein:", get_nutrition_value(soup, "Protein"))
        print("Vitamin A:", get_nutrition_value(soup, "Vitamin A"))
        print("Vitamin C:", get_nutrition_value(soup, "Vitamin C"))
        print("Calcium:", get_nutrition_value(soup, "Calcium"))
        print("Iron:", get_nutrition_value(soup, "Iron"))


        print("Brand:", get_product_table_value(soup, "Brand"))
        print("Item Weight:", get_product_table_value(soup, "Item Weight"))
        print("Specialty:", get_product_table_value(soup, "Specialty"))
        print("Temperature Condition:", get_product_table_value(soup, "Temperature Condition"))
        print("Number of Pieces:", get_product_table_value(soup, "Number of Pieces"))
        print("Region of Origin:", get_product_table_value(soup, "Region of Origin"))
        print("Cuisine:", get_product_table_value(soup, "Cuisine"))
        print("Variety:", get_product_table_value(soup, "Variety"))
        print("Number of Items:", get_product_table_value(soup, "Number of Items"))
        print("Size:", get_product_table_value(soup, "Size"))
        print("-" * 30)

        print("Flavor:", get_product_table_value(soup, "Flavor"))
        print("Produce sold as:", get_product_table_value(soup, "Produce sold as"))
        print("Item Form:", get_product_table_value(soup, "Item Form"))

        print("INGREDIENTS:", ingredients)
        print("LEGAL DISCLAIMER:", legal_disclaimer)
        print("DISCLAIMER:", disclaimer)
        print("IMAGE:", image_url)

        # # =========================
        # # RATING
        # # =========================
        # stars = soup.select_one("#acrPopover span.a-size-small")
        # if stars:
        #     print("Stars:", stars.get_text(strip=True))

        # reviews = soup.select_one("#acrCustomerReviewText")
        # if reviews:
        #     print("Reviews:", reviews.get_text(strip=True).strip("()"))

        # row = {

        #     "Category": "Save on Seasonal Produce",
        #     "Manufacturer": manufacturer,
        #     "Brand": get_product_table_value(soup,"Brand"),
        #     "UPC": upc,
        #     "ASIN": asin_val,
        #     "Item model number": f"'{item_model_number}",
        #     "Product Url": product_url,
        #     "Package Dimensions": package_Dimensions,
        #     "Units": units,
        #     "Flavor": get_product_table_value(soup,"Flavor"),
        #     "Item Weight": item_weight,
        #     "Specialty": get_product_table_value(soup, "Specialty"),
        #     "Temperature Condition": get_product_table_value(soup,"Temperature Condition"),
        #     "Cuisine": get_product_table_value(soup,"Cuisine"),
        #     "Variety": get_product_table_value(soup,"Variety"),
        #     "Size": get_product_table_value(soup,"Size"),
        #     "Number of Items": get_product_table_value(soup,"Number of Items"),
            
        #     "Serving Size": serving_size,
        #     "Calories": calories,
        #     "Total Fat": get_nutrition_value(soup,"Total Fat"),
        #     "Saturated Fat": get_nutrition_value(soup,"Saturated Fat"),
        #     "Monounsaturated Fat": get_nutrition_value(soup,"Monounsaturated Fat"),
        #     "Polyunsaturated Fat": get_nutrition_value(soup,"Polyunsaturated Fat"),
        #     "Cholesterol": get_nutrition_value(soup,"Cholesterol"),
        #     "Sodium": get_nutrition_value(soup,"Sodium"),
        #     "Total Carbohydrate": get_nutrition_value(soup,"Total Carbohydrate"),
        #     "Dietary Fiber": get_nutrition_value(soup,"Dietary Fiber"),
        #     "Soluble Fiber": get_nutrition_value(soup,"Soluble Fiber"),
        #     "Insoluble Fiber": get_nutrition_value(soup,"Insoluble Fiber"),
        #     "Sugars": get_nutrition_value(soup,"Sugars"),
        #     "Added Sugars": get_nutrition_value(soup,"Added Sugars"),
        #     "Starch": get_nutrition_value(soup,"Starch"),
        #     "Other Carbohydrate": get_nutrition_value(soup,"Other Carbohydrate"),
        #     "Sugar Alcohol": get_nutrition_value(soup,"Sugar Alcohol"),
        #     "Protein": get_nutrition_value(soup,"Protein"),
        #     "Vitamin A": get_nutrition_value(soup,"Vitamin A"),
        #     "Vitamin C": get_nutrition_value(soup,"Vitamin C"),
        #     "Calcium": get_nutrition_value(soup,"Calcium"),
        #     "Iron": get_nutrition_value(soup,"Iron"),

        #     # "Item Weight Table": get_product_table_value(soup,"Item Weight"),
        #     "Produce sold as": get_product_table_value(soup,"Produce sold as"),
        #     "Item Form": get_product_table_value(soup,"Item Form"),
        #     "Ingredients": ingredients,
        #     "Legal Disclaimer": legal_disclaimer,
        #     "Disclaimer": disclaimer,
        #     "Image Url": image_url,
        #     "Price": price,
        #     "Stars": soup.select_one("#acrPopover span.a-size-small").get_text(strip=True)
        #             if soup.select_one("#acrPopover span.a-size-small") else None,

        #     # "Reviews": soup.select_one("#acrCustomerReviewText").get_text(strip=True)
        #     #         if soup.select_one("#acrCustomerReviewText") else None,
        #     "Reviews": get_reviews_count(soup),
        # }

        # Write row to CSV file
        # with open("Amazon_products.csv", "a", newline="", encoding="utf-8") as f:
        #     writer = csv.DictWriter(f, fieldnames=row.keys())
        #     if f.tell() == 0:  # If file is empty, write header
        #         writer.writeheader()
        #     writer.writerow(row)

        # break



    except Exception as e:
        print("ERROR:", e)

    print("-" * 60)
    time.sleep(2)
