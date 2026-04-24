import requests
import json
import time

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
        "variables": {
            "url": {"path": url_path},
            "moduleParams": {}
        }
    }
    
    r = requests.post(BASE_GRAPHQL, headers=HEADERS, json=payload)
    return r.json()


def extract_product_detail(data):
    """Cari blok ProductDetail."""
    def search(x):
        if isinstance(x, dict):
            if x.get("type") == "ProductDetail":
                return x
            for v in x.values():
                result = search(v)
                if result:
                    return result
        elif isinstance(x, list):
            for item in x:
                result = search(item)
                if result:
                    return result
        return None
    
    return search(data)


def find_key(data, target_key):
    """Recursive key finder."""
    results = []

    def search(d, path=""):
        if isinstance(d, dict):
            for k, v in d.items():
                new_path = f"{path}.{k}" if path else k
                if k.lower() == target_key.lower():
                    results.append(v)
                search(v, new_path)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                search(v, f"{path}[{i}]")

    search(data)
    return results


def scrape_ulta_product(product_url):
    # ---------------------------
    # 1. Fetch main page
    # ---------------------------
    main_data = fetch_graphql(product_url)

    # Ambil semua SKU dari JSON
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

    # ---------------------------
    # 2. Extract detail global (description, usage, ingredients)
    # ---------------------------
    pd = extract_product_detail(main_data)

    description = pd.get("description") if pd else None
    usage = pd.get("usage") if pd else None
    ingredients = pd.get("ingredients") if pd else None

    # ---------------------------
    # 3. Extract brand + rating
    # ---------------------------
    brand = find_key(main_data, "brandName")
    brand_name = brand[0] if brand else None

    rating = find_key(main_data, "product_rating")
    rating = rating[0] if rating else None

    review_count = find_key(main_data, "product_reviews_count")
    review_count = review_count[0] if review_count else None

    # ---------------------------
    # 4. Extract Category
    # ---------------------------
    def get_last_category(cat):
        if isinstance(cat, list):
            cat = cat[0]
        if isinstance(cat, str):
            return cat.split(":")[-1].strip()
        return None

    cats = find_key(main_data, "product_category")
    category = get_last_category(cats[0]) if cats else None

    # ---------------------------
    # 5. FETCH PRICE FOR EACH SKU
    # ---------------------------
    final = []

    for item in skus:
        sku = item["skuId"]

        variant_json = fetch_graphql(
            f"{product_url.split('?')[0]}?sku={sku}"
        )

        # Ambil harga dari JSON SKU
        list_price = None
        sale_price = None

        def find_price(d):
            nonlocal list_price, sale_price
            if isinstance(d, dict):
                if "listPrice" in d:
                    list_price = d["listPrice"]
                if "salePrice" in d:
                    sale_price = d["salePrice"]
                for v in d.values():
                    find_price(v)
            elif isinstance(d, list):
                for v in d:
                    find_price(v)

        find_price(variant_json)

        # Siapkan image SKU
        image_url = f"https://media.ulta.com/i/ulta/{sku}?w=1080&h=1080&fmt=auto"

        final.append({
            **item,
            "listPrice": list_price,
            "salePrice": sale_price,
            "description": description,
            "usage": usage,
            "ingredients": ingredients,
            "brandName": brand_name,
            "rating": rating,
            "reviewCount": review_count,
            "category": category,
            "image": image_url
        })

        time.sleep(0.4)  # aman supaya tidak diblok

    return final


# ======================
# RUN
# ======================
product_url = "https://www.ulta.com/p/vice-lip-bond-glossy-longwear-liquid-lipstick-pimprod2033818?sku=2598622"
results = scrape_ulta_product(product_url)

for r in results:
    print(r)
