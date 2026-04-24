import csv
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://www.superdrug.com"

fields = [
    "Major Category",
    "Specific Category",
    "Product ID",
    "SKU ID",
    "Product Brand",
    "Product Desc",
    "Product URL",
    "Product Image Link",
    "Product Ingredients",
    "Rating",
    "User Reviews",
]

def accept_cookies(page):
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=8000)
        page.click("#onetrust-accept-btn-handler")
        print("🍪 Cookies accepted")
        page.wait_for_timeout(2000)
    except:
        print("🍪 No cookie banner found")

def page_details(page, product_url, major_category=None):
    page.goto(product_url, timeout=99000)
    page.wait_for_timeout(2000)
    time.sleep(.5)
    soup = BeautifulSoup(page.content(), "html.parser")

    # Brand
    brand_tag = soup.select_one("a.product-details-brand-link__text-link span")
    product_brand = brand_tag.get_text(strip=True) if brand_tag else None

    # Description
    desc_tag = soup.select_one("h1.product-details-title__text")
    product_desc = desc_tag.get_text(strip=True) if desc_tag else None

    # Reviews count
    reviews_tag = soup.select_one("span.reviews")
    number_of_reviews = reviews_tag.get_text(strip=True).strip("()") if reviews_tag else None
    if number_of_reviews:
        number_of_reviews = f"'{number_of_reviews}"

    # Rating
    rating_tag = soup.select_one("h3.pr-review-snapshot-snippets-headline")
    average_rating = rating_tag.get_text(strip=True) if rating_tag else None
    if average_rating:
        average_rating = f"'{average_rating}"

    # Product Code (jadi Product ID)
    code_tag = soup.select_one("p.product-general-information__section-item-description--articleNumber")
    product_code = code_tag.get_text(strip=True).replace("Product code:", "").strip() if code_tag else None
    if product_code:
        product_code = f"'{product_code}"

    # EAN (jadi SKU ID)
    ean_tag = soup.select_one("p.product-general-information__section-item-description--ean")
    ean = ean_tag.get_text(strip=True).replace("EAN:", "").strip() if ean_tag else None
    if ean:
        ean = f"'{ean}"

    # Ingredients
    ingredients_tag = soup.select_one("p.product-general-information__section-item-description--ingredients")
    ingredients = ingredients_tag.get_text(strip=True) if ingredients_tag else None

    # Ambil semua gambar 600x600
    image_tags = soup.select(".product-images-grid__image img")
    image_urls = [img.get("src") for img in image_tags if img.get("src") and "600x600" in img.get("src")]
    main_image = image_urls[0] if image_urls else None

    # Specific category (breadcrumb sebelum terakhir)
    breadcrumb_tags = soup.select("div.breadcrumb-container .breadcrumb-item__text")
    specific_category = breadcrumb_tags[-2].get_text(strip=True) if len(breadcrumb_tags) >= 2 else None

    return {
        "Major Category": major_category,
        "Specific Category": specific_category,
        "Product ID": product_code,        # ✅ sudah ditambah tanda '
        "SKU ID": ean,                     # ✅ sudah ditambah tanda '
        "Product Brand": product_brand,
        "Product Desc": product_desc,
        "Product URL": product_url,
        "Product Image Link": main_image,
        "Product Ingredients": ingredients,
        "Rating": average_rating,          # ✅ sudah ditambah tanda '
        "User Reviews": number_of_reviews  # ✅ sudah ditambah tanda '
    }


if __name__ == "__main__":
    input_file = "Makeup-superdrug_product_urls.csv"   # 📥 hasil step 1 (URL list)
    output_file = "Makeup-superdrug_products.csv"      # 📤 hasil detail produk

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        page.goto(BASE_URL, timeout=40000)
        accept_cookies(page)

        processed_urls = set()

        with open(input_file, "r", encoding="utf-8") as fin, \
             open(output_file, "w", newline="", encoding="utf-8") as fout:

            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=fields)
            writer.writeheader()

            for row in reader:
                major_category = row["Major Category"]
                # specific_category = row["Specific Category"]
                product_url = row["Product URL"]

                if product_url in processed_urls:
                    continue

                try:
                    details = page_details(page, product_url, major_category)
                    writer.writerow(details)
                    processed_urls.add(product_url)
                    print("   →", details["Product URL"])
                except Exception as e:
                    print(f"⚠️ Gagal scraping {product_url}: {e}")

        browser.close()
