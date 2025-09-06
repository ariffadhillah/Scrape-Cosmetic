import requests
import re
import json
import time
import csv
import math
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

majorcategory = 'coba'

fields  = [ "Major Category", "Specific Category", "Product ID", "SKU ID", "Product Brand", "Product Desc", "Product URL", "Product Image Link", "Product Ingredients" ]
data_save = []

filename = f'products_{majorcategory}.csv'

def get_section_text(soup, section_title):
    """
    Mengambil teks dari collapsible section berdasarkan judul (summary) seperti 'Ingredients'.
    
    :param soup: Objek BeautifulSoup dari halaman
    :param section_title: Judul section, misalnya 'Ingredients'
    :return: String teks dari section atau None jika tidak ditemukan
    """
    # Cari semua summary di dalam details
    details_tags = soup.find_all("details")
    for details in details_tags:
        summary_tag = details.find("summary")
        if summary_tag and summary_tag.get_text(strip=True) == section_title:
            # Ambil semua teks di div collapsible__content
            content_div = details.find("div", class_="collapsible__content")
            if content_div:
                return content_div.get_text(separator="\n\n", strip=True)
    return None


def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"❌ Error mengambil URL: {e}")
        return None


# def proses_menu_url(soup):
#     full_menu = soup.find("ul", class_="thb-full-menu")
#     if not full_menu:
#         print("Menu utama tidak ditemukan")
#         return []

#     li_items = full_menu.find_all("li", recursive=False)

#     if len(li_items) >= 4:
#         skincare_li = li_items[3]
        
#         menu_title = skincare_li.find("a", class_="thb-full-menu--link")
#         if menu_title:
#             major_category = menu_title.get_text(strip=True)
#             print(f"Category: {major_category}")

#         all_urls = []  # simpan semua URL di sini
        
#         submenus = skincare_li.find_all("ul")
#         for submenu in submenus:
#             for a in submenu.find_all("a"):
#                 url_li_items = f"{BASE_URL}{a.get('href')}"
#                 # print("test:", url_li_items)
#                 all_urls.append(url_li_items)  # simpan URL ke list
                
#         return all_urls
#     else:
#         print("Menu ke-4 tidak ditemukan")
#         return []


# def proses_menu_url(soup):
#     full_menu = soup.find("ul", class_="thb-full-menu")
#     if not full_menu:
#         print("Menu utama tidak ditemukan")
#         return []

#     li_items = full_menu.find_all("li", recursive=False)

#     if len(li_items) >= 4:
#         skincare_li = li_items[3]
        
#         menu_title = skincare_li.find("a", class_="thb-full-menu--link")
#         if menu_title:
#             major_category = menu_title.get_text(strip=True)
#             print(f"Category: {major_category}")

#         all_urls = []  # simpan semua URL di sini
        
#         submenus = skincare_li.find_all("ul")
#         for submenu in submenus:
#             for a in submenu.find_all("a"):
#                 url_li_items = f"{BASE_URL}{a.get('href')}"
#                 if url_li_items not in all_urls:
#                     all_urls.append(url_li_items)  # simpan URL ke list jika belum ada
                
#                 # all_urls.append(url_li_items)  # simpan URL ke list
                
#         return all_urls
#     else:
#         print("Menu ke-4 tidak ditemukan")
#         return []


def proses_menu_url(soup):
    full_menu = soup.find("ul", class_="thb-full-menu")
    if not full_menu:
        print("Menu utama tidak ditemukan")
        return []

    li_items = full_menu.find_all("li", recursive=False)

    if len(li_items) >= 6:
        skincare_li = li_items[5]
        
        menu_title = skincare_li.find("a", class_="thb-full-menu--link")
        if menu_title:
            major_category = menu_title.get_text(strip=True)
            print(f"Category: {major_category}")

        # Daftar URL yang akan di-skip
        skip_urls = {
            "https://www.contentbeautywellbeing.com/collections/natural-makeup-sets",
            "https://www.contentbeautywellbeing.com/collections/gift-vouchers",
            "https://www.contentbeautywellbeing.com/collections/cosmetic-accessories",
            "https://www.contentbeautywellbeing.com/collections/natural-makeup-sets",
            "https://www.contentbeautywellbeing.com/collections/talc-free-cosmetics",
            "https://www.contentbeautywellbeing.com/collections/vegan-natural-makeup",
            
        }

        all_urls = []  
        submenus = skincare_li.find_all("ul")
        for submenu in submenus:
            for a in submenu.find_all("a"):
                url_li_items = f"{BASE_URL}{a.get('href')}"
                if url_li_items not in all_urls and url_li_items not in skip_urls:
                    all_urls.append(url_li_items)  # hanya simpan jika tidak di skip

        return all_urls
    else:
        print("Menu ke-4 tidak ditemukan")
        return []



