import requests
import json
from bs4 import BeautifulSoup

slug = "foundation-makeup"
base_url = f"https://www.sephora.com/api/v2/catalog/categories/{slug}/seo"

params = {
    "targetSearchEngine": "NLP",
    "currentPage": 1,
    "pageSize": 1,  # Ambil 2 produk saja untuk testing cepat
    "content": "true",
    "includeRegionsMap": "true",
    "pickupRampup": "true",
    "sddRampup": "true",
    "includeEDD": "true",
    "loc": "en-US",
    "ch": "rwd"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.sephora.com/",
}

def get_top_level_category(category_data):
    while category_data.get("parentCategory"):
        category_data = category_data["parentCategory"]
    return category_data.get("displayName")

def format_rating(rating):
    try:
        return f"{round(float(rating), 1)}"
    except:
        return None

def format_review_count(count):
    try:
        count = int(count)
        return f"{round(count / 1000, 1)} K" if count >= 1000 else str(count)
    except:
        return None

# Get Catalog Page
response = requests.get(base_url, headers=headers, params=params)
products = response.json().get("products", [])

for p in products:
    product_url = p.get("targetUrl")
    detail_url = f"https://www.sephora.com{product_url}"
    print(f"\n==================================================")
    print(f"🔗 MENGAKSES PRODUK: {detail_url}")
    print(f"==================================================")

    try:
        res = requests.get(detail_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        script_tag = soup.find("script", {"id": "linkStore", "type": "text/json"})

        if not script_tag:
            print("❌ Script tag #linkStore tidak ditemukan")
            continue

        data_json = json.loads(script_tag.string)
        product = data_json.get("page", {}).get("product", {})

        # Meta Data Produk (Sama untuk semua SKU di produk ini)
        major_category = get_top_level_category(product.get("parentCategory", {}))
        specific_category = product.get("parentCategory", {}).get("displayName")
        product_id = product.get("productDetails", {}).get("productId")
        product_desc = product.get("productDetails", {}).get("displayName")
        product_brand = (
            product.get("productDetails", {}).get("brandName") or 
            product.get("currentSku", {}).get("brandName")
        )

        # Rating & Review
        seo_json_str = product.get("productSeoJsonLd", "")
        rating, review_count = None, None
        if isinstance(seo_json_str, str) and seo_json_str:
            try:
                seo_data = json.loads(seo_json_str)
                aggregate_rating = seo_data.get("aggregateRating", {})
                rating = aggregate_rating.get("ratingValue")
                review_count = aggregate_rating.get("reviewCount")
            except json.JSONDecodeError:
                pass

        # Ingredients Fallback
        raw_ingredients = (
            product.get("currentSku", {}).get("ingredientDesc") or 
            product.get("productDetails", {}).get("ingredientDesc")
        )
        clean_ingredients = None
        if raw_ingredients:
            ing_soup = BeautifulSoup(raw_ingredients, "html.parser")
            for tag in ing_soup.find_all(["p", "br", "strong", "u"]):
                tag.append("\n")
            clean_text = ing_soup.get_text().strip()
            clean_ingredients = "\n\n".join(
                line.strip() for line in clean_text.splitlines() if line.strip()
            )

        # Map tambahan data dari skuSelector jika ada
        sku_selector_list = product.get("skuSelector", {}).get("skus", [])
        sku_map = {item.get("skuId"): item for item in sku_selector_list if item.get("skuId")}

        # Ambil daftar seluruh SKU
        sku_list = product.get("regularChildSkus", [])
        print(f"📦 Total SKU ditemukan: {len(sku_list)}")

        # --- LOOPING TIAP SKU ID ---
        for idx, sku in enumerate(sku_list, 1):
            sku_id = sku.get("skuId")
            selector_info = sku_map.get(sku_id, {})

            # Ekstraksi Varian / Shade
            shade_variation = (
                sku.get("variationValue") or 
                selector_info.get("variationValue") or 
                sku.get("skuName")
            )
            shade_description = (
                sku.get("biography") or 
                selector_info.get("biography") or 
                sku.get("variationDescription")
            )
            price = sku.get("listPrice")
            sku_target_url = sku.get("targetUrl")
            full_sku_url = f"https://www.sephora.com{sku_target_url}" if sku_target_url else detail_url
            sku_image = f"https://www.sephora.com/productimages/sku/s{sku_id}-main-zoom.jpg?imwidth=1224"

            # Print hasil per SKU
            print(f"\n  --- [SKU {idx}/{len(sku_list)}] ---")
            print(f"  ID SKU             : {sku_id}")
            print(f"  Brand              : {product_brand}")
            print(f"  Nama Produk        : {product_desc}")
            print(f"  Shade / Varian     : {shade_variation}")
            print(f"  Shade Deskripsi    : {shade_description}")
            print(f"  Harga              : {price}")
            print(f"  URL SKU            : {full_sku_url}")
            print(f"  Gambar             : {sku_image}")

    except Exception as e:
        print(f"❌ Error memproses produk: {e}")