import requests
import re
import json
import time
import csv
import math
from bs4 import BeautifulSoup




BASE_URL = "https://www.spacenk.com/uk/makeup"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Connection": "keep-alive"
}

majorcategory = 'makeup'

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
    full_menu = soup.find("ul", class_="swiper-wrapper list-unstyled mb-1")
    if not full_menu:
        print("Menu utama tidak ditemukan")
        return []

    li_items = full_menu.find_all("li", recursive=False)

    if len(li_items) >= 7:
        for skincare_li in li_items[1:]:
            menu_title = skincare_li.find("a", class_="btn btn-tertiary")
            if menu_title:
                url_li_items = f"https://www.spacenk.com{menu_title['href']}"
                major_category = menu_title.get_text(strip=True)
                print(f"Category: {major_category}")
                print(f"URL: {url_li_items}")

                # Sekarang kita proses isi halaman major_category
                proses_items(url_li_items)


def proses_items(url):
    """Ambil isi dari halaman kategori"""
    print(f"Processing page: {url}")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            find_items = soup.find("div", class_="row product-grid")
            for product in find_items.find_all("div", class_="product-tile"):
                if product.find("a"):
                    product_url = f"https://www.spacenk.com{product.find('a')['href']}"
                    # print(f"Product URL: {product_url}")
                    process_product_url(product_url)

        else:
            print(f"Gagal membuka {url}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error membuka {url}: {e}")


def process_product_url(product_url):
    print(f"\nMemproses produk: {product_url}")
    time.sleep(0.5)
    soup_product = get_soup(product_url)
    # print(soup_product)
    # time.sleep(0.5)

    time.sleep(0.5)
    breadcrumb = soup_product.find("nav", class_="col breadcrumbs")
    specific_category = ""
    if breadcrumb:
        # Ambil semua item breadcrumb
        items = breadcrumb.find_all("li", class_="breadcrumb-item")
        if items:
            # Ambil teks dari item terakhir
            last_item = items[-1].find("a")
            specific_category = last_item.get_text(strip=True) if last_item else ""    


    time.sleep(0.5)
    ranting_rivew = soup_product.find("div", class_="ratings_holder")
    if ranting_rivew:
        # Ambil rating (contoh: 4.8)
        start = ranting_rivew.find("div", class_="pr-2 font-weight-bold")
        start = start.get_text(strip=True) if start else ""

        # Ambil jumlah review (contoh: (1,749))
        review = ranting_rivew.find("div", class_="reviewCountText")
        if review:
            review = review.get_text(strip=True)
            review = review.strip("()")  # hapus kurung dan koma
        else:
            review = ""


    time.sleep(0.5)
    find_product_detail_attributes = soup_product.find("div", class_="product-detail__attributes")
    if find_product_detail_attributes:
        attributes = find_product_detail_attributes.find("div", class_="d-flex flex-wrap")
        if attributes:
            for attr in attributes.find_all("div", class_="position-relative"):
                choice = attr.find("input", class_="position-absolute")
                if choice:
                    href_json = choice.get("value", "")
                    # print("tampilkan url dari",href_json)
                    if href_json:
                        json_url = f"{href_json}"
                        json_response = requests.get(json_url, headers=headers, timeout=10)
                        try:
                            data = json_response.json()
                            # print(json.dumps(data, indent=2))
                            product = data.get("product", [])
                            product_desc = product.get("productName", "")  
                            quantity_ = product.get("measurement", {}).get("quantity","")  
                            unit_ = product.get("measurement", {}).get("unit","")  
                            product_brand = product.get("brand", "").capitalize()  
                            product_id = product.get("masterID", "")  
                            sku_id = product.get("id", "")
                            imd_medium = product.get("images", {}).get("medium", {})
                            image_url = (imd_medium[0] if isinstance(imd_medium, list) and imd_medium else imd_medium).get("url", "")

                            ingredients = product.get("ingredients", "").capitalize()  
  
                            # image_url = product.get("images", {}).get("medium","").get("url","")  

                            product_url_items = data.get("queryString","")
                            
                            # print("Specific Category:", specific_category)
                            # print(f"Product ID {product_id}")
                            # print(f"SKU ID : {sku_id}")
                            # print(f"Product Brand : {product_brand}")
                            # print(f"Product Desc : {product_desc} {quantity_} {unit_}")
                            # print(f"Product URL : {'https://www.spacenk.com/uk/makeup/complexion/primer/skin-nova-MUK200036203.html?'}{product_url_items}")
                            # print(f"Product Image Link : {image_url}")
                            # print(f"Product Ingredients : {ingredients}")
                            # print("Rating:", start)
                            # print("Jumlah review:", review)
                            # print()

                            save_csv = {
                                "Major Category": majorcategory,
                                "Specific Category": specific_category,
                                "Product ID": f"'{product_id}",
                                "SKU ID": f"'{sku_id}",
                                "Product Brand": product_brand,
                                "Product Desc": f"{product_desc} {quantity_} {unit_}".replace("0 None","").replace("None",""),
                                "Product URL": f"{product_url}?{product_url_items}",
                                "Product Image Link": image_url,
                                "Product Ingredients": ingredients,
                                "Rating": f"'{start}",	
                                "User Reviews" : f"'{review}"
                            }

                            data_save.append(save_csv)
                            print('Saving', save_csv['Product ID'], save_csv['Product Desc'])
                            print('Saving', save_csv['Product URL'])
                            print()
                            time.sleep(1)
                            # with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                            #     writer = csv.DictWriter(csvfile, fieldnames=fields)
                            #     writer.writeheader()
                            #     for item in data_save:
                            #         writer.writerow(item)



                            # print(f"ini nilai dari measurement : {measurement}")

                            # break
                        except Exception as e:
                            print(f"Failed to parse JSON from {json_url}: {e}")



def main():
    soup = get_soup(BASE_URL)
    if not soup:
        return
    url_list = proses_menu_url(soup) 

if __name__ == "__main__":
    main()
