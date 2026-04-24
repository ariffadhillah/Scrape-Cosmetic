from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import time

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
    """Klik tombol Accept Cookies jika ada."""
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=8000)
        page.click("#onetrust-accept-btn-handler")
        print("🍪 Cookies accepted")
        page.wait_for_timeout(4000)
    except:
        print("🍪 No cookie banner found")

def get_category_links(page):
    """Ambil semua kategori utama Makeup (kecuali 'New In Makeup')."""
    page.goto(BASE_URL + "/make-up/c/makeup", timeout=99000)
    soup = BeautifulSoup(page.content(), "html.parser")

    first_wrapper = soup.find("div", class_="wrapper wrapper--0")
    category_links = []

    if first_wrapper:
        for a in first_wrapper.select("div.childs a.link"):
            name = a.get_text(strip=True)
            href = a.get("href")
            if href and "new-make-up" not in href.lower():
                category_links.append({"name": name, "url": BASE_URL + href})
    return category_links

def get_subcategory_links(page, category_url):
    """Ambil sub kategori dari 1 kategori."""
    page.goto(category_url, timeout=99000)
    soup = BeautifulSoup(page.content(), "html.parser")

    subcategory_links = []
    wrapper = soup.find("div", class_="wrapper wrapper--0")
    if wrapper:
        for a in wrapper.select("div.childs a.link"):
            name = a.get_text(strip=True)
            href = a.get("href")
            if href:
                subcategory_links.append({"name": name, "url": BASE_URL + href})
    return subcategory_links

def get_product_links(page, subcategory_url):
    """Ambil semua produk dari subkategori (dengan pagination)."""
    all_products = []
    page_num = 0

    while True:
        url = subcategory_url if page_num == 0 else f"{subcategory_url}?currentPage={page_num}"
        page.goto(url, timeout=99000)
        page.wait_for_timeout(5500)
        time.sleep(4)

        soup = BeautifulSoup(page.content(), "html.parser")
        product_list = soup.find("div", class_="product-grid__products-list")
        if not product_list:
            break

        products = []
        for a in product_list.select("a.product-image-container, a.cx-product-name"):
            href = a.get("href")
            if href and "/p/" in href:
                products.append(BASE_URL + href)

        if not products:
            break

        print(f"   📄 Page {page_num+1} → {len(products)} produk")
        all_products.extend(products)
        page_num += 1

    # Hapus duplikat URL sebelum dikembalikan
    return list(set(all_products))

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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        page.goto(BASE_URL, timeout=40000)
        accept_cookies(page)

        processed_urls = set()  # ✅ set untuk menyimpan URL yang sudah diproses

        with open("terbaru-superdrug_products.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            categories = get_category_links(page)
            for cat in categories:
                print(f"\n=== {cat['name']} ===")
                subcats = get_subcategory_links(page, cat["url"])
                targets = subcats if subcats else [{"name": cat["name"], "url": cat["url"]}]

                for sub in targets:
                    print(f"  ↳ {sub['name']}")
                    products = get_product_links(page, sub["url"])
                    for prod in products:
                        if prod in processed_urls:
                            continue  # lewati jika sudah diproses
                        details = page_details(page, prod, major_category=cat["name"])
                        writer.writerow(details)
                        processed_urls.add(prod)
                        print("   →", details["Product URL"])

        browser.close()
