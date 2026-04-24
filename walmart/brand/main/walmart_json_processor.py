
import requests
import json
from bs4 import BeautifulSoup
import time
import os
import csv
import re

walmart_data = []
# major_Category = "pet food"
category_name = 'Alcohol'
Sub_category_name = 'Single serve'

filename = f"result-{category_name}-{Sub_category_name}.csv"
fields = ["Category","Sub Category","UPC","Product ID", "SKU ID","Product Name","Product Maker","Varian/color","Product Url","Ingredients" , "Active Ingredients", "Inactive Ingredients", "Active Ingredient Name","Product Details", "Varian/color","Cuisine", "Flavor", "cheese_type", "Food condition", "Texture", 
    "Shelf life", "Packaged meal type", "Brand", "Flavor notes", 
    "Product line", "Net content statement", "Nutrition facts label image", 
    "Ingredient list image", "Weight", "Food preparation method", 
    "Cheese type", "Food form", "Size", "Spice level", "Pack quantity", 
    "Average sold by weight", "Container type", "Milk type", "Wine pairing", 
    "Percent of milk fat in dairy", "Count per pack", "Assembled product weight", 
    "Nut butter & spread type", "Multipack quantity", "Vegetable type", 
    "Instructions", "Product net content parent", "Cooking sauce & marinade type", 
    "Mixed spice & seasoning type", "Single herb & spice type", 
    "Tortilla & wrap type", "Grain type", "Color", "Plant Variety", 
    "Count Per Pack", "Count", "Piece Count", "Shelf Life", "Product Net Content UOM","Product Image URL","Price","Total Review Count","Rating", "Total protein per serving","Canned & jarred beans & legumes type", "Food & drug fact label type", "Pasta sauce type","Canned & jarred seafood type", "Retail packaging", "Material","Fruit type","Food preparation tips","Rice type","Dry beans & legumes type","Size descriptor","Dispenser style","Serv per cont","Pepper & peppercorn type","Bread & bun type", "Vinegar type", "Cooking spray type","Lamb cut","Lean to fat ratio","Protein source","Egg type","Plant-based milk type","Milk fat description","Snack chip type","Dough type","Theme","Dairy cream type","Occasion","Poultry cut","Cooking oil type","Caffeine designation","Bottled drinking water type", "Drink mix type", "Seafood type",  "Condiment type", "Origin of cheese","Nut type","Butter & margarine type","Salad dressing type","Piece count", "Yogurt type","Roast type","Individually wrapped","Baking mix type","Chocolate type","Beer style"      

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
            # try:

            # except:
            #     None
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
                "UPC": f"'{upc}",  # Tambahkan tanda kutip untuk menjaga format angka panjang di Excel
                "SKU ID": skuId,
                "Product Name": product_name,
                "Product Maker": product_brand,
                "Product Url":  product_url,
                # "Major Category": major_Category,
                "Category": category_name,
                "Sub Category": Sub_category_name,
                "Ingredients" : ingredients,
                "Active Ingredients": active_ingredients,
                "Inactive Ingredients" : inactive_ingredients,
                "Active Ingredient Name": active_Ingredient_Name,
                "Product Details": Product_details,
                "Varian/color": item_varian,


                "Cuisine": spec_dict.get("cuisine"),
                "Flavor": spec_dict.get("flavor"),
                "cheese_type": spec_dict.get("cheese_type"),
                "Food condition": spec_dict.get("food_condition"),
                "Texture": spec_dict.get("texture"),
                "Shelf life": spec_dict.get("shelf_life"),
                "Packaged meal type": spec_dict.get("packaged_meal_type"),
                "Brand": spec_dict.get("brand"),
                "Flavor notes": spec_dict.get("flavor_notes"),
                "Product line": spec_dict.get("product_line"),
                "Net content statement": spec_dict.get("net_content_statement"),
                "Nutrition facts label image": spec_dict.get("nutrition_facts_label_image"),      
                "Ingredient list image": spec_dict.get("ingredient_list_image"),      
                "Weight": spec_dict.get("weight"),      
                "Food preparation method": spec_dict.get("food_preparation_method"),
                "Food form": spec_dict.get("food_form"),      
                "Size": spec_dict.get("size"),      
                "Spice level": spec_dict.get("spice_level"),      
                "Pack quantity": spec_dict.get("pack_quantity"),      
                "Average sold by weight": spec_dict.get("average_sold_by_weight"),      
                "Container type": spec_dict.get("container_type"),      
                "Milk type": spec_dict.get("milk_type"),      
                "Wine pairing": spec_dict.get("wine_pairing"),      
                "Percent of milk fat in dairy": spec_dict.get("percent_of_milk_fat_in_dairy"),      
                "Count per pack": spec_dict.get("count_per_pack"),      
                "Assembled product weight": spec_dict.get("assembled_product_weight"),      
                "Nut butter & spread type": spec_dict.get("nut_butter_&_spread_type"),      
                "Multipack quantity": spec_dict.get("multipack_quantity"),      
                "Vegetable type": spec_dict.get("vegetable_type"),      
                "Instructions": spec_dict.get("instructions"),      
                "Product net content parent": spec_dict.get("product_net_content_parent"),      
                "Cooking sauce & marinade type": spec_dict.get("cooking_sauce_&_marinade_type"),      
                "Mixed spice & seasoning type": spec_dict.get("mixed_spice_&_seasoning_type"),      
                "Single herb & spice type": spec_dict.get("single_herb_&_spice_type"),      
                "Tortilla & wrap type": spec_dict.get("tortilla_&_wrap_type"),      
                "Grain type": spec_dict.get("grain_type"),      
                "Color": spec_dict.get("color"),      
                "Plant Variety": spec_dict.get("plant_variety"),      
                "Count Per Pack": spec_dict.get("count_per_pack"),      
                "Count": spec_dict.get("count"),      
                "Piece Count": spec_dict.get("piece_count"),      
                "Shelf Life": spec_dict.get("shelf_life"),      
                "Product Net Content UOM": spec_dict.get("product_net_content_uom"),      
                "Total protein per serving": spec_dict.get("total_protein_per_serving"),      
                "Occasion": spec_dict.get("occasion"),      
                "Canned & jarred beans & legumes type": spec_dict.get("canned_&_jarred_beans_&_legumes_type"),      
                "Food & drug fact label type": spec_dict.get("food_&_drug_fact_label_type"),      
                "Pasta sauce type": spec_dict.get("pasta_sauce_type"),      
                "Canned & jarred seafood type": spec_dict.get("canned_&_jarred_seafood_type"),      
                "Retail packaging": spec_dict.get("retail_packaging"),      
                "Material": spec_dict.get("material"),      
                "Fruit type": spec_dict.get("fruit_type"),      
                "Poultry cut": spec_dict.get("poultry_cut"),      
                "Food preparation tips": spec_dict.get("food_preparation_tips"),      
                "Rice type": spec_dict.get("rice_type"),      
                "Dry beans & legumes type": spec_dict.get("dry_beans_&_legumes_type"),      
                "Size descriptor": spec_dict.get("size_descriptor"),      
                "Dispenser style": spec_dict.get("dispenser_style"),      
                "Cooking oil type": spec_dict.get("cooking_oil_type"),      
                "Serv per cont": spec_dict.get("serv_per_cont"),      
                "Pepper & peppercorn type": spec_dict.get("pepper_&_peppercorn_type"),      
                "Bread & bun type": spec_dict.get("bread_&_bun_type"),      
                "Vinegar type": spec_dict.get("vinegar_type"),      
                "Cooking spray type": spec_dict.get("cooking_spray_type"),      
                "Lamb cut": spec_dict.get("lamb_cut"),      
                "Lean to fat ratio": spec_dict.get("lean_to_fat_ratio"),      
                "Protein source": spec_dict.get("protein_source"),      
                "Egg type": spec_dict.get("egg_type"),      
                "Plant-based milk type": spec_dict.get("plant-based_milk_type"),      
                "Milk fat description": spec_dict.get("milk_fat_description"),      
                "Snack chip type": spec_dict.get("snack_chip_type"),      
                "Dough type": spec_dict.get("dough_type"),      
                "Theme": spec_dict.get("theme"),      
                "Dairy cream type": spec_dict.get("dairy_cream_type"),      
                "Caffeine designation": spec_dict.get("caffeine_designation"),      
                "Bottled drinking water type": spec_dict.get("bottled_drinking_water_type"),      
                "Drink mix type": spec_dict.get("drink_mix_type"),      
                "Seafood type": spec_dict.get("seafood_type"),      
                "Condiment type": spec_dict.get("condiment_type"),      
                "Origin of cheese": spec_dict.get("origin_of_cheese"),
                "Nut type": spec_dict.get("nut_type"),
                "Butter & margarine type": spec_dict.get("butter_&_margarine_type"),
                "Salad dressing type": spec_dict.get("salad_dressing_type"),
                "Piece count": spec_dict.get("piece_count"),
                "Yogurt type": spec_dict.get("yogurt_type"),
                "Roast type": spec_dict.get("roast_type"),
                "Individually wrapped": spec_dict.get("individually_wrapped"),
                "Baking mix type": spec_dict.get("baking_mix_type"),
                "Chocolate type": spec_dict.get("chocolate_type"),
                "Beer style": spec_dict.get("beer_style"),
                

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
