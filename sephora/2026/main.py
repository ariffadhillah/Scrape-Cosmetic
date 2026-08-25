import requests
import csv
import time
import random
from bs4 import BeautifulSoup

slug = "foundation-makeup"
base_url = f"https://www.sephora.com/api/v2/catalog/categories/{slug}/seo"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

session = requests.Session()

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.sephora.com/",
        "Origin": "https://www.sephora.com",
        "Connection": "keep-alive"
    }

def clean_html_text(raw_html):
    """Pembersih HTML tag untuk Ingredients & Description"""
    if not raw_html:
        return ""
    ing_soup = BeautifulSoup(raw_html, "html.parser")
    for tag in ing_soup.find_all(["p", "br", "strong", "u", "li"]):
        tag.append("\n")
    clean_text = ing_soup.get_text().strip()
    return "\n\n".join(line.strip() for line in clean_text.splitlines() if line.strip())

def format_rating(rating):
    try:
        return f"{round(float(rating), 1)}" if rating else ""
    except:
        return ""

def format_review_count(count):
    try:
        count = int(count)
        return f"{round(count / 1000, 1)} K" if count >= 1000 else str(count)
    except:
        return ""

# Initial Request
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

try:
    response = session.get(base_url, headers=get_headers(), params=params, timeout=10)
    data = response.json()
    total_pages = data.get("totalPages", 1)
except Exception as e:
    print(f"❌ Error request awal: {e}")
    exit()

print(f"📄 Total Pages: {total_pages}")
print("=" * 70)

all_data = []

