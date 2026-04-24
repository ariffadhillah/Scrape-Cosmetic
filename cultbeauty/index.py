import requests
import re
import json
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = "https://www.cultbeauty.co.uk"
CATEGORY_URL = BASE_URL + "/c/fragrance/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Connection": "keep-alive"
}

majorcategory = 'Fragrance'

fields = [
    "Major Category", "Specific Category", "Product ID", "SKU ID",
    "Product Brand", "Product Desc", "Product URL", "Product Image Link",
    "Product Ingredients", "Rating", "User Reviews"
]
data_save = []

filename = f'products_{majorcategory}.csv'

# ==============================
# 🔹 Utilities
# ==============================

def format_rating(rating):
    """Format angka rating jadi 1 desimal"""
    try:
        return f"{round(float(rating), 1)}"
    except Exception:
        return ''


def format_review_count(count):
    """Format jumlah review, kalau > 1000 tampilkan dalam ribuan (K)"""
    try:
        count = int(count)
        return f"{round(count / 1000, 1)} K" if count >= 1000 else str(count)
    except Exception:
        return ''


def get_soup(url):
    """Ambil halaman dan parsing ke BeautifulSoup"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print(f"✅ Status {response.status_code}: {url}")
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"❌ Error ambil URL: {e}")
        return None


# ==============================
# 🔹 Menu & Produk
# ==============================

def proses_menu_url(soup):
    """Cari kategori menu lalu proses setiap produk"""
    full_menu = soup.find("section", {"data-description": "FRAGRANCE-WEEK-LP-2025-CATEGORIES"})
    
    if not full_menu:
        print("❌ Menu utama tidak ditemukan")
        return []

    # cari semua div kategori di dalam section
    li_items = full_menu.find_all("div", class_="relative flex flex-col items-center image-card m-1")
    
    if not li_items:
        print("❌ Tidak ada item kategori ditemukan")
        return []

    # contoh: mulai dari item kedua
    for skincare_li in li_items[1:]:
        menu_title = skincare_li.find("a", class_="-outline-offset-[0.1vw]")
        if menu_title and menu_title.get("href"):
            url_li_items = BASE_URL + menu_title["href"]

            # ambil kategori dari URL
            category_slug = url_li_items.rstrip("/").split("/")[-1]
            category_name = category_slug.replace("-", " ").title()

            print(f"\n=== Category: {category_name} ===")
            print(f"URL: {url_li_items}")

            # kirim ke fungsi lain
            proses_menu_category(url_li_items)



# def proses_menu_url(soup):
#     """Cari kategori menu lalu proses setiap produk"""
#     full_menu = soup.find_all("section", {"class": "widgets mb-6 md:mb-12 customWidgetMargin"})
#     if not full_menu or len(full_menu) < 2:
#         print("❌ Menu utama tidak ditemukan")
#         return []

#     li_items = full_menu[1].find_all("div", class_="carousel-item")
#     if li_items:
#         # contoh: mulai dari item kedua
#         for skincare_li in li_items[1:]:
#             menu_title = skincare_li.find("a", class_="w-48 brand-logo-carousel-item")
#             if menu_title:
#                 url_li_items = BASE_URL + menu_title["href"]

#                 # ambil kategori dari URL
#                 category_slug = url_li_items.rstrip("/").split("/")[-1]
#                 category_name = category_slug.replace("-", " ").title()

#                 print(f"\n=== Category: {category_name} ===")
#                 print(f"URL: {url_li_items}")

#                 # kirim ke get_products dengan category_name
#                 # get_products(url_li_items, category_name)
#                 proses_menu_category(url_li_items)


# def proses_menu_category(baseurl):
#     res = requests.get(baseurl, headers=HEADERS)
#     soup = BeautifulSoup(res.text, "html.parser")
    
#     full_menu_category = soup.find("div", class_="categories overflow-x-auto flex gap-6 mb-12 p-1")
#     if not full_menu_category:
#         print("❌ Tidak menemukan div kategori")
#         return

#     menu_title_category = full_menu_category.find_all("a")
#     if not menu_title_category:
#         print("❌ Tidak menemukan link kategori")
#         return

#     for a in menu_title_category:
#         url_li_items__category = BASE_URL + a.get("href", "")
#         if not url_li_items__category:
#             continue

#         # ambil kategori dari URL
#         categoryslug = url_li_items__category.rstrip("/").split("/")[-1]
#         categoryname = categoryslug.replace("-", " ").title()

#         print(f"\n=== Sub Category: {categoryname} ===")
#         print(f"Sub URL: {url_li_items__category}")
#         get_products(url_li_items__category, categoryname)


def proses_menu_category(baseurl):
    res = requests.get(baseurl, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    
    full_menu_category = soup.find("div", class_="categories overflow-x-auto flex gap-6 mb-12 p-1")
    if not full_menu_category:
        print("❌ Tidak menemukan div kategori")
        return

    menu_title_category = full_menu_category.find_all("a")
    if not menu_title_category:
        print("❌ Tidak menemukan link kategori")
        return

    for a in menu_title_category:
        url_li_items__category = BASE_URL + a.get("href", "")
        if not url_li_items__category:
            continue

        # ambil text langsung dari <a>
        categoryname = a.get_text(strip=True)

        print(f"\n=== Sub Category: {categoryname} ===")
        print(f"Sub URL: {url_li_items__category}")
        get_products(url_li_items__category, categoryname)


def get_products(base_url, categoryname):
    """Loop semua halaman produk per kategori"""
    page = 1
    while True:
        url = f"{base_url}?pageNumber={page}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        scripts = soup.find_all("script", string=re.compile("trackingObj"))

        products_found = False
        for script in scripts:
            text = script.string
            if not text:
                continue
            match = re.search(r'const\s+trackingObj\s*=\s*(\{.*?\})\s*;', text, re.S)
            if match:
                try:
                    data = json.loads(match.group(1))
                    if data:
                        products_found = True
                        print(f"\n📄 Page {page} ({url})")
                        for pid, item in data.items():
                            product_url = BASE_URL + item.get("url", "")
                            process_product_url(product_url, categoryname)
                except Exception as e:
                    print("⚠️ Error parse JSON:", e)

        if not products_found:
            print(f"❌ Tidak ada produk di page {page}, stop.")
            break

        page += 1


# ==============================
# 🔹 Detail Produk
# ==============================

def process_product_url(product_url, categoryname):
    """Proses halaman detail produk"""
    print(f"\n🔎 Memproses produk: {product_url}")
    product_id = product_url.rstrip("/").split("/")[-1]
    soup = get_soup(product_url)
    if not soup:
        return

    # --- Brand ---
    brand_tag = soup.find("a", class_="block uppercase text-gray-500 text-sm tracking-widest title-font mb-2 cursor-pointer")
    brand_name = brand_tag.text.strip() if brand_tag else ""

    # --- Ingredients ---
    final_text = ""
    ingredients_container = soup.find("div", {"aria-labelledby": "Ingredients"})
    if ingredients_container:
        ingredients_div = ingredients_container.find("div", class_="attribute-content")
        if ingredients_div:
            paragraphs = ingredients_div.find_all("p")
            cleaned_texts = [p.get_text(strip=True) + "\n" for p in paragraphs]
            final_text = "\n".join(cleaned_texts).strip()

    # --- Reviews / Rating ---
    rating_value, review_count_value = None, None
    find_reviews = soup.find("script", {"type": "application/ld+json"})
    if find_reviews:
        try:
            data = json.loads(find_reviews.string)
            aggregate = data.get("aggregateRating", {})
            rating_value = format_rating(aggregate.get("ratingValue")) if aggregate else None
            review_count_value = format_review_count(aggregate.get("reviewCount")) if aggregate else None
        except Exception as e:
            print("⚠️ Error parse JSON reviews:", e)

    # --- Variasi Produk ---
    script_items = soup.find_all("script", string=re.compile("variationData"))
    for script_item in script_items:
        text_variationData = script_item.string
        if not text_variationData:
            continue

        match = re.search(r'const\s+variationData\s*=\s*(\[.*?\]);', text_variationData, re.S)
        if not match:
            continue

        try:
            data_items = json.loads(match.group(1))
            for item_product in data_items:
                if not isinstance(item_product, dict):
                    continue

                sku_id = item_product.get("sku")
                product_desc = item_product.get("title")
                url_product_items = f"{product_url}?variation={sku_id}"

                # ambil image
                images = item_product.get("images", [])
                product_image_raw = ""
                if isinstance(images, list) and images:
                    product_image_raw = images[0].get("original", "")
                product_image = f"https:{product_image_raw}" if str(product_image_raw).startswith("//") else product_image_raw

                # --- Simpan hasil ---
                save_csv = {
                    "Major Category": majorcategory,
                    "Specific Category": categoryname,
                    "Product ID": f"'{product_id}",
                    "SKU ID": f"'{sku_id}",
                    "Product Brand": brand_name,
                    "Product Desc": f"{product_desc}",
                    "Product URL": f"{url_product_items}",
                    "Product Image Link": product_image,
                    "Product Ingredients": final_text,
                    "Rating": f"'{rating_value}",
                    "User Reviews": f"'{review_count_value}"
                }

                data_save.append(save_csv)
                print('Saving', save_csv['Product ID'], save_csv['Product Desc'])
                time.sleep(1)

        except Exception as e:
            print("⚠️ Error parse variationData:", e)


# ==============================
# 🔹 Save ke CSV
# ==============================

def save_to_csv():
    """Simpan semua data ke CSV sekali saja"""
    if not data_save:
        print("❌ Tidak ada data untuk disimpan.")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data_save)

    print(f"\n✅ Data berhasil disimpan ke {filename} ({len(data_save)} baris)")


# ==============================
# 🔹 Main
# ==============================

def main():
    soup = get_soup(CATEGORY_URL)
    if soup:
        proses_menu_url(soup)
    save_to_csv()


if __name__ == "__main__":
    main()
