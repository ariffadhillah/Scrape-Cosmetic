import requests
import json
import time
from bs4 import BeautifulSoup

API_URL = "https://www.boots.com/INTERSHOP/web/WFS/Boots-BootsGB-Site/en_GB/-/GBP/ViewBootsSearch-SimpleProductSearch"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}


def get_all_product_urls():
    """Ambil produk dasar dari API (Brand, Description, Rating, ReviewCount, URL)"""
    all_products = []
    page_index = 0
    page_size = 44
    total_products = None

    while True:
        payload = {
            "query": "",
            "indices": {
                "products": {
                    "paging": {"index": page_index, "size": page_size},
                    "criteria": {"category": ["beauty & skincare", "makeup", "face"]},
                    "sortBy": "mostRelevant",
                }
            },
            "returnHits": True,
            "returnSuggestions": False,
            "returnFacets": True,
            "returnChanel": False,
            "searchRequired": True,
            "adRequired": True,
            "adParams": {
                "pageId": "viewCategoryApiDesktop",
                "eventType": "viewCategory",
                "environment": "desktop",
                "customerId": "",
                "category": "1595015>1595036>1595098",
            },
        }

        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
        data = response.json()

        if total_products is None:
            total_products = data["products"]["paging"]["total"]
            print(f"🔎 Total produk ditemukan: {total_products}")

        hits = data["products"]["hits"]
        if not hits:
            break

        for product in hits:
            product_data = {
                "Brand": product.get("brand"),
                "Description": product.get("title"),
                "Rating": product.get("reviews", {}).get("average"),
                "ReviewCount": product.get("reviews", {}).get("count"),
                "URL": f'https://www.boots.com{product.get("referenceUri")}',
            }
            all_products.append(product_data)

        page_index += 1
        if page_index * page_size >= total_products:
            break

        time.sleep(1)

    print(f"✅ Total produk terkumpul: {len(all_products)}")
    return all_products


def scrape_product_html(url):
    """Ambil data tambahan dari HTML"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Gagal buka {url}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    # Product Code
    product_code = soup.select_one("span[itemprop='sku']")
    product_code = product_code.get_text(strip=True) if product_code else None

    # SKU (kadang di meta tag atau di script JSON-LD)
    sku = None
    sku_tag = soup.find("meta", {"itemprop": "productID"})
    if sku_tag:
        sku = sku_tag.get("content")

    # Ingredients
    ingredients = None
    ing_header = soup.find(string=lambda t: "Ingredients" in t)
    if ing_header:
        ing_block = ing_header.find_parent()
        if ing_block:
            sibling = ing_block.find_next_sibling()
            if sibling:
                ingredients = sibling.get_text(strip=True)

    # Breadcrumb → Specific Category
    breadcrumb_tags = soup.select("div.breadcrumb-container .breadcrumb-item__text")
    specific_category = breadcrumb_tags[-2].get_text(strip=True) if len(breadcrumb_tags) >= 2 else None

    # Image
    image = None
    img_tag = soup.select_one("img.product-carousel__image")
    if img_tag:
        image = img_tag.get("src")

    return {
        "ProductCode": product_code,
        "SKU": sku,
        "Ingredients": ingredients,
        "SpecificCategory": specific_category,
        "Image": image,
    }


if __name__ == "__main__":
    products = get_all_product_urls()

    # Tes 5 produk dulu
    for i, product in enumerate(products[:5], start=1):
        print(f"\n📌 Scraping produk {i}: {product['URL']}")
        extra = scrape_product_html(product["URL"])
        product.update(extra)
        print(json.dumps(product, indent=2, ensure_ascii=False))
