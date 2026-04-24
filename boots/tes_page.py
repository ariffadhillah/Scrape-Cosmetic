import requests
from bs4 import BeautifulSoup
import json
import time
import csv

# ======================
# STEP 1: Ambil semua URL produk dari API
# ======================
API_URL = "https://www.boots.com/online/api/search/v2/multiple-query/uk"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "content-type": "application/json",
    "x-client-id": "9c5ed6f8b3d1ec6191ae260ae7daac",
    "x-search-usertoken": "457ce85f-b9f3-41b6-b132-08691f8ff0ec",
    "x-user-token": "457ce85f-b9f3-41b6-b132-08691f8ff0ec",
    "Origin": "https://www.boots.com",
    "Referer": "https://www.boots.com/beauty/makeup/face"
}


def get_all_product_urls():
    """Ambil semua referenceUri dari Boots API"""
    all_urls = []
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

    #     response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    #     data = response.json()

    #     if total_products is None:
    #         total_products = data["products"]["paging"]["total"]
    #         print(f"🔎 Total produk ditemukan: {total_products}")

    #     hits = data["products"]["hits"]
    #     if not hits:
    #         break

    #     for product in hits:
    #         reference_uri = f'https://www.boots.com{product.get("referenceUri")}'
    #         all_urls.append(reference_uri)

    #     page_index += 1
    #     if page_index * page_size >= total_products:
    #         break

    #     time.sleep(1)

    # print(f"✅ Total URL terkumpul: {len(all_urls)}")
    # return all_urls


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

# ======================
# STEP 2: Scraper per produk
# ======================
def get_sibling_text(soup, keyword):
    """Cari teks setelah heading tertentu (contoh: Ingredients)."""
    h_tag = soup.find(["h2", "h3"], string=lambda t: t and keyword.lower() in t.lower())
    if h_tag:
        sib = h_tag.find_next_sibling(["p", "div"])
        if sib:
            return sib.get_text(" ", strip=True)
    return None


def scrape_product(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Gagal buka {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Brand
    brand_tag = soup.select_one("a.product-details-brand-link__text-link span")
    if brand_tag:
        product_brand = brand_tag.get_text(strip=True)
    else:
        brand_tag = soup.select_one('span[itemprop="Brand"]')
        product_brand = brand_tag.get_text(strip=True) if brand_tag else None

    # Description
    desc_tag = soup.select_one("h1.pdpTitle")
    product_desc = desc_tag.get_text(strip=True) if desc_tag else None

    # Rating Value
    rating_value_tag = soup.select_one('[itemprop="ratingValue"]')
    rating_value = rating_value_tag.get_text(strip=True) if rating_value_tag else None

    # Review Count
    review_count_tag = soup.select_one('meta[itemprop="reviewCount"]')
    if review_count_tag and review_count_tag.has_attr("content"):
        review_count = review_count_tag["content"]
    else:
        review_count_div = soup.select_one("div.bv_numReviews_text")
        review_count = review_count_div.get_text(strip=True) if review_count_div else None

    # Product Code
    product_id_tag = soup.select_one("div#productId")
    product_id = product_id_tag.get_text(strip=True) if product_id_tag else None

    # SKU ID → ambil dari URL
    sku_id = url.split("-")[-1] if "-" in url else None

    # Ingredients
    product_ingredients = get_sibling_text(soup, "Ingredients")

    # Image
    image_tag = soup.select_one('img[itemprop="image"]')
    product_image = image_tag["src"] if image_tag and image_tag.has_attr("src") else None

    # Specific Category (breadcrumb sebelum terakhir)
    breadcrumb_tags = soup.select("div.breadcrumb-container .breadcrumb-item__text")
    specific_category = breadcrumb_tags[-2].get_text(strip=True) if len(breadcrumb_tags) >= 2 else None

    # return {
    #     "Brand": product_brand,
    #     "Description": product_desc,
    #     "Rating": rating_value,
    #     "ReviewCount": review_count,
    #     "ProductCode": product_id,
    #     "SKU": sku_id,
    #     "Ingredients": product_ingredients,
    #     "Image": product_image,
    #     "SpecificCategory": specific_category,
    #     "URL": url,
    # }

    return {
        "ProductCode": product_id,
        "SKU": sku_id,
        "Ingredients": product_ingredients,
        "SpecificCategory": specific_category,
        "Image": product_image,
    }

# ======================
# STEP 3: Main Process
# ======================
# if __name__ == "__main__":
#     urls = get_all_product_urls()

#     for i, url in enumerate(urls[:5], start=1):  # tes dulu 5 produk pertama
#         print(f"\n📌 Scraping produk {i}: {url}")
#         product_data = scrape_product(url)
#         print(json.dumps(product_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    products = get_all_product_urls()

    # Tes 5 produk dulu
    for i, product in enumerate(products[:5], start=1):
        print(f"\n📌 Scraping produk {i}: {product['URL']}")
        extra = scrape_product(product["URL"])
        product.update(extra)
        print(json.dumps(product, indent=2, ensure_ascii=False))
