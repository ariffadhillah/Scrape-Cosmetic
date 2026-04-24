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
            "path": "https://www.ulta.com/p/vice-lip-bond-glossy-longwear-liquid-lipstick-pimprod2033818?sku=2598624"
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


# =========================
# 2. Generic recursive finder
# =========================
def find_key(data, target_key, path=""):
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key

            if key.lower() == target_key.lower():
                results.append((new_path, value))

            results.extend(find_key(value, target_key, new_path))

    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{path}[{i}]"
            results.extend(find_key(item, target_key, new_path))

    return results


# =========================
# 3. Extract Variants
# =========================
variant_results = find_key(data, "variants")

print("\n===== VARIANTS =====")

if not variant_results:
    print("Tidak ditemukan key 'variants'")
else:
    print("Jumlah blok variants:", len(variant_results))

    for path, variants_list in variant_results:
        print("\n--- PATH:", path)

        if isinstance(variants_list, list):
            for item in variants_list:
                print({
                    "productId": item.get("productId"),
                    "skuId": item.get("skuId"),
                    "name": item.get("name"),
                    "shadeDescription": item.get("shadeDescription"),
                    "url": item.get("linkSelectAction", {}).get("url")
                })


# =========================
# 4. Extract Ingredients
# =========================
ingredient_results = find_key(data, "ingredients")

print("\n===== INGREDIENTS =====")

if not ingredient_results:
    print("Ingredients tidak ditemukan")
else:
    for path, value in ingredient_results:
        print("\n--- PATH:", path)
        print("VALUE:", value)


# =========================
# 5. Extract Description
# =========================
description_results = find_key(data, "description")

print("\n===== DESCRIPTION =====")

if not description_results:
    print("Description tidak ditemukan")
else:
    for path, value in description_results:
        print("\n--- PATH:", path)
        print("VALUE:", value)

# =========================
# 6. Extract usage
# =========================
usage_results = find_key(data, "usage")

print("\n===== usage =====")

if not usage_results:
    print("usage tidak ditemukan")
else:
    for path, value in usage_results:
        print("\n--- PATH:", path)
        print("VALUE:", value)



def get_last_category(cat_string):
    if not isinstance(cat_string, str):
        return None
    parts = cat_string.split(":")
    return parts[-1].strip() if parts else None


category_results = find_key(data, "product_category")

for path, value in category_results:
    last_cat = get_last_category(value)
    print("Kategori terakhir:", last_cat)


def get_last_category_from_list(cat):
    if isinstance(cat, list):
        return cat[-1]
    if isinstance(cat, str):
        return cat.split(":")[-1].strip()
    return None

