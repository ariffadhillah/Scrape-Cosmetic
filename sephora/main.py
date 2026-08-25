import requests
import csv
import time

# Slug untuk kategori produk
slug = "foundation-makeup"
base_url = f"https://www.sephora.com/api/v2/catalog/categories/{slug}/seo"

# Parameter untuk request
params = {
    "targetSearchEngine": "NLP",
    "currentPage": 1,
    "pageSize": 60,
    "content": "true",
    "includeRegionsMap": "true",
    "pickupRampup": "true",
    "sddRampup": "true",
    "includeEDD": "true",
    "loc": "en-US",
    "ch": "rwd"
}

# Headers untuk request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.sephora.com/",
    "Origin": "https://www.sephora.com",
    "Connection": "keep-alive"
}

# Request pertama untuk mendapatkan total halaman
response = requests.get(base_url, headers=headers, params=params)
data = response.json()
total_pages = data.get("pageSize", 1)

print(f"Total Pages: {total_pages}")
print("=" * 60)

# List untuk menampung semua data produk
all_data = []

# Looping dari halaman 1 sampai total_pages
for page in range(1, total_pages + 1):
    print(f"📄 Page: {page}")
    params["currentPage"] = page
    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()

    products = data.get("products", [])

    for product in products:
        brand = product.get("brandName", "")
        name = product.get("displayName", "")
        product_url = product.get("targetUrl", "")
        product_id = product.get("productId", "")
        full_product_url = f"https://www.sephora.com{product_url}"

        # Ambil detail produk untuk SKU
        time.sleep(0.2)
        detail_url = f"https://www.sephora.com/api/v3/users/profiles/undefined/product/{product_id}"
        detail_response = requests.get(detail_url, headers=headers)
        time.sleep(0.2)

        if detail_response.status_code == 200:
            product_detail = detail_response.json()
            current_sku = product_detail.get("currentSku", {})
            sku_current = current_sku.get("skuId", "")

            regular_child_skus = product_detail.get("regularChildSkus", [])
            all_sku_ids = [sku.get("skuId") for sku in regular_child_skus if sku.get("skuId")]

        else:
            sku_current = ""
            all_sku_ids = []

        # Simpan data ke list
        all_data.append({
            "Category": slug,
            "Produk Id": product_id,
            "Product Desc": name,
            "Product Brand": brand,
            "Product Url": full_product_url,
            "SkuId (Current)": sku_current,
            "All SKU IDs": ", ".join(str(sku) for sku in all_sku_ids)
        })

        print(f"✔ {name} | {brand} | Produk Id: {product_id} | SKU Current: {sku_current} | Total SKUs: {len(all_sku_ids)}")

    # Hindari rate-limit
    time.sleep(2)

# Simpan ke CSV
csv_filename = f"{slug}_products.csv"
csv_headers = ["Category", "Produk Id", "Product Desc", "Product Brand", "Product Url", "SkuId (Current)", "All SKU IDs"]

with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(all_data)

print("\n✅ Data berhasil disimpan ke:", csv_filename)
