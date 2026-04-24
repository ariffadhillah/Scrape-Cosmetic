import requests
import json
import time
# from pagination import get_all_urls
import sys
# sys.path.append("E:/Scraping/Weather Station Metadata/Doctor/cosmetics/ultah/pagination")

from pagination_ import get_all_urls


BASE_GRAPHQL = "https://www.ulta.com/dxl/graphql"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "x-ulta-dxl-query-id": "Page",
    "x-ulta-client-locale": "en-US",
    "x-ulta-client-country": "US",
    "x-ulta-client-channel": "web",
    "x_ulta_site": "CA",
}

QUERY = """
query Page($url: JSON, $moduleParams: JSON) {
  Page(url: $url, moduleParams: $moduleParams) {
    content
    customResponseAttributes
    meta
    __typename
  }
}
"""


def fetch_graphql(url_path):
    payload = {
        "operationName": "Page",
        "query": QUERY,
        "variables": {"url": {"path": url_path}, "moduleParams": {}}
    }
    r = requests.post(BASE_GRAPHQL, headers=HEADERS, json=payload)
    return r.json()


def extract_product_detail(data):
    """Find ProductDetail block."""
    def search(x):
        if isinstance(x, dict):
            if x.get("type") == "ProductDetail":
                return x
            for v in x.values():
                found = search(v)
                if found:
                    return found
        elif isinstance(x, list):
            for item in x:
                found = search(item)
                if found:
                    return found
        return None
    return search(data)


def find_key(data, target_key):
    results = []
    def search(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k.lower() == target_key.lower():
                    results.append(v)
                search(v)
        elif isinstance(d, list):
            for v in d:
                search(v)
    search(data)
    return results


def scrape_ulta_product(product_url):
    # Fetch MAIN JSON (global)
    main_data = fetch_graphql(product_url)

    # ============ Extract all SKU IDs ============
    variant_lists = find_key(main_data, "variants")
    skus = []
    for lst in variant_lists:
        if isinstance(lst, list):
            for item in lst:
                if item.get("skuId"):
                    skus.append({
                        "productId": item.get("productId"),
                        "skuId": item.get("skuId"),
                        "name": item.get("name"),
                        "shadeDescription": item.get("shadeDescription"),
                        "variant_url": item.get("linkSelectAction", {}).get("url")
                    })

    # ============ Extract Global ProductDetail ============
    pd = extract_product_detail(main_data)
    global_description = pd.get("description") if pd else None
    global_usage = pd.get("usage") if pd else None
    global_ingredients = pd.get("ingredients") if pd else None

    # ============ Brand, rating, review count ============
    brand_vals = find_key(main_data, "brandName")
    brand_name = brand_vals[0] if brand_vals else None

    rating_vals = find_key(main_data, "product_rating")
    rating = rating_vals[0] if rating_vals else None

    review_vals = find_key(main_data, "product_reviews_count")
    review_count = review_vals[0] if review_vals else None

    # ---------------------------
    # 3b. Extract productName
    # ---------------------------
    name_vals = find_key(main_data, "productName")
    product_name = name_vals[0] if name_vals else None

    # ============ Category ============
    cat_vals = find_key(main_data, "product_category")
    def get_last(cat):
        if isinstance(cat, list): cat = cat[0]
        if isinstance(cat, str): return cat.split(":")[-1].strip()
        return None
    category = get_last(cat_vals[0]) if cat_vals else None

    # ============ Fetch PER SKU JSON ============
    final = []

    product_base_url = product_url.split("?")[0]

    for item in skus:
        sku = item["skuId"]

        # ===========================
        # Fetch SKU JSON (per-variant)
        # ===========================
        sku_json = fetch_graphql(f"{product_base_url}?sku={sku}")

        # ============= Extract price, description, usage, ingredients from SKU JSON =============
        sku_list_price = None
        sku_sale_price = None
        sku_description = None
        sku_usage = None
        sku_ingredients = None

        def search_all(d):
            nonlocal sku_list_price, sku_sale_price
            nonlocal sku_description, sku_usage, sku_ingredients

            if isinstance(d, dict):

                # --- PRICES ---
                if "listPrice" in d:
                    sku_list_price = d["listPrice"]
                if "salePrice" in d:
                    sku_sale_price = d["salePrice"]

                # --- DESCRIPTION BLOCKS (sometimes included per SKU) ---
                if "description" in d and isinstance(d["description"], str):
                    sku_description = d["description"]
                if "usage" in d and isinstance(d["usage"], str):
                    sku_usage = d["usage"]
                if "ingredients" in d and isinstance(d["ingredients"], str):
                    sku_ingredients = d["ingredients"]

                for v in d.values():
                    search_all(v)

            elif isinstance(d, list):
                for v in d:
                    search_all(v)

        search_all(sku_json)

        # Fallback ke global
        if not sku_description: sku_description = global_description
        if not sku_usage: sku_usage = global_usage
        if not sku_ingredients: sku_ingredients = global_ingredients

        # Image
        image_url = f"https://media.ulta.com/i/ulta/{sku}?w=1080&h=1080&fmt=auto"

        final.append({
            **item,
            "productName": product_name,
            "listPrice": sku_list_price,
            "salePrice": sku_sale_price,
            "description": sku_description,
            "usage": sku_usage,
            "ingredients": sku_ingredients,
            "brandName": brand_name,
            "rating": rating,
            "reviewCount": review_count,
            "category": category,
            "image": image_url
        })

        time.sleep(0.4)

    return final


# ======================
# RUN
# ======================
product_url = "https://www.ulta.com/p/vice-lip-bond-glossy-longwear-liquid-lipstick-pimprod2033818?sku=2598624"
product_url = get_all_urls()
results = scrape_ulta_product(product_url)
for r in results:
    print("\n--- SKU ---")
    print(r)



# for url in product_urls:
#     results = scrape_ulta_product(url)
#     print("\n--- HASIL PRODUK ---")
#     for r in results:
#         print(r)

# product_url = get_all_urls()

# product_url = product_url.split("https://www.ulta.com")[-1]
# product_url = "https://www.ulta.com" + product_url




# for url_ in product_url:
#     print(url_)
#     results_url = scrape_ulta_product(url_)
#     print(results_url)

#     # print("\n--- HASIL PRODUK ---")
#     # for r in results:
#     #     print(r)