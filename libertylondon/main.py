import requests
import re
import json
import time
import csv
import math
from bs4 import BeautifulSoup




BASE_URL = "https://www.libertylondon.com/uk/department/beauty/skin-care/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Connection": "keep-alive"
}


majorcategory = 'Skincare'

fields  = [ "Major Category", "Specific Category", "Product ID", "SKU ID", "Product Brand", "Product Desc", "Product URL", "Product Image Link", "Product Ingredients", "Rating", "User Reviews" ]
data_save = []

filename = f'products_{majorcategory}.csv'


def get_soup(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"❌ Error mengambil URL: {e}")
        return None


def proses_menu_url(soup):
    full_menu = soup.find("ul", class_="swiper-wrapper")
    if not full_menu:
        print("Menu utama tidak ditemukan")
        return []

    li_items = full_menu.find_all("li", recursive=False)
    for list_menu in li_items:
        a_tag = list_menu.find("a")
        if a_tag and a_tag.get("href"):
            url_menu = url_menu = "https://www.libertylondon.com" + a_tag["href"]
            proses_items(url_menu)
        # break



# def proses_items(url):
#     """Ambil isi dari halaman kategori"""
#     print(f"Processing page: {url}")
#     try:
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.text, "html.parser")
#             total_number_of_results = soup.find('span', class_="total-number-of-results").text.strip().replace(" Results",'')
#             print(total_number_of_results)
#             find_items = soup.find("div", class_="row product-grid")
#             for product in find_items.find_all("div", class_="product-tile"):
#                 if product.find("a"):
#                     product_url = f"https://www.libertylondon.com{product.find('a')['href']}"
#                     # print(f"Product URL: {product_url}")
#                     process_product_url(product_url)

#         else:
#             print(f"Gagal membuka {url}, status code: {response.status_code}")
#     except Exception as e:
#         print(f"Error membuka {url}: {e}")

def proses_items(url):
    """Ambil isi dari halaman kategori"""
    print(f"Processing page: {url}")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # ambil total number of results
            total_number_of_results = soup.find('span', class_="total-number-of-results").text.strip().replace(" Results",'')
            total_number_of_results = int(total_number_of_results)
            print("Total items:", total_number_of_results)

            # bikin url baru dengan parameter ?sz=total_number_of_results
            # ambil cgid dari url asli
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(url)
            qs = parse_qs(parsed.query)

            cgid = qs.get("cgid", [""])[0]  # ambil cgid dari query string
            if not cgid:
                # fallback: extract dari path (misalnya "beauty_make-up_face")
                path_parts = parsed.path.strip("/").split("/")
                if len(path_parts) >= 4:
                    cgid = f"{path_parts[2]}_{path_parts[3]}_{path_parts[4]}"

            new_url = (
                f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                f"?cgid={cgid}&prefn1=canShipTo&prefv1=GB&start=0&sz={total_number_of_results}&srule=undefined"
            )
            print("New URL:", new_url)

            # request ulang ke new_url
            response_all = requests.get(new_url, headers={"User-Agent": "Mozilla/5.0"})
            if response_all.status_code == 200:
                soup_all = BeautifulSoup(response_all.text, "html.parser")
                find_items = soup_all.find("div", class_="row product-grid")
                for product in find_items.find_all("div", class_="product-tile"):
                    if product.find("a"):
                        product_url = f"https://www.libertylondon.com{product.find('a')['href']}"
                        print("Memproses produk Item:", product_url)
                        process_product_url(product_url)

        else:
            print(f"Gagal membuka {url}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error membuka {url}: {e}")



def fetch_json(json_url):
    """Ambil data JSON dari url"""
    try:
        json_response = requests.get(json_url, headers=headers, timeout=10)
        json_response.raise_for_status()
        data = json_response.json()
        # print(f"✅ Berhasil ambil JSON: {json_url}")
        return data
    except Exception as e:
        print(f"❌ Gagal ambil JSON dari {json_url}: {e}")
        return None