for page in range(1, total_pages + 1):
    print(f"\n📄 Page: {page}")
    params["currentPage"] = page
    
    if page > 1:
        page_delay = random.uniform(3.0, 5.0)
        print(f"⏳ Jeda ganti halaman {page_delay:.2f} detik...")
        time.sleep(page_delay)
        
        res = session.get(base_url, headers=get_headers(), params=params, timeout=10)
        if res.status_code != 200:
            print(f"⚠️ Warning: Page {page} Error Status {res.status_code}")
            continue
        data = res.json()

    products = data.get("products", [])

    for prod_idx, product in enumerate(products, start=1):
        time.sleep(random.uniform(0.5, 1.0))  # Delay per product untuk mengurangi risiko rate limit
        product_id = product.get("productId", "")
        
        cat_brand = product.get("brandName", "")
        cat_name = product.get("displayName", "")
        cat_rating = product.get("rating", "")
        cat_reviews = product.get("reviews", "")

        time.sleep(random.uniform(1.2, 2.5))

        detail_url = f"https://www.sephora.com/api/v3/users/profiles/undefined/product/{product_id}"
        
        try:
            detail_response = session.get(detail_url, headers=get_headers(), timeout=10)
            
            if detail_response.status_code in [403, 429]:
                print(f"🛑 Terdeteksi Rate Limit ({detail_response.status_code})! Cooling down 30d...")
                time.sleep(30)
                continue

            if detail_response.status_code != 200:
                print(f"❌ Gagal ambil detail Product ID: {product_id}")
                continue

            product_detail = detail_response.json()
            
            # --- BRAND & NAME ---
            product_brand = (
                product_detail.get("brand", {}).get("displayName") or 
                product_detail.get("brandName") or 
                cat_brand
            )
            product_name = (
                product_detail.get("displayName") or 
                product_detail.get("productName") or 
                cat_name
            )

            # --- CATEGORIES ---
            parent_cat = product_detail.get("parentCategory", {})
            specific_category = parent_cat.get("displayName", slug) if isinstance(parent_cat, dict) else slug
            
            major_cat_obj = parent_cat.get("parentCategory", {}) if isinstance(parent_cat, dict) else {}
            major_category = major_cat_obj.get("displayName", "Makeup") if isinstance(major_cat_obj, dict) else "Makeup"

            # --- RATING & REVIEWS ---
            rating_val = product_detail.get("rating") or cat_rating
            reviews_val = product_detail.get("reviews") or cat_reviews
            rating = format_rating(rating_val)
            reviews = format_review_count(reviews_val)

            # --- EXTRACT INGREDIENTS DARI BERBAGAI LEVEL ROOT ---
            global_ingredients = (
                product_detail.get("ingredientDesc") or 
                product_detail.get("ingredients") or 
                product_detail.get("currentSku", {}).get("ingredientDesc") or 
                product_detail.get("productDetails", {}).get("ingredientDesc") or 
                ""
            )

            # --- MAPPING SKU SELECTOR (Lokasi Shade & Description Sebenarnya) ---
            sku_selector_list = product_detail.get("skuSelector", {}).get("skus", [])
            sku_map = {}
            for s_item in sku_selector_list:
                s_id = s_item.get("skuId")
                if s_id:
                    sku_map[s_id] = s_item

            child_skus = product_detail.get("regularChildSkus", [])

            print(f"\n📦 [{prod_idx}/{len(products)}] {product_brand} - {product_name} | Total SKUs: {len(child_skus)}")

            for index, sku in enumerate(child_skus, start=1):
                time.sleep(random.uniform(0.5, 1.0))
                sku_id = sku.get("skuId", "")
                
                # Pengecekan data dari skuSelector Map
                selector_data = sku_map.get(sku_id, {})
                
                # --- EXTRACT SHADE / VARIATION ---
                variation_value = (
                    sku.get("variationValue") or 
                    selector_data.get("variationValue") or 
                    sku.get("skuName") or 
                    selector_data.get("skuName") or 
                    sku.get("variationType") or 
                    ""
                )

                # --- EXTRACT SHADE DESCRIPTION ---
                variation_desc = (
                    sku.get("biography") or 
                    selector_data.get("biography") or 
                    sku.get("variationDescription") or 
                    selector_data.get("variationDescription") or 
                    selector_data.get("description") or 
                    ""
                )
                
                price = sku.get("listPrice", "")
                sale_price = sku.get("valuePrice", price)
                is_out_of_stock = sku.get("isOutOfStock", False)
                
                target_path = sku.get("targetUrl", "")
                sku_url = f"https://www.sephora.com{target_path}" if target_path else ""

                # --- EXTRACT SKU IMAGE ---
                sku_images = sku.get("skuImages") or selector_data.get("skuImages", {})
                image_url = ""
                if isinstance(sku_images, dict):
                    image_url = sku_images.get("image1500") or sku_images.get("image250") or ""
                elif isinstance(sku_images, str):
                    image_url = sku_images

                if image_url and not image_url.startswith("http"):
                    image_url = f"https://www.sephora.com{image_url}"

                # --- EXTRACT INGREDIENTS SPECIFIC PER SKU ---
                sku_raw_ing = (
                    sku.get("ingredientDesc") or 
                    selector_data.get("ingredientDesc") or 
                    global_ingredients
                )
                clean_ingredients = clean_html_text(sku_raw_ing)

                row = {
                    "Major Category": major_category,
                    "Specific Category": specific_category,
                    "Product ID": product_id,
                    "Product Brand": product_brand,
                    "Product Name": product_name,
                    "SKU Index": f"{index}/{len(child_skus)}",
                    "SKU ID": sku_id,
                    "Shade / Variation": variation_value,
                    "Shade Description": variation_desc,
                    "Price": price,
                    "Sale Price": sale_price,
                    "Out Of Stock": is_out_of_stock,
                    "Rating": rating,
                    "User Reviews": reviews,
                    "Product Ingredients": clean_ingredients,
                    "SKU Image URL": image_url,
                    "SKU URL": sku_url
                }

                all_data.append(row)

                print(f"   └─ [SKU {index}/{len(child_skus)}] ID: {sku_id} | Shade: {variation_value[:30]} | Price: {price}")
                
                time.sleep(random.uniform(0.01, 0.03))

        except Exception as e:
            print(f"❌ Error Produk {product_id}: {e}")

        if prod_idx % 10 == 0:
            pause = random.uniform(5.0, 8.0)
            print(f"\n☕ Cooling down batch... Istirahat {pause:.2f} detik")
            time.sleep(pause)

# Simpan ke CSV
csv_filename = f"{slug}_skus_fixed_v2.csv"
csv_headers = [
    "Major Category", "Specific Category", "Product ID", "Product Brand", "Product Name", 
    "SKU Index", "SKU ID", "Shade / Variation", "Shade Description", "Price", "Sale Price", 
    "Out Of Stock", "Rating", "User Reviews", "Product Ingredients", "SKU Image URL", "SKU URL"
]

with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(all_data)

print(f"\n✅ Selesai! Total {len(all_data)} varian SKU berhasil disimpan ke {csv_filename}")