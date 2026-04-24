# import requests
# import json

# # =========================
# # 1. Fetch Data Ulta
# # =========================
# url = "https://www.ulta.com/dxl/graphql"

# payload = {
#     "operationName": "Page",
#     "query": """
#         query Page($url: JSON, $moduleParams: JSON) {
#           Page(url: $url, moduleParams: $moduleParams) {
#             content
#             customResponseAttributes
#             meta
#             __typename
#           }
#         }
#     """,
#     "variables": {
#         "url": {
#             "path": "https://www.ulta.com/p/all-nighter-waterproof-makeup-setting-spray-pimprod2053044?sku=2642048"
#         },
#         "moduleParams": {}
#     }
# }

# headers = {
#     "User-Agent": "Mozilla/5.0",
#     "Content-Type": "application/json",
#     "x-ulta-dxl-query-id": "Page",
#     "x-ulta-client-locale": "en-US",
#     "x-ulta-client-country": "US",
#     "x-ulta-client-channel": "web",
#     "x_ulta_site": "CA",
# }

# response = requests.post(url, headers=headers, json=payload)
# data = response.json()


# def extract_ulta_product(data):
#     """
#     Extract product details + variants + last category from ULTA GraphQL JSON.
#     Returns list of dicts (one per variant).
#     """

#     # =============================
#     # 1. Find ProductDetail block
#     # =============================
#     def find_product_detail(d):
#         result = []

#         def search(x):
#             if isinstance(x, dict):
#                 if x.get("type") == "ProductDetail":
#                     result.append(x)
#                 for v in x.values():
#                     search(v)
#             elif isinstance(x, list):
#                 for item in x:
#                     search(item)

#         search(d)
#         return result

#     product_detail_blocks = find_product_detail(data)

#     if product_detail_blocks:
#         pd = product_detail_blocks[0]
#         description = pd.get("description")
#         usage = pd.get("usage")
#         ingredients = pd.get("ingredients")
#     else:
#         description = usage = ingredients = None

#     # =============================
#     # 2. Generic key finder
#     # =============================
#     def find_key(d, target_key, path=""):
#         results = []
#         if isinstance(d, dict):
#             for key, value in d.items():
#                 new_path = f"{path}.{key}" if path else key
#                 if key.lower() == target_key.lower():
#                     results.append((new_path, value))
#                 results.extend(find_key(value, target_key, new_path))
#         elif isinstance(d, list):
#             for i, item in enumerate(d):
#                 new_path = f"{path}[{i}]"
#                 results.extend(find_key(item, target_key, new_path))
#         return results

#     # =============================
#     # 3. Extract LAST CATEGORY
#     # =============================
#     def get_last_category(cat):
#         """Ambil kategori terakhir. Bisa list atau string."""
#         if isinstance(cat, list) and cat:
#             cat = cat[0]
#         if isinstance(cat, str):
#             return cat.split(":")[-1].strip()
#         return None

#     category_results = find_key(data, "product_category")

#     last_category = None
#     for path, value in category_results:
#         last_category = get_last_category(value)
#         break  # cukup ambil pertama

#     # =============================
#     # 5. Extract brandName
#     # =============================
#     brand_name = None
#     brand_results = find_key(data, "brandName")

#     for path, value in brand_results:
#         brand_name = value
#         break   # ambil yang pertama saja

#     # =============================
#     # 6. Extract product_rating
#     # =============================
#     rating = None
#     rating_results = find_key(data, "product_rating")
#     for path, value in rating_results:
#         rating = value
#         break

#     # =============================
#     # 7. Extract product_reviews_count
#     # =============================
#     review_count = None
#     review_count_results = find_key(data, "product_reviews_count")
#     for path, value in review_count_results:
#         review_count = value
#         break


#     # =============================
#     # Extract product_sale_price
#     # =============================
#     product_sale_price = None
#     price_results = find_key(data, "product_sale_price")

#     for path, value in price_results:
#         product_sale_price = value
#         break



#     # =============================
#     # 4. Extract Variants
#     # =============================
#     variant_results = find_key(data, "variants")

#     final_items = []

#     for path, variants_list in variant_results:
#         if isinstance(variants_list, list):
#             for item in variants_list:
#                 sale_price = item.get("salePrice")
#                 sku_id = item.get("skuId")
#                 image_url = (
#                     f"https://media.ulta.com/i/ulta/{sku_id}?w=1080&h=1080&fmt=auto"
#                     if sku_id else None
#                 )

#                 final_items.append({
#                     "productId": item.get("productId"),
#                     "skuId": sku_id,
#                     "name": item.get("name"),
#                     "shadeDescription": item.get("shadeDescription"),
#                     "url": item.get("linkSelectAction", {}).get("url"),

#                     "description": description,
#                     "usage": usage,
#                     "ingredients": ingredients,
#                     "salePrice": sale_price,

#                     "category": last_category,
#                     "brandName": brand_name,

#                     "rating": rating,
#                     "reviewCount": review_count,

#                     "image": image_url,
#                     # "salePrice": product_sale_price,

#                 })

#     return final_items


# results = extract_ulta_product(data)

# for r in results:
#     print(r)


