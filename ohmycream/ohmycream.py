import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
major_category = 'fragrance'
specific_category = 'fragrance'
key_product = 'fragrance'
url_collections = 'https://ohmycream.co.uk/collections/'

BASE_URL = f"{url_collections}"
API_URL = f"{url_collections}{key_product}/products.json?page="



HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.ewg.org/",
    "Connection": "keep-alive"
}


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


# 1. Ambil JSON dari API
def get_json_data(page=1):
    try:
        url = API_URL + str(page)
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Gagal mengambil data JSON: {e}")
        return None

# 2. Ambil HTML dari halaman produk
def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Gagal mengambil HTML: {e}")
        return None

def parse_product_page(product_url, product_id):
    html = get_html(product_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    # --- Ambil Ingredients ---
    ingredients_container = soup.find("div", class_="ingredients__content")
    if ingredients_container:
        paragraphs = [p.get_text(" ", strip=True) for p in ingredients_container.find_all("p")]
        ingredients_text = "\n\n".join(paragraphs).capitalize()
        data["ingredients"] = ingredients_text
    else:
        data["ingredients"] = "Tidak ada ingredients"

    # --- Ambil Rating & Review dari Yotpo API ---
    url_rating = f"https://api-cdn.yotpo.com/v3/storefront/store/ZWnXgxtdLk7li8dJll4GCFCJZQZrU6qBwSnbyP6i/product/{product_id}/reviews?page=1&perPage=5&sort=date,smart_optimistic,images,badge,rating"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url_rating, headers=headers)
        if resp.status_code == 200:
            rating_data = resp.json().get("bottomline", {})
            data["rating"] = rating_data.get("averageScore", 0)
            data["review_count"] = rating_data.get("totalReview", 0)
        else:
            data["rating"] = 0
            data["review_count"] = 0
    except Exception as e:
        print(f"Error fetching rating: {e}")
        data["rating"] = 0
        data["review_count"] = 0

    return data

all_products = []

def process_all_pages():
    page = 1
    while True:
        print(f"\n=== Memproses halaman {page} ===")
        json_data = get_json_data(page)

        # Cek apakah produk kosong → hentikan loop
        if not json_data or not json_data.get("products"):
            print(f"Tidak ada data produk di halaman {page}. Selesai.")
            break

        # Proses produk di halaman ini
        process_products(page)

        # Lanjut ke halaman berikutnya
        page += 1

    # Simpan semua data ke CSV setelah semua halaman selesai
    df = pd.DataFrame(all_products)
    df.to_csv(f"{major_category}/hasil_scraping-{specific_category}.csv", index=False, encoding="utf-8-sig")
    print(f"\nData berhasil disimpan ke {major_category}/hasil_scraping-{specific_category}.csv")


def process_products(page=1):
    test_urlPage = f"{API_URL}{page}"
    print("Testing URL Page:", test_urlPage)
    json_data = get_json_data(page)
    if not json_data or "products" not in json_data:
        print("Data produk tidak ditemukan.")
        return

    for product in json_data["products"]:
        id_product = product.get("id")
        title = product.get("title")
        vendor = product.get("vendor")
        handle = product.get("handle")
        
        product_url = f"{BASE_URL}{key_product}/products/{handle}"

        # Ambil detail dari halaman produk (sekali saja)
        product_data = parse_product_page(product_url, id_product)
        ingredients = product_data["ingredients"] if product_data else "Tidak ada ingredients"

        # Loop setiap varian
        variants = product.get("variants", [])
        product_images = product.get("images", [])
        
        # Buat list URL unik dari images
        fallback_images = [img.get("src") for img in product_images if img.get("src")]
        fallback_images = list(dict.fromkeys(fallback_images))  # hapus duplikat

        # for i, variant in enumerate(variants):
        #     sku = variant.get("id")
        #     # cek apakah featured_image ada
        #     featured_image = variant.get("featured_image", {})
        #     image_url = featured_image.get("src") if featured_image else None

        #     # kalau featured_image kosong, ambil dari fallback_images
        #     if not image_url and i < len(fallback_images):
        #         image_url = fallback_images[i]  # fallback ke gambar sesuai urutan
        #     elif not image_url and fallback_images:
        #         image_url = fallback_images[0]  # kalau urutan habis, ambil gambar pertama

        #     variant_url = f"{product_url}?variant={variant.get('id')}"
        #     rating_value = format_rating(product_data["rating"]) if product_data else None
        #     review_count_value = format_review_count(product_data["review_count"]) if product_data else None

        #     # specific_category = key_product.replace('Make Up', '').replace('Hair', '').replace('').title()

        #     # Simpan ke list all_products
        #     all_products.append({
        #         "Major Category": major_category.replace('-', ' ').title(),
        #         "Specific Category": specific_category,
        #         "Product ID": f"'{id_product}",
        #         "SKU ID": f"'{sku}",
        #         "Product Brand": vendor.replace('_', ' '),
        #         "Product Desc": title,
        #         "Product URL": variant_url,
        #         "Product Image Link": image_url,
        #         "Product Ingredients": ingredients,
        #         "Rating": f"'{rating_value.replace('0.0', '') if rating_value else None}",
        #         "User Reviews": review_count_value
        #     })

        for i, variant in enumerate(variants):
            sku = variant.get("id")

            # Ambil featured_image kalau ada
            featured_image = variant.get("featured_image", {})
            image_url = featured_image.get("src") if featured_image else None

            # Kalau featured_image kosong → ambil dari fallback_images
            if not image_url:
                if i < len(fallback_images):
                    image_url = fallback_images[i]  # gambar sesuai urutan varian
                elif fallback_images:
                    image_url = fallback_images[0]  # default: gambar pertama

            variant_url = f"{product_url}?variant={sku}"
            rating_value = format_rating(product_data["rating"]) if product_data else None
            review_count_value = format_review_count(product_data["review_count"]) if product_data else None

            all_products.append({
                "Major Category": major_category.replace('-', ' ').title(),
                "Specific Category": specific_category,
                "Product ID": f"'{id_product}",
                "SKU ID": f"'{sku}",
                "Product Brand": vendor.replace('_', ' '),
                "Product Desc": title,
                "Product URL": variant_url,
                "Product Image Link": image_url,
                "Product Ingredients": ingredients,
                "Rating": f"'{rating_value.replace('0.0', '') if rating_value else None}",
                "User Reviews": review_count_value
            })



