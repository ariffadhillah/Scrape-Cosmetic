import requests
import json
import csv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Konfigurasi
slug = "foundation-makeup"
base_url = f"https://www.sephora.com/api/v2/catalog/categories/{slug}/seo"
csv_filename = f"{slug}_products.csv"
csv_headers = [
    "Top-Level Category",
    "Category",
    "Product ID",
    "SKU ID",
    "Product Brand",
    "Product Desc",
    "Product URL",
    "Product Image",
    "price",
    "Ingredients",
    "Rating",
    "Review Count",
    "Formatted Rating",
    "Formatted Review Count"
]

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.sephora.com/",
}

# Format & Ekstraksi
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
        return f"{round(count / 1000, 1)}K" if count >= 1000 else str(count)
    except:
        return None

# Scraping detail produk
def scrape_all_product_details(product_urls):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for idx, relative_url in enumerate(product_urls, 1):
            detail_url = f"https://www.sephora.com{relative_url}"
            print(f"🔗 [{idx}/{len(product_urls)}] Mengakses: {detail_url}")

            try:
                page.goto(detail_url, timeout=60000)
                page.wait_for_selector("script#linkStore", timeout=10000, state="attached")
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                script_tag = soup.find("script", {"id": "linkStore", "type": "text/json"})

                if not script_tag:
                    print(f"⚠️ Script tag tidak ditemukan di {detail_url}")
                    continue

                json_data = json.loads(script_tag.string)
                product = json_data.get("page", {}).get("product", {})

                # Data pokok
                major_category = get_top_level_category(product.get("parentCategory", {}))
                category = product.get("parentCategory", {}).get("displayName")
                product_id = product.get("productDetails", {}).get("productId")
                sku_id = product.get("currentSku", {}).get("skuId")
                list_price = product.get("currentSku", {}).get("listPrice")
                brand = product.get("currentSku", {}).get("brandName")
                desc = product.get("productDetails", {}).get("displayName")
                image_link = f"https://www.sephora.com/productimages/sku/s{sku_id}-main-zoom.jpg?imwidth=1224"

                # Ingredients
                ingredients_raw = product.get("currentSku", {}).get("ingredientDesc")
                if ingredients_raw:
                    soup = BeautifulSoup(ingredients_raw, "html.parser")
                    for br in soup.find_all(["p", "br", "strong", "u"]):
                        br.insert_after("\n")
                    ingredients = "\n".join([line.strip() for line in soup.get_text(separator="", strip=True).splitlines() if line.strip()])
                else:
                    ingredients = None

                # Rating & review
                rating = None
                reviews = None
                seo_json_str = product.get("productSeoJsonLd", "")
                if isinstance(seo_json_str, str):
                    try:
                        seo_data = json.loads(seo_json_str)
                        rating = seo_data.get("aggregateRating", {}).get("ratingValue")
                        reviews = seo_data.get("aggregateRating", {}).get("reviewCount")
                    except json.JSONDecodeError:
                        print("❌ Gagal decode SEO JSON")

                results.append({
                    "Top-Level Category": major_category,
                    "Category": category,
                    "Product ID": product_id,
                    "SKU ID": sku_id,
                    "Product Brand": brand,
                    "Product Desc": desc,
                    "Product URL": detail_url,
                    "Product Image": image_link,
                    "price": list_price,
                    "Ingredients": ingredients,
                    "Rating": rating,
                    "Review Count": reviews,
                    "Formatted Rating": format_rating(rating),
                    "Formatted Review Count": format_review_count(reviews)
                })

            except Exception as e:
                print(f"❌ Gagal membuka {detail_url}: {e}")

        browser.close()
    return results

# Main logic: Ambil semua halaman
def main():
    print("📥 Mengambil halaman pertama untuk deteksi total pages...")
    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()

    total_pages = data.get("pageSize", 1)
    print(f"📄 Total Halaman: {total_pages}")

    all_product_urls = []

    for page_num in range(1, total_pages + 1):
        print(f"\n📄 Memproses halaman {page_num}/{total_pages}")
        params["currentPage"] = page_num
        response = requests.get(base_url, headers=headers, params=params)
        data = response.json()
        products = data.get("products", [])
        urls = [p.get("targetUrl", "") for p in products if p.get("targetUrl")]
        all_product_urls.extend(urls)

        # Scrape dan simpan tiap halaman
        results = scrape_all_product_details(urls)

        # Append atau buat CSV
        mode = "a" if page_num > 1 else "w"
        with open(csv_filename, mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            if page_num == 1:
                writer.writeheader()
            writer.writerows(results)

    print(f"\n✅ Selesai. Data disimpan ke {csv_filename}")

if __name__ == "__main__":
    main()
