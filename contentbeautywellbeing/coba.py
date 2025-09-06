import requests
import re
import json
import time
import csv
from bs4 import BeautifulSoup

BASE_URL = "https://www.contentbeautywellbeing.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Connection": "keep-alive"
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"❌ Error mengambil URL: {e}")
        return None

def extract_json_object(text, start_pos=0):
    """
    Cari objek JSON pertama yang berpasangan kurung kurawal dari posisi start_pos.
    Mengembalikan substring JSON (termasuk kurung kurawal) atau None.
    """
    i = text.find('{', start_pos)
    if i == -1:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == '{':
            depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0:
                return text[i:j+1]
    return None

def get_section_text(soup, section_title):
    """
    Mengambil teks dari collapsible section berdasarkan judul (summary).
    Mengembalikan teks gabungan atau None.
    """
    details_tags = soup.find_all("details")
    for details in details_tags:
        summary_tag = details.find("summary")
        if summary_tag and summary_tag.get_text(strip=True) == section_title:
            content_div = details.find("div", class_="collapsible__content")
            if content_div:
                return content_div.get_text(separator="\n", strip=True)
    return None

def proses_menu_url(soup):
    """
    Kembalikan tuple (list_of_urls, major_category)
    """
    full_menu = soup.find("ul", class_="thb-full-menu")
    if not full_menu:
        print("Menu utama tidak ditemukan")
        return [], None

    li_items = full_menu.find_all("li", recursive=False)

    if len(li_items) >= 5:
        skincare_li = li_items[4]  # li ke-5 (index 4)
        menu_title = skincare_li.find("a", class_="thb-full-menu--link")
        major_category = menu_title.get_text(strip=True) if menu_title else None

        all_urls = []
        submenus = skincare_li.find_all("ul")
        for submenu in submenus:
            for a in submenu.find_all("a"):
                href = a.get("href") or ""
                if href.startswith("http"):
                    url_li_items = href
                else:
                    url_li_items = f"{BASE_URL}{href}"
                all_urls.append(url_li_items)
        return all_urls, major_category
    else:
        print("Menu yang dicari tidak ditemukan (periksa index li).")
        return [], None

def process_product_url(product_url, major_category=None):
    """
    Mengembalikan list of dict untuk setiap variant pada product_url.
    Menerima major_category yang didapat dari menu.
    """
    print(f"\nMemproses produk: {product_url}")
    soup_product = get_soup(product_url)
    if not soup_product:
        print(f"Gagal mengambil data produk dari {product_url}")
        return []

    # Specific category dari breadcrumbs
    breadcrumbs = soup_product.select("nav.breadcrumbs a")
    specific_category = breadcrumbs[-1].get_text(strip=True) if len(breadcrumbs) >= 3 else None

    # Ingredients (menggunakan helper)
    ingredients_text = get_section_text(soup_product, "Ingredients")

    # Cari script yang berisi web-pixels-manager-setup
    script_tag = soup_product.find("script", id="web-pixels-manager-setup")
    if not script_tag:
        print("❌ Script web-pixels-manager-setup tidak ditemukan")
        return []

    script_content = script_tag.string or script_tag.get_text()
    if not script_content:
        print("❌ Script kosong")
        return []

    # Temukan posisi kata 'initData:' lalu ekstrak objek JSON lengkap setelahnya
    idx = script_content.find('initData:')
    raw_json = None
    if idx != -1:
        # pos setelah 'initData:'
        raw_json = extract_json_object(script_content, idx + len('initData:'))
    else:
        # fallback: mencari pattern umum dengan regex (kurang reliable)
        m = re.search(r'initData:\s*({.*?})\s*,\s*["\']', script_content, re.DOTALL)
        if m:
            raw_json = m.group(1)

    if not raw_json:
        print("❌ Tidak ada JSON initData ditemukan")
        return []

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"❌ Gagal parsing JSON: {e}")
        return []

    product_variants = data.get("productVariants", [])
    if not product_variants:
        print("Tidak ada productVariants di JSON")
        return []

    results = []
    for variant in product_variants:
        product = variant.get("product", {})
        price = variant.get("price", {})

        product_id = product.get("id", "")
        sku_id = variant.get("id", "")
        product_brand = product.get("vendor", "")
        product_title = product.get("title", "")
        variant_title = variant.get("title", "")
        product_url_full = f"{BASE_URL}{product.get('url')}?variant={variant.get('id')}" if product.get("url") and variant.get("id") else None
        product_image_raw = variant.get("image", {}).get("src", "")
        product_image = f"https:{product_image_raw}" if product_image_raw.startswith("//") else product_image_raw

        item = {
            "major_category": major_category,
            "specific_category": specific_category,
            "product_id": product_id,
            "variant_id": sku_id,
            "brand": product_brand,
            "product_title": product_title,
            "variant_title": variant_title,
            "sku": variant.get("sku"),
            "price": price.get("amount"),
            "currency": price.get("currencyCode"),
            "url": product_url_full,
            "image": product_image,
            "ingredients": ingredients_text
        }
        results.append(item)

        # cetak ringkasan (opsional)
        # print(f"Major Category: {major_category}")
        # print(f"Specific Category: {specific_category}")
        print(f"Product ID: {product_id}")
        # print(f"Variant ID: {sku_id}")
        print(f"Brand: {product_brand}")
        print(f"Title: {product_title} / {variant_title}")
        # print(f"URL: {product_url_full}")
        # print(f"Image: {product_image}")
        # print("Ingredients:")
        # print(ingredients_text if ingredients_text else "Ingredients tidak ditemukan")
        # print("-" * 40)
        print()

    return results

def url_all_items(url_list, major_category=None):
    all_products = []
    total = len(url_list)
    print(f"Total category links: {total}")

    for url_items in url_list:
        print(f"\nMemproses halaman kategori: {url_items}")
        soup_items = get_soup(url_items)
        if not soup_items:
            print(f"Gagal mengambil data dari {url_items}")
            continue

        find_items = soup_items.find("ul", id="product-grid")
        if not find_items:
            print("Tidak ada item ditemukan pada halaman kategori ini.")
            continue

        # loop semua produk di page tersebut
        for a in find_items.find_all("a", class_="product-card-title"):
            href = a.get("href")
            if not href:
                continue
            product_url = f"{BASE_URL}{href}" if href.startswith("/") else href
            product_results = process_product_url(product_url, major_category)
            if product_results:
                all_products.extend(product_results)

        # jika pagination perlu ditangani, kamu bisa tambahkan logika untuk next page di sini

    print(f"\nTotal produk yang berhasil diproses: {len(all_products)}")
    return all_products

def main():
    soup = get_soup(BASE_URL)
    if not soup:
        return

    url_list, major_category = proses_menu_url(soup)
    print(f"Major category dari menu: {major_category}")
    all_products = url_all_items(url_list, major_category)

    # contoh: simpan ke CSV
    if all_products:
        keys = all_products[0].keys()
        with open(f"products_{major_category}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_products)
        print(f"Data disimpan ke products_{major_category}.csv")

if __name__ == "__main__":
    main()
