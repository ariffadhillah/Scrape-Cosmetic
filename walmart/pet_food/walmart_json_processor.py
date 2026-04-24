
import requests
import json
from bs4 import BeautifulSoup
import time
import os
import csv
import re

walmart_data = []

# major_Category = "pet food"
category_name = 'Pet Food'

filename = f"result-{category_name}.csv"
fields = ["Category","UPC","Product ID", "SKU ID","Product Name","Product Maker","Varian/color","Product Url","Ingredients" , "Active Ingredients", "Inactive Ingredients", "Active Ingredient Name","Product Details", "Varian/color", "Animal lifestage", "Weight", "Pet food flavor", "Meat type","Pet food condition", "Product line", "Brand", "Animal health concern", "Size","Pet food form","Shelf life","Product Image URL","Price","Total Review Count","Rating"
          ]

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
            upc = data['props']['pageProps']['initialData']['data']['product']['upc']
            totalReviewCount = data['props']['pageProps']['initialData']['data']['reviews']['totalReviewCount']
            # averageRating = data['props']['pageProps']['initialData']['data']['reviews']['averageOverallRating']
            raw_rating = data['props']['pageProps']['initialData']['data']['reviews'].get('averageOverallRating')
            averageRating = round(float(raw_rating), 1) if raw_rating is not None else ""

            

            idml_data = data['props']['pageProps']['initialData']['data'].get('idml')
            product_ingredients = normalisasi_ingredients(idml_data)

            # longDescription = data['props']['pageProps']['initialData']['data']['idml']['longDescription']
            # product_details = data['props']['pageProps']['initialData']['data']['idml']['shortDescription']
            # print(f"Product details: {product_details}...")  # Print sebagian untuk verifikasi
            # print(f"Long Description: {longDescription[:100]}...")  # Print sebagian untuk verifikasi
            # print()
            # print()


            shortDescription = data['props']['pageProps']['initialData']['data']['idml'].get('shortDescription', '')
            longDescription  = data['props']['pageProps']['initialData']['data']['idml'].get('longDescription', '')

            def text(x):
                return BeautifulSoup(x or "", "html.parser").get_text("\n", strip=True)

            Product_details = "Product details\n\n" + "\n\n".join(
                t for t in [text(shortDescription), text(longDescription)] if t
            )

            


            specs = data['props']['pageProps']['initialData']['data']['idml']["specifications"]

            spec_dict = {
                item["name"].lower().replace(" ", "_"): item["value"]
                for item in specs
            }
            
            # print(Product_details)


            
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
                "UPC": upc,
                "SKU ID": skuId,
                "Product Name": product_name,
                "Product Maker": product_brand,
                "Product Url":  product_url,
                # "Major Category": major_Category,
                "Category": category_name,
                "Ingredients" : ingredients,
                "Active Ingredients": active_ingredients,
                "Inactive Ingredients" : inactive_ingredients,
                "Active Ingredient Name": active_Ingredient_Name,
                "Product Details": Product_details,
                "Varian/color": item_varian,
                "Animal lifestage": spec_dict.get("animal_lifestage"),
                "Weight": spec_dict.get("weight"),
                "Pet food flavor": spec_dict.get("pet_food_flavor"),
                "Meat type": spec_dict.get("meat_type"),
                "Pet food condition": spec_dict.get("pet_food_condition"),
                "Product line": spec_dict.get("product_line"),
                "Brand": spec_dict.get("brand"),
                "Animal health concern": spec_dict.get("animal_health_concern"),
                "Size": spec_dict.get("size"),
                "Pet food form": spec_dict.get("pet_food_form"),
                "Shelf life": spec_dict.get("shelf_life"),                
                "Product Image URL": imageUrl,
                "Price": price,
                "Total Review Count": totalReviewCount,
                "Rating": f"'{averageRating}",
            }
            walmart_data.append(data_walmart)
            print('Saving', data_walmart['Product Url'])
            print('Saving', data_walmart['UPC'])

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
