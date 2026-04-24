import requests
import json
import time
import csv
from bs4 import BeautifulSoup

API_URL = "https://www.boots.com/online/api/search/v2/multiple-query/uk"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Referer": "https://www.boots.com/beauty/skincare/",
    "x-client-id": "9c5ed6f8b3d1ec6191ae260ae7daac",
    "x-search-usertoken": "457ce85f-b9f3-41b6-b132-08691f8ff0ec",
    "x-user-token": "457ce85f-b9f3-41b6-b132-08691f8ff0ec",
    "Origin": "https://www.boots.com",
}

# =========================
# Utility: Formatter
# =========================
def format_rating(rating):
    """Format angka rating jadi 1 desimal"""
    try:
        return f"{round(float(rating), 1)}"
    except Exception:
        return ''


def format_review_count(count):
    """Format jumlah review, kalau > 1000 tampilkan dalam ribuan (K)"""
    try:
        count = int(count)
        return f"{round(count / 1000, 1)} K" if count >= 1000 else str(count)
    except Exception:
        return ''



# =========================
# STEP 1: API → Ambil data dasar
# =========================
def get_all_product_urls():
    all_products = []
    page_index = 0
    page_size = 48
    total_products = None

    while True:
        # payload = {
        #     "query": "",
        #     "indices": {
        #         "products": {
        #             "paging": {"index": page_index, "size": page_size},
        #             "criteria": {
        #                 "category": [
        #                     "beauty & skincare",
        #                     "facial skincare",
        #                     "face moisturisers"
        #                 ]
        #             },
        #             "sortBy": "mostRelevant",
        #         }
        #     },
        #     "returnHits": True,
        #     "returnSuggestions": False,
        #     "returnFacets": True,
        #     "returnChanel": False,
        #     "searchRequired": True,
        #     "adRequired": True,
        #     "adParams": {
        #         "pageId": "viewCategoryApiDesktop",
        #         "eventType": "viewCategory",
        #         "environment": "desktop",
        #         "customerId": "",
        #         "category": "1595015>2139186>1595038>1595216",
        #     },
        # }


        payload = {
            "query": "",
            "indices": {
                "products": {
                    "paging": {"index": 0, "size": 48},
                    "criteria": {
                        "category": [
                            "fragrance",
                            "aftershave",
                            "shop all aftershave",
                            # "shop all premium & professional hair",
                        ]
                    },
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
                "category": "1595016>1595044>1595226",
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
            rating = product.get("reviews", {}).get("average")
            review_count = product.get("reviews", {}).get("count")

            product_data = {
                "Product Brand": product.get("brand"),
                "Product Desc": product.get("title"),
                "Rating": format_rating(rating),
                "User Reviews": format_review_count(review_count),
                "Product URL": f'https://www.boots.com{product.get("referenceUri")}',
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
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"❌ Gagal buka {url}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Product Code
        product_id_tag = soup.select_one("div#productId")
        product_id = product_id_tag.get_text(strip=True) if product_id_tag else None
        if product_id:
            product_id = f"'{product_id}"

        # SKU ID → ambil dari URL
        sku_id = url.split("-")[-1] if "-" in url else None
        if sku_id:
            sku_id = f"'{sku_id}"

        # Ingredients
        product_ingredients = get_sibling_text(soup, "Ingredients")

        # Image
        image_tag = soup.select_one('img[itemprop="image"]')
        product_image = image_tag["src"] if image_tag and image_tag.has_attr("src") else None

        major_category = "Fragrance"
        specific_category = "Aftershave"

        return {
            "Major Category": major_category,
            "Product ID": product_id,
            "SKU ID": sku_id,
            "Product Ingredients": product_ingredients,
            "Specific Category": specific_category,
            "Product Image Link": product_image,
        }
    except Exception as e:
        print(f"⚠️ Error scrape {url}: {e}")
        return None


# =========================
# STEP 3: Gabung + Simpan ke CSV
# =========================
def save_to_csv(products, filename="Fragrance-products-15.csv"):
    fieldnames = [ "Major Category", "Specific Category",  "Product ID", "SKU ID", "Product Brand", "Product Desc", "Product URL", "Product Image Link", "Product Ingredients", "Rating", "User Reviews" ]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

    print(f"📂 Data berhasil disimpan ke {filename}")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    products = get_all_product_urls()

    all_data = []
    # for i, product in enumerate(products, start=1):  # tes dulu 20 produk
    # for i, product in enumerate(products, start=1):  # tes dulu 20 produk
    #     print(f"\n📌 Scraping produk {i}/{len(products)}: {product['Product URL']}")
    #     extra = scrape_product(product["Product URL"])
    #     product.update(extra)
    #     all_data.append(product)


    for i, product in enumerate(products, start=1):
        print(f"\n📌 Scraping produk {i}/{len(products)}: {product['Product URL']}")
        extra = scrape_product(product["Product URL"])
        if not extra:  # kalau None, skip
            print(f"⚠️ Lewati produk {i} karena gagal scraping")
            continue
        product.update(extra)
        all_data.append(product)


    save_to_csv(all_data)
