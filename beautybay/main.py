import requests
import json
import csv

majorcategory__ = 'bathandbody'
majorcategory = 'Bath & Body'


API_URL = f"https://lister-page-api.public.prd.beautybay.com/header?pageUrl=/l/{majorcategory__}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.beautybay.com/",
}

# === konfigurasi ===


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
    "Review",
    "User Reviews",
]
data_save = []               # akan berisi dict baris CSV
seen_rows = set()            # untuk dedup berdasarkan (product_url, sku_id)
filename = f'products_{majorcategory}.csv'


def parse_product_detail(json_detail):
    """
    Parse detail produk BeautyBay dari JSON API.
    Mengembalikan list dict dengan format konsisten.
    """

    results = []

    # --- data umum ---
    product_id = json_detail.get("sku", "")
    product_name = json_detail.get("name", "")
    brand = json_detail.get("brand", {}).get("name", "")
    measurement = json_detail.get("measurement", "")
    url_product_canonical = json_detail.get("seoData", {}).get("canonical","")
    ingredients = json_detail.get("ingredients", "")
    reviewSummary = json_detail.get("reviewSummary", {})
    reviewcount = reviewSummary.get("count", "")
    overallRating = reviewSummary.get("overallRating", "")

    # --- cek apakah ada variants ---
    variants = json_detail.get("variants")

    if isinstance(variants, dict) and ("inStock" in variants or "outOfStock" in variants):
        # Loop keduanya
        for stock_key in ["inStock", "outOfStock"]:
            if stock_key in variants:
                for data_variant in variants[stock_key]:
                    name_variant = data_variant.get("name", "")
                    measurement_variant = data_variant.get("measurement", "")
                    product_id = data_variant.get("sku")
                    url_variants = data_variant.get("url", "")
                    imageUrl = data_variant.get("imageUrl", "")

                    # --- susun product_desc ---
                    base_name = product_name
                    parts = [base_name]

                    if measurement_variant:
                        parts.append(measurement_variant)
                    if name_variant:
                        parts.append(name_variant)

                    # Gabungkan
                    product_desc = " ".join(parts)

                    # Hilangkan duplikat kata (misal "60ml 60ml")
                    tokens = product_desc.split()
                    seen = []
                    clean_tokens = []
                    for t in tokens:
                        if t not in seen:
                            clean_tokens.append(t)
                            seen.append(t)
                    product_desc = " ".join(clean_tokens)

                    results.append({
                        "brand": brand,
                        "product_id": product_id,
                        "product_desc": product_desc,
                        "image_url": imageUrl,
                        "url product canonical": f"{url_product_canonical}{url_variants}",
                        "stock_status": stock_key,  # inStock / outOfStock
                        "ingredients": ingredients,
                        "review": reviewcount,
                        "overallRating": overallRating
                    })
    else:
        # Produk tanpa variasi        
        image_list = json_detail.get("media", {}).get("images", [])
        first_image = image_list[0] if image_list else ""

        results.append({
            "brand": brand,
            "product_id": product_id,
            "product_desc": f"{product_name} {measurement}".strip(),
            "url_variants": "",
            "image_url": first_image,
            "url product canonical": url_product_canonical,
            "ingredients": ingredients,
            "review": reviewcount,
            "overallRating": overallRating,
            "stock_status": "unknown"
        })

    return results



