#     # walmart_json_processor.py

# import requests
# import json
# from bs4 import BeautifulSoup
# import time
# import os

# def ekstrak_json_next_data(url):
#     """
#     Mengambil konten HTML dari URL, mencari tag <script id="__NEXT_DATA__">,
#     dan mengembalikan konten JSON di dalamnya.
#     """
#     try:
#         # Header yang diperkuat
#         headers = {
#             # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
#         }
        
#         # Menggunakan timeout 20 detik untuk meningkatkan peluang sukses
#         response = requests.get(url, headers=headers, timeout=20)
#         response.raise_for_status() 
        
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Mencari tag <script> berdasarkan ID
#         script_tag = soup.find('script', id='__NEXT_DATA__')
        
#         if script_tag and script_tag.string:
#             json_text = script_tag.string
#             data_dict = json.loads(json_text)
#             return data_dict
#         else:
#             return None

#     except Exception as e:
#         # Menampilkan URL yang gagal untuk debug
#         print(f"❌ Kesalahan JSON/Request pada URL {url}: {e}")
#         return None

# def proses_dan_simpan_json(url, output_dir="json_output"):
#     """Mengambil JSON, mengekstrak data kunci, dan menyimpannya."""
    
#     # 1. Ambil data JSON
#     data = ekstrak_json_next_data(url)
    
#     if data:
#         print(f"✅ JSON berhasil diekstrak untuk: {url}")
        
#         # 2. Ekstrak data kunci untuk verifikasi
#         try:
#             product_name = data['props']['pageProps']['initialData']['data']['contentLayout']['pageMetadata']['pageContext']['itemContext']['name']
#             product_brand = data['props']['pageProps']['initialData']['data']['contentLayout']['pageMetadata']['pageContext']['itemContext']['brand']
#             averageRating = data['props']['pageProps']['initialData']['data']['reviews']['averageOverallRating']
#             product_ingredients = data['props']['pageProps']['initialData']['data']['idml']['ingredients']
#             price = data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice']['price']
#             totalReviewCount = data['props']['pageProps']['initialData']['data']['reviews']['totalReviewCount']
#             print(f"   -> Nama Produk: {product_name}")
#             print(f"   -> Produk Brand: {product_brand}")
#             print(f"   -> Harga: ${price}")
#             print(f"   -> Ingredients: {product_ingredients}")
#             print(f"   -> averageRating: {averageRating}")
#             print(f"   -> totalReviewCount: {totalReviewCount}")
#         except KeyError as e:
#             print(f"   ⚠️ Gagal mengekstrak kunci data utama: {e}")
#             product_name = "unknown_product"

#         # 3. Simpan seluruh JSON ke file
#         # Gunakan Item ID sebagai nama file agar unik
#         try:
#             item_id = data['query']['itemid']
#             file_name = f"{item_id}_{product_name[:20].replace(' ', '_')}.json"
#         except:
#             file_name = f"data_{int(time.time())}.json"
            
#         # os.makedirs(output_dir, exist_ok=True)
#         # file_path = os.path.join(output_dir, file_name)
        
#         # with open(file_path, 'w', encoding='utf-8') as f:
#         #     json.dump(data, f, ensure_ascii=False, indent=4)
            
#         # print(f"   💾 Data lengkap disimpan ke: {file_path}")
#         return True
#     else:
#         print(f"❌ Gagal mengambil JSON untuk: {url}")
#         return False


# walmart_json_processor.py

import requests
import json
from bs4 import BeautifulSoup
import time
import os
import csv

walmart_data = []

major_Category = "Fragrances"
category_name = 'Perfume for Women.csv'

filename = f"{major_Category}-{category_name}.csv"
fields = ["Product ID", "SKU ID","Product Name","Product Maker","Varian/color","Product Url","Major Category","Category","Ingredients", "Active Ingredients", "Inactive Ingredients", "Active Ingredient Name", "Product Image URL", "Price","Total Review Count","Rating"]

def normalisasi_ingredients(idml_data):
    """
    Selalu kembalikan 4 field ingredients walaupun sebagian None
    """
    ingredients = {
        "ingredients": {
            "name": "Ingredients",
            "value": ""
        },
        "activeIngredients": {
            "name": "Active Ingredients",
            "value": ""
        },
        "inactiveIngredients": {
            "name": "Inactive Ingredients",
            "value": ""
        },
        "activeIngredientName": {
            "name": "Active Ingredient Name",
            "value": ""
        }
    }

    if not idml_data or not isinstance(idml_data, dict):
        return ingredients

    raw = idml_data.get("ingredients")
    if not raw or not isinstance(raw, dict):
        return ingredients

    # mapping aman
    if raw.get("ingredients"):
        ingredients["ingredients"]["value"] = raw["ingredients"].get("value")

    if raw.get("activeIngredients"):
        val = raw["activeIngredients"].get("value")
        # ingredients["activeIngredients"]["value"] = None if val in ["None", "", None] else val
        ingredients["activeIngredients"]["value"] = raw["activeIngredients"].get("value")

    if raw.get("inactiveIngredients"):
        ingredients["inactiveIngredients"]["value"] = raw["inactiveIngredients"].get("value")

    if raw.get("activeIngredientName"):
        ingredients["activeIngredientName"]["value"] = raw["activeIngredientName"].get("value")

    return ingredients


def ekstrak_json_dan_soup(url):
    time.sleep(2)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        data_dict = json.loads(script_tag.string) if script_tag else None
        return data_dict, soup
    except Exception as e:
        print(f"❌ Kesalahan pada URL {url}: {e}")
        return None, None

