import requests
import csv
import time
from bs4 import BeautifulSoup
import json
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


slug = "foundation-makeup"
base_url = f"https://www.sephora.com/api/v2/catalog/categories/{slug}/seo"

params = {
    "targetSearchEngine": "NLP",
    "currentPage": 1,
    "pageSize": 1,
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

# --- Ambil jumlah halaman ---
response = requests.get(base_url, headers=headers, params=params)
data = response.json()
# total_pages = 1  # Bisa kamu ubah nanti ke `data.get("totalPages", 1)` jika diketahui pasti
total_pages = 1
print(f"📄 Total Pages: {total_pages}\n{'='*60}")

all_data = []

# Set untuk melacak URL detail unik (menghindari duplikasi root product)
seen_detail_urls = set()

# Set untuk melacak URL SKU unik yang berhasil di-generate
seen_sku_urls = set()

for page in range(1, total_pages + 1):
    print(f"📄 Page: {page}")
    params["currentPage"] = page
    response = requests.get(base_url, headers=headers, params=params)
    products = response.json().get("products", [])

    for p in products:
        time.sleep(0.5)
        product_url = p.get("targetUrl")
        if not product_url:
            continue
            
        detail_url = f"https://www.sephora.com{product_url}"
        
        # 1. Cek & hilangkan jika detail_url produk utama duplikat
        if detail_url in seen_detail_urls:
            print(f"⏭️ Skip duplicate product URL: {detail_url}")
            continue
        seen_detail_urls.add(detail_url)

        print(f"🔗 url {detail_url}")

        try:
            time.sleep(0.1)
            res = requests.get(detail_url, headers=headers)
            time.sleep(0.2)
            soup = BeautifulSoup(res.text, "html.parser")
            time.sleep(0.8)
            script_tag = soup.find("script", {"id": "linkStore", "type": "text/json"})
            time.sleep(0.3)

            if not script_tag:
                print("❌ Script tag tidak ditemukan\n")
                continue

            data_json = json.loads(script_tag.string)
            product = data_json.get("page", {}).get("product", {})

            # Ambil semua skuId dari regularChildSkus
            sku_list = product.get("regularChildSkus", [])
            all_sku_ids = [sku.get("skuId") for sku in sku_list if sku.get("skuId")]
            
            # Parsing URL dasar untuk kebutuhan replace parameter query
            parsed_url = urlparse(detail_url)
            query_params = parse_qs(parsed_url.query)

            for sku_id in all_sku_ids:
                # Ganti parameter skuId dengan sku_id yang baru dari JSON
                query_params['skuId'] = [sku_id]
                
                # Bangun kembali URL baru dengan SKU ID yang sesuai
                new_query = urlencode(query_params, doseq=True)
                new_sku_url = urlunparse((
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    new_query,
                    parsed_url.fragment
                ))
                
                # 2. Cek & hilangkan jika URL SKU spesifik ini duplikat
                if new_sku_url not in seen_sku_urls:
                    seen_sku_urls.add(new_sku_url)
                    print("📦 SKU ID URL:", new_sku_url)

                    try:
                        time.sleep(0.1)
                        sku_res = requests.get(new_sku_url, headers=headers)
                        time.sleep(0.2)
                        soup_res = BeautifulSoup(sku_res.text, "html.parser")
                        time.sleep(0.8)
                        script_tag_res = soup_res.find("script", {"id": "linkStore", "type": "text/json"})
                        time.sleep(0.3)

                        if not script_tag_res:
                            print("❌ Script tag tidak ditemukan untuk SKU URL:", new_sku_url)
                            continue
                        data_json_res = json.loads(script_tag_res.string)
                        product_res = data_json_res.get("page", {}).get("product", {})



                        specific_category = product_res.get("parentCategory", {}).get("displayName")
                        product_id = product_res.get("productDetails", {}).get("productId")
                        sku_id = product_res.get("currentSku", {}).get("skuId")
                        product_brand = product_res.get("currentSku", {}).get("brandName")
                        product_desc = product_res.get("productDetails", {}).get("displayName")
                        product_image = f"https://www.sephora.com/productimages/sku/s{sku_id}-main-zoom.jpg?imwidth=1224"

                        # Ingredients cleanup
                        raw_ingredients = product_res.get("currentSku", {}).get("ingredientDesc")
                        if raw_ingredients:
                            ing_soup = BeautifulSoup(raw_ingredients, "html.parser")
                            for tag in ing_soup.find_all(["p", "br", "strong", "u"]):
                                tag.insert_after("\n")
                            clean_ingredients = "\n".join(
                                [line.strip() for line in ing_soup.get_text(separator="", strip=True).splitlines() if line.strip()]
                            )
                        else:
                            clean_ingredients = None

                        # Ingredients cleanup
                        raw_ingredients = product_res.get("currentSku", {}).get("ingredientDesc")
                        if raw_ingredients:
                            ing_soup = BeautifulSoup(raw_ingredients, "html.parser")

                            # Tambahkan newline di akhir setiap tag <p> agar masing-masing jadi 1 baris
                            for tag in ing_soup.find_all(["p", "br", "strong", "u"]):
                                tag.append("\n")

                            # Ambil teks dengan separator bawaan (\n otomatis dari append)
                            clean_ingredients = ing_soup.get_text().strip()

                            # Opsional: bersihkan baris kosong dan strip spasi
                            clean_ingredients = "\n\n".join(
                                line.strip() for line in clean_ingredients.splitlines() if line.strip()
                            )
                        else:
                            clean_ingredients = None


                        # Rating & review
                        seo_json_str = product_res.get("productSeoJsonLd", "")
                        rating, review_count = None, None

                        if isinstance(seo_json_str, str):
                            try:
                                seo_data = json.loads(seo_json_str)
                                aggregate_rating = seo_data.get("aggregateRating", {})
                                rating = aggregate_rating.get("ratingValue")
                                review_count = aggregate_rating.get("reviewCount")
                            except json.JSONDecodeError:
                                print("❌ Gagal decode SEO JSON")
                        
                        print("🆔 Product ID:", product_id)
                        print("⭐ Rating:", format_rating(rating))
                        print("📝 Review Count:", format_review_count(review_count))
                        print()

                        # Tambahkan ke list
                        all_data.append({
                            "Major Category": "major_category",
                            "Specific Category": specific_category,
                            "Product ID": product_id,
                            "SKU ID": sku_id,
                            "Product Brand": product_brand,
                            "Product Desc": product_desc,
                            "Product URL": detail_url,
                            "Product Image Link": product_image,
                            "Product Ingridents": clean_ingredients,
                            # "Rating": rating,
                            # "Review Count": review_count,
                            "Rating": format_rating(rating),
                            "User Reviews": format_review_count(review_count),
                        })
                    except Exception as e:
                        print(f"❌ Gagal memproses SKU URL {new_sku_url}: {e}")
                    

        except Exception as e:
            print(f"❌ Error saat memproses {detail_url}: {e}")



            # print("📦 Semua SKU ID:", all_sku_ids)



        except Exception as e:
            print(f"❌ Gagal mengambil detail produk: {e}")
            continue

    # Simpan ke CSV
filename = f"{slug}_products.csv"
with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
    writer.writeheader()
    writer.writerows(all_data)

print(f"\n✅ Data berhasil disimpan ke: {filename}")