def get_total_products_and_pages(url, items_per_page=29):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    count_element = soup.select_one("#ProductCount .facets__label")
    if count_element:
        text = count_element.get_text(strip=True)
        total_products = int(''.join(filter(str.isdigit, text)))
    else:
        total_products = 0

    total_pages = math.ceil(total_products / items_per_page) if total_products else 1
    return total_products, total_pages


def fix_url(url):
    # Jika ada domain ganda, perbaiki
    double_domain = "https://www.contentbeautywellbeing.comhttps://"
    if url.startswith(double_domain):
        url = url.replace(double_domain, "https://", 1)
    return url

def url_all_items(url_list):
    url_list = [fix_url(u) for u in url_list]
    total = len(url_list)
    print(f"Total Collections: {total}")

    for i, url_items in enumerate(url_list):  
        print(f"\nMemproses Koleksi Ke-{i+1}: {url_items}")

        # Hitung total produk & halaman untuk koleksi ini
        total_products, total_pages = get_total_products_and_pages(url_items)
        print(f"  Total produk: {total_products}")
        print(f"  Total halaman: {total_pages}")

        for page in range(1, total_pages + 1):
            page_url = f"{url_items}?page={page}"
            print(f"    - Memproses halaman {page}: {page_url}")
            time.sleep(0.5)
            soup_items = get_soup(page_url)

            if not soup_items:
                print(f"    Gagal mengambil data dari {page_url}")
                continue

            find_items = soup_items.find("ul", id="product-grid")
            if find_items:
                product_links = set()
                for a in find_items.find_all("a", class_="product-card-title"):
                    href = a.get("href", "")
                    if "/products/" in href:
                        product_url = f"{BASE_URL}{href}"
                        product_links.add(product_url)

                for product_url in product_links:
                    time.sleep(0.5)
                    product_data = process_product_url(product_url)
                    if product_data:
                        product_data
                        # save_to_csv(product_data)
            else:
                print(f"    Tidak ada item di halaman {page}")


def process_product_url(product_url):
    print(f"\nMemproses produk: {product_url}")
    soup_product = get_soup(product_url)
    time.sleep(0.5)
    if not soup_product:
        print(f"Gagal mengambil data produk dari {product_url}")
        return None

    time.sleep(0.5)
    breadcrumbs = soup_product.select("nav.breadcrumbs a")
    specific_category = breadcrumbs[-1].get_text(strip=True) if len(breadcrumbs) >= 3 else None

    time.sleep(0.5)
    ingredients_text = get_section_text(soup_product, "Ingredients")

    # Ambil script dengan data JSON
    script_tag = soup_product.find("script", id="web-pixels-manager-setup")
    time.sleep(0.5)
    if not script_tag:
        print("❌ Script tidak ditemukan")
        return None

    script_content = script_tag.string
    if not script_content:
        print("❌ Script kosong")
        return None

    # Ambil bagian initData dari script
    match = re.search(r'initData:\s*({.*?}),\s*}', script_content, re.DOTALL)
    if not match:
        print("❌ Tidak ada JSON initData ditemukan")
        return None

    raw_json = match.group(1)

    try:
        data = json.loads(raw_json)
        product_variants = data.get("productVariants", [])

        if not product_variants:
            print("Tidak ada productVariants di JSON")
            return None

        
        for variant in product_variants:
            product = variant.get("product", {})
            price = variant.get("price", {})

            product_id = product.get("id", "")            
            sku_id = variant.get("id", "")
            product_brand = product.get("vendor", "")
            product_desc = product.get("title", "")
            product_url = f"{BASE_URL}{product.get('url')}?variant={variant.get('id')}" if product.get("url") and variant.get("id") else None
            product_image_raw = variant.get("image", {}).get("src", "")
            product_image = f"https:{product_image_raw}" if product_image_raw.startswith("//") else product_image_raw


            save_csv = {
                "Major Category": majorcategory,
                "Specific Category": specific_category,
                "Product ID": f"'{product_id}",
                "SKU ID": f"'{sku_id}",
                "Product Brand": product_brand,
                "Product Desc": product_desc,
                "Product URL": product_url,
                "Product Image Link": product_image,
                "Product Ingredients": ingredients_text
            }

            data_save.append(save_csv)
            print('Saving', save_csv['Product ID'], save_csv['Product Desc'])
            time.sleep(0.5)  # beri jeda agar tidak terlalu cepat
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                for item in data_save:
                    writer.writerow(item)


    except json.JSONDecodeError as e:
        print(f"❌ Gagal parsing JSON: {e}")
        return None



def main():
    soup = get_soup(BASE_URL)
    if not soup:
        return
    
    url_list = proses_menu_url(soup)  # Ambil semua URL
    url_all_items(url_list)  # Tampilkan jumlah dan URL-nya


if __name__ == "__main__":
    main()