def cari_url_gambar_robust(soup, data):
    time.sleep(2)
    """Mencari URL gambar dari berbagai kemungkinan lokasi di HTML dan JSON."""
    
    # --- STRATEGI 1: Cari di JSON (Paling Akurat & Resolusi Tinggi) ---
    try:
        # Mencoba mengambil gambar pertama dari list allImages
        all_imgs = data['props']['pageProps']['initialData']['data']['product']['imageInfo']['allImages']
        if all_imgs and len(all_imgs) > 0:
            return all_imgs[0]['url']
    except: pass

    try:
        # Jalur alternatif di JSON
        return data['props']['pageProps']['initialData']['data']['product']['imageInfo']['mainImageUrl']
    except: pass

    # --- STRATEGI 2: Cari di HTML (BeautifulSoup) ---
    # Cari berdasarkan data-testid atau data-seo-id yang Anda temukan
    img_tag = soup.find('img', {'data-testid': 'hero-image'}) or \
              soup.find('img', {'data-seo-id': 'hero-image'})
    
    if img_tag:
        # Coba ambil src, jika tidak ada (karena lazy load), ambil srcset atau data-src
        img_url = img_tag.get('src') or img_tag.get('srcset') or img_tag.get('data-src')
        if img_url:
            # Jika srcset berisi banyak URL, ambil yang pertama (biasanya yang dipisahkan koma)
            return img_url.split(',')[0].split(' ')[0]

    # --- STRATEGI 3: Pencarian Brutal (Cari tag <img> yang mengandung kata kunci Walmart Images) ---
    for img in soup.find_all('img', src=True):
        if 'walmartimages.com/seo' in img['src'] or 'walmartimages.com/ip' in img['src']:
            return img['src']

    return "Image Not Found"

def proses_dan_simpan_json(product_url, output_dir="json_output"):
    data, soup = ekstrak_json_dan_soup(product_url)
    
    if data and soup:
        # print(f"✅ Data berhasil diekstrak untuk: {url}")
        


        try:
            # Ekstraksi Data Standar
            product_name = data['props']['pageProps']['initialData']['data']['contentLayout']['pageMetadata']['pageContext']['itemContext']['name']
            productId = data['props']['pageProps']['initialData']['data']['contentLayout']['pageMetadata']['pageContext']['itemContext']['productId']
            skuId = data['props']['pageProps']['initialData']['data']['contentLayout']['pageMetadata']['pageContext']['itemContext']['itemId']
            product_brand = data['props']['pageProps']['initialData']['data']['contentLayout']['pageMetadata']['pageContext']['itemContext']['brand']
            price = data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice']['price']
            totalReviewCount = data['props']['pageProps']['initialData']['data']['reviews']['totalReviewCount']
            # averageRating = data['props']['pageProps']['initialData']['data']['reviews']['averageOverallRating']
            raw_rating = data['props']['pageProps']['initialData']['data']['reviews'].get('averageOverallRating')
            averageRating = round(float(raw_rating), 1) if raw_rating is not None else ""

            
            # product_ingredients = data['props']['pageProps']['initialData']['data']['idml']['ingredients']

            idml_data = data['props']['pageProps']['initialData']['data'].get('idml')
            product_ingredients = normalisasi_ingredients(idml_data)


            
            # PANGGIL FUNGSI PENCARIAN GAMBAR ROBUST
            imageUrl = cari_url_gambar_robust(soup, data)

            # 3. EKSTRAKSI VARIAN / COLOR (Permintaan Baru Anda)
            item_varian = ""

            # Cari div variant-group-0
            variant_group = soup.find('div', {'data-testid': 'variant-group-0'})
            if variant_group:
                # Cari span dengan class ml1 yang berisi nama warna/varian
                color_span = variant_group.find('span', class_='ml1')
                if color_span:
                    item_varian = color_span.get_text(strip=True).title()

            ingredients = product_ingredients["ingredients"]["value"]
            active_ingredients = product_ingredients["activeIngredients"]["value"]
            inactive_ingredients = product_ingredients["inactiveIngredients"]["value"]
            active_Ingredient_Name = product_ingredients["activeIngredientName"]["value"]
            


            data_walmart = {
                "Product ID": productId,
                "SKU ID": skuId,
                "Product Name": product_name,
                "Product Maker": product_brand,
                "Product Url":  product_url,
                "Major Category": major_Category,
                "Category": category_name,
                "Ingredients" : ingredients,
                # "Active Ingredients ": active_ingredients,
                "Active Ingredients": active_ingredients,
                "Inactive Ingredients" : inactive_ingredients,
                "Active Ingredient Name": active_Ingredient_Name,
                "Product Image URL": imageUrl,
                "Price": price,
                "Varian/color": item_varian,
                "Total Review Count": totalReviewCount,
                "Rating": f"'{averageRating}",
            }
            walmart_data.append(data_walmart)
            print('Saving', data_walmart['Product Url'])

            # with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            #     writer = csv.DictWriter(csvfile, fieldnames=fields)
            #     writer.writeheader()
            #     for item in data:
            #         writer.writerow(item)
            
            file_exists = os.path.isfile(filename)
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data_walmart)


        except Exception as e:
            print(f"   ⚠️ Terjadi kesalahan saat memproses data: {e}")
            


        return True
    else:
        print(f"❌ Gagal mengambil data untuk: {product_url}")
        return False