def process_product_url(product_url_item):
    print(f"\nMemproses produk Item: {product_url_item}")

    # ambil ID hanya kalau sesuai pola angka sebelum .html
    match = re.search(r"-(\d+)\.html$", product_url_item)
    if not match:
        return  # skip produk tanpa ID numeric

    id_product_url_item = match.group(1)
    # print("ID Product:", id_product_url_item)

    time.sleep(0.5)
    soup_product = get_soup(product_url_item)
    if not soup_product:
        return

    time.sleep(0.5)
    breadcrumb = soup_product.find("div", class_="pdp-breadcrumbs")
    specific_category = ""
    if breadcrumb:
        # Ambil semua item breadcrumb
        items = breadcrumb.find_all("li", class_="breadcrumb-item")
        if items:
            # Ambil teks dari item terakhir
            last_item = items[-1].find("a")
            specific_category = last_item.get_text(strip=True) if last_item else ""    



    # cari div yang teksnya "Ingredients"
    ingredients_div = soup_product.find("div", class_="accordion-text", string=lambda t: t and "Ingredients" in t)

    ingredients_text = ""
    if ingredients_div:
        # ambil sibling berikutnya yang berisi konten
        content_div = ingredients_div.find_parent("div", class_="accordion").find_next_sibling("div")
        if content_div:
            p_tag = content_div.find("p")
            if p_tag:
                ingredients_text = p_tag.get_text(" ", strip=True)    


    # kasih default
    start = ""
    review = ""

    try:
        time.sleep(0.5)
        ranting_rivew = soup_product.find("div", class_="ratings")
        if ranting_rivew:
            # Ambil rating (contoh: 4.8)
            start_tag = ranting_rivew.find("div", {"class": "bv_text", "itemprop": "ratingValue"})
            start = start_tag.get_text(strip=True) if start_tag else ""

            # Ambil jumlah review (contoh: (1,749))
            review_tag = ranting_rivew.find("div", class_="bv_numReviews_component_container")
            if review_tag:
                review = review_tag.get_text(strip=True)
                review = review.strip("()")  # hapus kurung
    except Exception as e:
        print("⚠️ Error parsing rating/review:", e)

    # ingredients_text = get_section_text(soup_product, "Ingredients")

    json_urls = []

    # cari custom select
    find_product_detail_attributes = soup_product.find("div", class_="liberty-custom-select-wrapper")
    if find_product_detail_attributes:
        attributes = find_product_detail_attributes.find("div", class_="liberty-custom-select")
        if attributes:
            for attr in attributes.find_all("div", class_="liberty-custom-options-color d-flex"):
                buttons = attr.find_all("button")
                for choice in buttons:
                    href_json = choice.get("data-url", "")
                    if href_json and href_json not in json_urls:  # hindari duplikat
                        json_urls.append(href_json)

    # fallback kalau tidak ada JSON sama sekali
    if not json_urls:
        fallback_url = (
            f"https://www.libertylondon.com/on/demandware.store/"
            f"Sites-liberty-Site/default/Product-Variation?"
            f"dwvar_{id_product_url_item}_color=&"
            f"dwvar_{id_product_url_item}_size=ONE&"
            f"pid={id_product_url_item}&quantity=1"
        )
        json_urls.append(fallback_url)

    # proses semua json_urls
    for json_url in json_urls:
        data = fetch_json(json_url)
        if data:
            # print(f"🔗 JSON dari {json_url}")
            # # contoh: hanya tampilkan sebagian supaya tidak terlalu panjang
            # print(json.dumps(data, indent=2)[:500], "...\n")

            product = data.get("product", [])
            product_desc = product.get("productName", "")  
            # product_id = id_product_url_item
            sku_id = product.get("EAN", "") 
            product_brand = product.get("brand", "").capitalize() 
            imd_medium = product.get("images", {}).get("large", {})
            image_url = (imd_medium[0] if isinstance(imd_medium, list) and imd_medium else imd_medium).get("url", "")
            queryString_ = data.get("queryString","")
            one_product_url = f"{product_url_item}?{queryString_}"
            # quantity_ = product.get("measurement", {}).get("quantity","")  

            # print("Product Id", id_product_url_item)
            # print("Product Id", id_product_url_item)
            # print("SKU Id", sku_id)
            # print("Product Desc", product_desc)
            # print("Product Brand", product_brand)
            # print("Product URL", one_product_url)
            # print("Image Url", image_url)
            # print("Ingredients:", ingredients_text)
            # print("Start", start)
            # print("review", review)
            # print()


            save_csv = {
                "Major Category": majorcategory,
                "Specific Category": specific_category,
                "Product ID": f"'{id_product_url_item}",
                "SKU ID": f"'{sku_id}",
                "Product Brand": product_brand,
                "Product Desc": product_desc,
                "Product URL": one_product_url,
                "Product Image Link": image_url,
                "Product Ingredients": ingredients_text,
                "Rating": f"'{start}",	
                "User Reviews" : f"'{review}"
            }
            
            data_save.append(save_csv)
            print('Saving', save_csv['Product ID'], save_csv['Product Desc'])
            # print('Saving', save_csv['Product URL'])
            # print()
            time.sleep(1)
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                for item in data_save:
                    writer.writerow(item)



def main():
    soup = get_soup(BASE_URL)
    if not soup:
        return
    proses_menu_url(soup) 

if __name__ == "__main__":
    main()