import requests
import json

# =========================
# 1. Fetch Data Ulta
# =========================
url = "https://www.ulta.com/dxl/graphql"

payload = {
    "operationName": "Page",
    "query": """
        query Page($url: JSON, $moduleParams: JSON) {
          Page(url: $url, moduleParams: $moduleParams) {
            content
            customResponseAttributes
            meta
            __typename
          }
        }
    """,
    "variables": {
        "url": {
            "path": "https://www.ulta.com/p/all-nighter-waterproof-makeup-setting-spray-pimprod2053044?sku=2642048"
        },
        "moduleParams": {}
    }
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "x-ulta-dxl-query-id": "Page",
    "x-ulta-client-locale": "en-US",
    "x-ulta-client-country": "US",
    "x-ulta-client-channel": "web",
    "x_ulta_site": "CA",
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()


def extract_ulta_product(data):
    """
    Extract product details + variants + last category from ULTA GraphQL JSON.
    Returns list of dicts (one per variant).
    """

    # =============================
    # 1. Find ProductDetail block
    # =============================
    def find_product_detail(d):
        result = []

        def search(x):
            if isinstance(x, dict):
                if x.get("type") == "ProductDetail":
                    result.append(x)
                for v in x.values():
                    search(v)
            elif isinstance(x, list):
                for item in x:
                    search(item)

        search(d)
        return result

    product_detail_blocks = find_product_detail(data)

    if product_detail_blocks:
        pd = product_detail_blocks[0]
        description = pd.get("description")
        usage = pd.get("usage")
        ingredients = pd.get("ingredients")
    else:
        description = usage = ingredients = None

    # =============================
    # 2. Generic key finder
    # =============================
    def find_key(d, target_key, path=""):
        results = []
        if isinstance(d, dict):
            for key, value in d.items():
                new_path = f"{path}.{key}" if path else key
                if key.lower() == target_key.lower():
                    results.append((new_path, value))
                results.extend(find_key(value, target_key, new_path))
        elif isinstance(d, list):
            for i, item in enumerate(d):
                new_path = f"{path}[{i}]"
                results.extend(find_key(item, target_key, new_path))
        return results

    # =============================
    # 3. Extract LAST CATEGORY
    # =============================
    def get_last_category(cat):
        if isinstance(cat, list) and cat:
            cat = cat[0]
        if isinstance(cat, str):
            return cat.split(":")[-1].strip()
        return None

    category_results = find_key(data, "product_category")

    last_category = None
    for path, value in category_results:
        last_category = get_last_category(value)
        break

    # =============================
    # 4. Extract brandName
    # =============================
    brand_name = None
    brand_results = find_key(data, "brandName")
    for path, value in brand_results:
        brand_name = value
        break

    # =============================
    # 5. Extract product_rating
    # =============================
    rating = None
    rating_results = find_key(data, "product_rating")
    for path, value in rating_results:
        rating = value
        break

    # =============================
    # 6. Extract product_reviews_count
    # =============================
    review_count = None
    review_count_results = find_key(data, "product_reviews_count")
    for path, value in review_count_results:
        review_count = value
        break

    # =============================
    # 7. UNIVERSAL PRICE FINDER
    # =============================
    def find_price_by_sku(d, sku):
        """
        Cari listPrice dan salePrice berdasarkan skuId.
        """
        found = {}

        def search(x):
            if isinstance(x, dict):
                if x.get("skuId") == sku:
                    if "listPrice" in x:
                        found["listPrice"] = x.get("listPrice")
                    if "salePrice" in x:
                        found["salePrice"] = x.get("salePrice")

                if "listPrice" in x and "salePrice" in x:
                    found.setdefault("listPrice", x.get("listPrice"))
                    found.setdefault("salePrice", x.get("salePrice"))

                for v in x.values():
                    search(v)

            elif isinstance(x, list):
                for item in x:
                    search(item)

        search(d)
        return found if found else {"listPrice": None, "salePrice": None}

    # =============================
    # 8. Extract Variants
    # =============================
    variant_results = find_key(data, "variants")

    final_items = []

    for path, variants_list in variant_results:
        if isinstance(variants_list, list):
            for item in variants_list:

                sku_id = item.get("skuId")

                # cari harga berdasarkan skuId
                price = find_price_by_sku(data, sku_id)

                # generate image url
                image_url = (
                    f"https://media.ulta.com/i/ulta/{sku_id}?w=1080&h=1080&fmt=auto"
                    if sku_id else None
                )

                final_items.append({
                    "productId": item.get("productId"),
                    "skuId": sku_id,
                    "name": item.get("name"),
                    "shadeDescription": item.get("shadeDescription"),
                    "url": item.get("linkSelectAction", {}).get("url"),

                    "listPrice": price["listPrice"],
                    "salePrice": price["salePrice"],

                    "description": description,
                    "usage": usage,
                    "ingredients": ingredients,

                    "category": last_category,
                    "brandName": brand_name,

                    "rating": rating,
                    "reviewCount": review_count,

                    "image": image_url,
                })

    return final_items


# =============================
# RUN
# =============================
results = extract_ulta_product(data)

for r in results:
    print(r)