def main():
    process_all_pages()


if __name__ == "__main__":
    main()




# def process_all_pages():
#     page = 1
#     while True:
#         print(f"\n=== Memproses halaman {page} ===")
#         json_data = get_json_data(page)

#         # Cek apakah produk kosong → hentikan loop
#         if not json_data or not json_data.get("products"):
#             print(f"Tidak ada data produk di halaman {page}. Selesai.")
#             break

#         # Proses produk di halaman ini
#         process_products(page)

#         # Lanjut ke halaman berikutnya
#         page += 1







# def process_products(page=1):
#     test_urlPage = f"{API_URL}{page}"
#     print("Testing URL Page:", test_urlPage)
#     json_data = get_json_data(page)
#     if not json_data or "products" not in json_data:
#         print("Data produk tidak ditemukan.")
#         return

#     for product in json_data["products"]:
#         id_product = product.get("id")
#         title = product.get("title")
#         vendor = product.get("vendor")
#         handle = product.get("handle")
#         product_url = f"{BASE_URL}{key_product}/products/{handle}"
#         # print(title)
#         # Ambil detail dari halaman produk (sekali saja)
#         product_data = parse_product_page(product_url, id_product)
#         ingredients = product_data["ingredients"] if product_data else "Tidak ada ingredients"

#         # Loop setiap varian
#         variants = product.get("variants", [])
#         product_images = product.get("images", [])
        
#         # Buat list URL unik dari images
#         fallback_images = [img.get("src") for img in product_images if img.get("src")]
#         fallback_images = list(dict.fromkeys(fallback_images))  # hapus duplikat

#         for i, variant in enumerate(variants):
#             sku = variant.get("id")
#             # cek apakah featured_image ada
#             featured_image = variant.get("featured_image", {})
#             image_url = featured_image.get("src") if featured_image else None

#             # kalau featured_image kosong, ambil dari fallback_images
#             if not image_url and i < len(fallback_images):
#                 image_url = fallback_images[i]  # fallback ke gambar sesuai urutan
#             elif not image_url and fallback_images:
#                 image_url = fallback_images[0]  # kalau urutan habis, ambil gambar pertama


#             variant_url = f"{product_url}?variant={variant.get('id')}"
#             rating_value = format_rating(product_data["rating"]) if product_data else None
#             review_count_value = format_review_count(product_data["review_count"]) if product_data else None

#             specific_category = key_product.replace('-', ' ').replace(major_category, '').title()
            

#             print(f"Major Category: {major_category.title()}")
#             print(f"Specific Category: {specific_category}")
#             print(f"Product ID: {id_product}")
#             print(f"SKU ID: {sku}")
#             print(f"Product Brand: {vendor}")
#             print(f"Product Desc: {title}")
#             print(f"Product URL: {variant_url}")
#             print(f"Product Image Link: {image_url}")
#             print(f"Product Ingredients: {ingredients}")
#             print("Rating:", rating_value.replace('0.0', ''))
#             print("User Reviews:", review_count_value)
#             # print(f"URL: {product_url}")
#             print("-" * 50)  # pemisah antar varian



# def main():
#     process_all_pages()


# if __name__ == "__main__":
#     main()





# import requests
# import pandas as pd
# from bs4 import BeautifulSoup

# Simpan semua hasil scraping di list