def fetch_api_data():
    response = requests.get(API_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.json()

def get_category(data):
    # urls = []
    if "links" in data:
        for item in data["links"]:
            title = item.get("title", "")
            link_category = item.get("link")
            # ❌ skip kalau title "View All"
            if title.lower() == "view all":
                continue
            if link_category:
                if link_category.startswith("/"):
                    link_category = "https://lister-page-api.public.prd.beautybay.com/listings?pageUrl=" + link_category
                    get_specific_category(link_category)
                    # break


# def get_specific_category(link_category):
#     print(f"🔗 Fetching: {link_category}")
#     try:
#         response = requests.get(link_category, headers=HEADERS, timeout=10)
#         response.raise_for_status()
#         data_json = response.json()  
#         menuheader = data_json.get("header",{}).get("navigation",{})
#         name_items = menuheader.get("name","")
#         url_items = menuheader.get("url","")
#         print(name_items)
#         print(url_items)


#         # print(json.dumps(data_json, indent=2)[:2000])  # tampilkan sebagian dulu
#         return data_json
#     except Exception as e:
#         print(f"❌ Error fetch category: {e}")
#         return None


def get_specific_category(link_category):
    print(f"🔗 Fetching categoty: {link_category}")
    try:
        response = requests.get(link_category, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data_json = response.json()  

        header = data_json.get("header", {})
        navigation = header.get("navigation", [])

        for item in navigation:
            name_specific_category = item.get("name", "")
            uri = item.get("uri", "")
            if name_specific_category.lower() == "view all":  # skip View All
                continue
            full_url = "https://lister-page-api.public.prd.beautybay.com/listings?pageUrl=" + uri
            print(name_specific_category, "->", full_url)

            get_product_url(full_url, name_specific_category)
            # break

        return data_json
    except Exception as e:
        print(f"❌ Error fetch category: {e}")
        return None

def get_product_url(url_items, name_specific_category):
    print(f"🔗 test url: {url_items}")
    print(f"🔗 test name: {name_specific_category}")
    try:
        response = requests.get(url_items, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data_json_items = response.json()

        # total halaman
        total_pages = data_json_items.get("totalPages", 1)

        # loop semua halaman
        for page in range(1, total_pages + 1):
            page_url = f"{url_items}&page={page}"
            print(f"📄 Fetching page {page}/{total_pages} -> {page_url}")

            try:
                page_resp = requests.get(page_url, headers=HEADERS, timeout=15)
                page_resp.raise_for_status()
                page_data = page_resp.json()

                listerContent = page_data.get("listerContent", {})
                tiles = listerContent.get("tiles", {})
                content = tiles.get("content", [])

                for items in content:
                    productUrl = items.get("productUrl", "")
                    title = items.get("title", "")
                    if productUrl:
                        cleaned = productUrl.strip("/").split("/")
                        # contoh cleaned = ['p', 'maybelline', 'lash-sensational-sky-high-mascara', 'lash-sensational-sky-high-mascara']

                        if len(cleaned) >= 3:
                            # hanya ambil brand + slug pertama
                            final_slug = "-".join(cleaned[1:3])  
                            # print("name", title)
                            detail_product_url = f"https://pdp-api.public.prd.beautybay.com/product/{final_slug}"
                            # print("➡️", detail_product_url)
                            # print("➡️", "https://www.beautybay.com"+productUrl)
                            get_detail_product_url(detail_product_url, name_specific_category)
                            # break


            except Exception as e:
                print(f"❌ Error fetch page {page}: {e}")
            # break

        return data_json_items
    except Exception as e:
        print(f"❌ Error fetch category: {e}")
        return None

def get_detail_product_url(detail_product_url, name_specific_category):
    print(f"🔗 Page Detail: {detail_product_url}")
    try:
        response = requests.get(detail_product_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        json_detail = response.json()  

        # product_id = json_detail.get("parentProductId","")
        # product_name = json_detail.get("name","")
        # brand_raw = json_detail.get("brand", {}).get("name","")
        # # brand = brand_raw.get("", {})
        # print(product_id)
        # print(product_name)
        # print(brand_raw)


        # response = requests.get(url)
        # data = response.json()
        parsed = parse_product_detail(json_detail)

        for item in parsed:

            product_brand = item['brand']
            product_desc = item['product_desc']
            product_Id = item['product_id']
            sku_Id = item['product_id']
            url_Product = item['url product canonical']
            url_image = item['image_url']
            ingredients = item['ingredients']
            review = item['review']
            overall_rating = item['overallRating']
            # print(f"Stock Status: {item['stock_status']}")

            major_category = majorcategory.title()
            
            # print(f"Major Category: {major_category}")
            # print(f"Specific Category: {name_specific_category}")
            # print(f"Product Id: {product_Id}")
            # print(f"SKU Id: {sku_Id}")
            # print(f"Product Brand: {product_brand}")
            # print(f"Product Desc: {product_desc}")
            # print(f"Product URL: {url_Product}")
            # print(f"Product Image Link: {url_image}")
            # print(f"Product Ingredients: {ingredients}")
            # print(f"Review: {review}")
            # print(f"User Reviews: {overall_rating}")
            # # print(f"Stock Status: {item['stock_status']}")
            # print("="*80)

            row = {
                "Major Category": major_category,
                "Specific Category": name_specific_category,
                "Product ID": f"'{product_Id}",
                "SKU ID": f"'{sku_Id}",
                "Product Brand": product_brand or "",
                "Product Desc": product_desc or "",
                "Product URL": url_Product or "",
                "Product Image Link": url_image or "",
                "Product Ingredients": ingredients or "",
                "Review" :f"'{review}",
                "User Reviews" : f"'{overall_rating}"
            }
            data_save.append(row)
            print("✅ Row ditambahkan:", row["Product ID"], row["Product Desc"])


    except Exception as e:
        print(f"❌ Error fetch category: {e}")
        return None


def save_csv():
    if not data_save:
        print("⚠️ Tidak ada data untuk disimpan.")
        return
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in data_save:
                writer.writerow(row)
        print(f"\n✅ Selesai. {len(data_save)} baris tersimpan ke '{filename}'")
    except Exception as e:
        print(f"❌ Gagal menyimpan CSV: {e}")


def main():
    data = fetch_api_data()
    get_category(data)

    save_csv()

if __name__ == "__main__":
    main()

