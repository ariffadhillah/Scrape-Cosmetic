# # # # import requests
# # # # import json
# # # # from bs4 import BeautifulSoup

# # # # # --- KONFIGURASI ---
# # # # # url = "https://thrivemarket.com/p/gomacro-oatmeal-chocolate-chip-cookie"
# # # # url = "https://thrivemarket.com/p/thats-it-mango-probiotic-mini-fruit-bars"

# # # # proxies = {
# # # #     'http': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
# # # #     'https': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
# # # # }

# # # # headers = {
# # # #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# # # #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
# # # # }

# # # # try:
# # # #     print(f"Mengakses: {url}...")
# # # #     response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
    
# # # #     if response.status_code == 200:
# # # #         soup = BeautifulSoup(response.text, 'html.parser')

# # # #         # --- 1. EKSTRAKSI DARI productSchema ---
# # # #         script_schema = soup.find('script', id='productSchema')
# # # #         name, sku, image, description, price, brand, size_ = "", "", "", "", "", "", ""
        
# # # #         if script_schema:
# # # #             data_schema = json.loads(script_schema.string)
# # # #             name = data_schema.get("name")
# # # #             size_ = data_schema.get("size")
# # # #             sku = data_schema.get("sku")
# # # #             image = data_schema.get("image", [None])[0]
# # # #             description = data_schema.get("description")
# # # #             price = data_schema.get("offers", {}).get("price")
# # # #             brand = data_schema.get("brand", {}).get("name")

# # # #         # --- 2. EKSTRAKSI DARI __NEXT_DATA__ (Ingredients & Nutrition) ---
# # # #         ingredients_list = []
# # # #         nutrition_map = {}
# # # #         script_next = soup.find('script', id='__NEXT_DATA__')
        
# # # #         if script_next:
# # # #             try:
# # # #                 data_next = json.loads(script_next.string)
# # # #                 product_data = data_next.get("props", {}).get("pageProps", {}).get("product", {})
                
# # # #                 # Ekstraksi Ingredients
# # # #                 ingredients_list = product_data.get("ingredients", [])
                
# # # #                 # Ekstraksi Nutrition Info
# # # #                 nutrition_raw = product_data.get("nutrition_info", [])
# # # #                 # Kita petakan list ke dalam dictionary agar mudah dipanggil
# # # #                 for item in nutrition_raw:
# # # #                     label = item.get("friendly_label")
# # # #                     value = item.get("value")
# # # #                     if label:
# # # #                         nutrition_map[label] = value
                        
# # # #             except Exception as e:
# # # #                 print(f"Gagal memproses data internal NEXT_DATA: {e}")

# # # #         # --- 3. PRINT HASIL ---
# # # #         print("-" * 60)
# # # #         print(f"NAME        : {name}")
# # # #         print(f"Size        : {size_}")
# # # #         print(f"SKU         : {sku}")
# # # #         print(f"PRICE       : {price}")
# # # #         print(f"BRAND       : {brand}")
# # # #         print(f"IMAGE       : {image}")
# # # #         print(f"Description : {description[:100]}...")
        
# # # #         print("\nINGREDIENTS :")
# # # #         if ingredients_list:
# # # #             print(", ".join(ingredients_list))
# # # #         else:
# # # #             print("Ingredients tidak ditemukan.")

# # # #         print("\nNUTRITION INFO :")
# # # #         # Anda bisa memanggil label apapun yang ada di JSON secara spesifik
# # # #         print(f"Calcium            : {nutrition_map.get('Calcium', '-')}")
# # # #         print(f"Calcium            : {nutrition_map.get('Calcium % DV', '-')}")
        
# # # #         print(f"Calories            : {nutrition_map.get('Calories', '-')}")
# # # #         print(f"Total Fat           : {nutrition_map.get('Total Fat % DV', '-')}")
# # # #         print(f"Saturated Fat       : {nutrition_map.get('Saturated Fat % DV', '-')}")
# # # #         print(f"Sodium              : {nutrition_map.get('Sodium % DV', '-')}")
# # # #         print(f"Total Carbohydrate  : {nutrition_map.get('Total Carbohydrate % DV', '-')}")
# # # #         print(f"Dietary Fiber       : {nutrition_map.get('Dietary Fiber % DV', '-')}")
# # # #         print(f"Total Sugars        : {nutrition_map.get('Total Sugars', '-')}")
# # # #         print(f"Protein             : {nutrition_map.get('Protein % DV', '-')}")
# # # #         print(f"Iron                : {nutrition_map.get('Iron % DV', '-')}")
# # # #         print(f"Potassium           : {nutrition_map.get('Potassium % DV', '-')}")
# # # #         print(f"Allergen Warning    : {nutrition_map.get('Warning / Allergen Information', '-')}")
# # # #         print("-" * 60)
            
# # # #     else:
# # # #         print(f"Gagal akses. Status code: {response.status_code}")

# # # # except Exception as e:
# # # #     print(f"Terjadi kesalahan: {e}")



# # # import requests
# # # import json
# # # import csv
# # # import os
# # # from bs4 import BeautifulSoup

# # # # --- KONFIGURASI ---
# # # url = "https://thrivemarket.com/p/thats-it-mango-probiotic-mini-fruit-bars"
# # # filename = "thrive_data_fixed.csv"

# # # proxies = {
# # #     'http': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
# # #     'https': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
# # # }

# # # headers = {
# # #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# # # }

# # # # --- DEFINISI HEADER TETAP (Satu per satu agar rapi) ---
# # # FIELDNAMES = [
# # #     'URL', 'Name', 'Brand', 'SKU', 'Size', 'Price', 'Image URL', 'Description', 'Ingredients',
# # #     'Calories', 
# # #     'Total Fat', 'Total Fat Percent DV', 
# # #     'Saturated Fat', 'Saturated Fat Percent DV',
# # #     'Trans Fat', 
# # #     'Cholesterol', 'Cholesterol Percent DV',
# # #     'Sodium', 'Sodium Percent DV',
# # #     'Total Carbohydrate', 'Total Carbohydrate Percent DV',
# # #     'Dietary Fiber', 'Dietary Fiber Percent DV',
# # #     'Total Sugars', 'Includes Added Sugars', 'Includes Added Sugars Percent DV',
# # #     'Protein', 'Protein Percent DV',
# # #     'Vitamin D', 'Vitamin D Percent DV',
# # #     'Calcium', 'Calcium Percent DV',
# # #     'Iron', 'Iron Percent DV',
# # #     'Potassium', 'Potassium Percent DV',
# # #     'Allergen Warning'
# # # ]

# # # try:
# # #     print(f"Mengakses: {url}...")
# # #     response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
    
# # #     if response.status_code == 200:
# # #         soup = BeautifulSoup(response.text, 'html.parser')
# # #         # Inisialisasi baris dengan string kosong untuk semua kolom di FIELDNAMES
# # #         data_row = {field: "" for field in FIELDNAMES} 
        
# # #         # Masukkan URL asal ke kolom URL
# # #         data_row['URL'] = url

# # #         # --- 1. EKSTRAKSI SCHEMA ---
# # #         script_schema = soup.find('script', id='productSchema')
# # #         if script_schema:
# # #             ds = json.loads(script_schema.string)
# # #             data_row['Name'] = ds.get("name", "")
# # #             data_row['Brand'] = ds.get("brand", {}).get("name", "")
# # #             data_row['SKU'] = ds.get("sku", "")
# # #             data_row['Size'] = ds.get("size", "")
# # #             data_row['Price'] = ds.get("offers", {}).get("price", "")
# # #             # Ambil image pertama dari list jika ada
# # #             img_data = ds.get("image", [])
# # #             data_row['Image URL'] = img_data[0] if isinstance(img_data, list) and img_data else ""
# # #             # Bersihkan description dari newline agar CSV tetap rapi
# # #             desc = ds.get("description", "")
# # #             data_row['Description'] = desc.replace("\n", " ").strip()

# # #         # --- 2. EKSTRAKSI NEXT_DATA ---
# # #         script_next = soup.find('script', id='__NEXT_DATA__')
# # #         if script_next:
# # #             data_next = json.loads(script_next.string)
# # #             product_data = data_next.get("props", {}).get("pageProps", {}).get("product", {})
            
# # #             # Ingredients
# # #             ingredients = product_data.get("ingredients", [])
# # #             data_row['Ingredients'] = ", ".join(ingredients)
            
# # #             # Nutrition Info Mapping
# # #             nutrition_raw = product_data.get("nutrition_info", [])
# # #             temp_map = {item.get("friendly_label"): item.get("value") for item in nutrition_raw}

# # #             # Pemetaan manual satu per satu ke kolom yang sesuai
# # #             data_row['Calories'] = temp_map.get('Calories', "")
# # #             data_row['Total Fat'] = temp_map.get('Total Fat', "")
# # #             data_row['Total Fat Percent DV'] = temp_map.get('Total Fat % DV', "")
# # #             data_row['Saturated Fat'] = temp_map.get('Saturated Fat', "")
# # #             data_row['Saturated Fat Percent DV'] = temp_map.get('Saturated Fat % DV', "")
# # #             data_row['Trans Fat'] = temp_map.get('Trans Fat', "")
# # #             data_row['Cholesterol'] = temp_map.get('Cholesterol', "")
# # #             data_row['Cholesterol Percent DV'] = temp_map.get('Cholesterol % DV', "")
# # #             data_row['Sodium'] = temp_map.get('Sodium', "")
# # #             data_row['Sodium Percent DV'] = temp_map.get('Sodium % DV', "")
# # #             data_row['Total Carbohydrate'] = temp_map.get('Total Carbohydrate', "")
# # #             data_row['Total Carbohydrate Percent DV'] = temp_map.get('Total Carbohydrate % DV', "")
# # #             data_row['Dietary Fiber'] = temp_map.get('Dietary Fiber', "")
# # #             data_row['Dietary Fiber Percent DV'] = temp_map.get('Dietary Fiber % DV', "")
# # #             data_row['Total Sugars'] = temp_map.get('Total Sugars', "")
# # #             data_row['Includes Added Sugars'] = temp_map.get('Includes Added Sugars', "")
# # #             data_row['Includes Added Sugars Percent DV'] = temp_map.get('Includes Added Sugars % DV', "")
# # #             data_row['Protein'] = temp_map.get('Protein', "")
# # #             data_row['Protein Percent DV'] = temp_map.get('Protein % DV', "")
# # #             data_row['Vitamin D'] = temp_map.get('Vitamin D', "")
# # #             data_row['Vitamin D Percent DV'] = temp_map.get('Vitamin D % DV', "")
# # #             data_row['Calcium'] = temp_map.get('Calcium', "")
# # #             data_row['Calcium Percent DV'] = temp_map.get('Calcium % DV', "")
# # #             data_row['Iron'] = temp_map.get('Iron', "")
# # #             data_row['Iron Percent DV'] = temp_map.get('Iron % DV', "")
# # #             data_row['Potassium'] = temp_map.get('Potassium', "")
# # #             data_row['Potassium Percent DV'] = temp_map.get('Potassium % DV', "")
# # #             data_row['Allergen Warning'] = temp_map.get('Warning / Allergen Information', "")

# # #         # --- 3. SIMPAN KE CSV ---
# # #         file_exists = os.path.isfile(filename)
# # #         with open(filename, mode='a', newline='', encoding='utf-8') as f:
# # #             writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
# # #             if not file_exists:
# # #                 writer.writeheader()
# # #             writer.writerow(data_row)

# # #         print("-" * 60)
# # #         print(f"BERHASIL: {data_row['Name']}")
# # #         print(f"URL: {url}")
# # #         print("-" * 60)
            
# # #     else:
# # #         print(f"Gagal akses. Status code: {response.status_code}")

# # # except Exception as e:
# # #     print(f"Terjadi kesalahan: {e}")



# # import requests
# # import json
# # import csv
# # import os
# # import time
# # from bs4 import BeautifulSoup

# # # --- KONFIGURASI FILE ---
# # input_filename = "all_urls_thrive.csv"    # File sumber URL
# # output_filename = "thrive_data_fixed.csv" # File hasil scraping

# # proxies = {
# #     'http': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
# #     'https': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
# # }

# # headers = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# # }

# # # --- DEFINISI HEADER TETAP ---
# # FIELDNAMES = [
# #     "Category","Sub Category",'SKU',  'Name', 'Brand',  'Size', 'Price', 'URL', 'Image URL', 'Description', 'Ingredients',
# #     'Calories', 'Total Fat', 'Total Fat Percent DV', 'Saturated Fat', 'Saturated Fat Percent DV',
# #     'Trans Fat', 'Cholesterol', 'Cholesterol Percent DV', 'Sodium', 'Sodium Percent DV',
# #     'Total Carbohydrate', 'Total Carbohydrate Percent DV', 'Dietary Fiber', 'Dietary Fiber Percent DV',
# #     'Total Sugars', 'Includes Added Sugars', 'Includes Added Sugars Percent DV',
# #     'Protein', 'Protein Percent DV', 'Vitamin D', 'Vitamin D Percent DV',
# #     'Calcium', 'Calcium Percent DV', 'Iron', 'Iron Percent DV',
# #     'Potassium', 'Potassium Percent DV', 'Allergen Warning'
# # ]

# # def scrape_product(url):
# #     """Fungsi untuk mengambil data dari satu URL"""
# #     try:
# #         response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
# #         if response.status_code != 200:
# #             print(f" Gagal: {url} (Status: {response.status_code})")
# #             return None

# #         soup = BeautifulSoup(response.text, 'html.parser')
# #         data_row = {field: "" for field in FIELDNAMES} 
# #         data_row['URL'] = url

# #         # 1. Ekstraksi Schema
# #         script_schema = soup.find('script', id='productSchema')
# #         if script_schema:
# #             ds = json.loads(script_schema.string)
# #             data_row['Name'] = ds.get("name", "")
# #             data_row['Brand'] = ds.get("brand", {}).get("name", "")
# #             data_row['SKU'] = ds.get("sku", "")
# #             data_row['Size'] = ds.get("size", "")
# #             data_row['Price'] = ds.get("offers", {}).get("price", "")
# #             img_data = ds.get("image", [])
# #             data_row['Image URL'] = img_data[0] if isinstance(img_data, list) and img_data else ""
# #             data_row['Description'] = ds.get("description", "").replace("\n", " ").strip()

# #         # 2. Ekstraksi Next_Data
# #         script_next = soup.find('script', id='__NEXT_DATA__')
# #         if script_next:
# #             data_next = json.loads(script_next.string)
# #             product_data = data_next.get("props", {}).get("pageProps", {}).get("product", {})
            
# #             # Ingredients
# #             ingredients = product_data.get("ingredients", [])
# #             data_row['Ingredients'] = ", ".join(ingredients)
            
# #             # Nutrition Mapping
# #             nutrition_raw = product_data.get("nutrition_info", [])
# #             temp_map = {item.get("friendly_label"): item.get("value") for item in nutrition_raw}

# #             data_row['Calories'] = temp_map.get('Calories', "")
# #             data_row['Total Fat'] = temp_map.get('Total Fat', "")
# #             data_row['Total Fat Percent DV'] = temp_map.get('Total Fat % DV', "")
# #             data_row['Saturated Fat'] = temp_map.get('Saturated Fat', "")
# #             data_row['Saturated Fat Percent DV'] = temp_map.get('Saturated Fat % DV', "")
# #             data_row['Trans Fat'] = temp_map.get('Trans Fat', "")
# #             data_row['Cholesterol'] = temp_map.get('Cholesterol', "")
# #             data_row['Cholesterol Percent DV'] = temp_map.get('Cholesterol % DV', "")
# #             data_row['Sodium'] = temp_map.get('Sodium', "")
# #             data_row['Sodium Percent DV'] = temp_map.get('Sodium % DV', "")
# #             data_row['Total Carbohydrate'] = temp_map.get('Total Carbohydrate', "")
# #             data_row['Total Carbohydrate Percent DV'] = temp_map.get('Total Carbohydrate % DV', "")
# #             data_row['Dietary Fiber'] = temp_map.get('Dietary Fiber', "")
# #             data_row['Dietary Fiber Percent DV'] = temp_map.get('Dietary Fiber % DV', "")
# #             data_row['Total Sugars'] = temp_map.get('Total Sugars', "")
# #             data_row['Includes Added Sugars'] = temp_map.get('Includes Added Sugars', "")
# #             data_row['Includes Added Sugars Percent DV'] = temp_map.get('Includes Added Sugars % DV', "")
# #             data_row['Protein'] = temp_map.get('Protein', "")
# #             data_row['Protein Percent DV'] = temp_map.get('Protein % DV', "")
# #             data_row['Vitamin D'] = temp_map.get('Vitamin D', "")
# #             data_row['Vitamin D Percent DV'] = temp_map.get('Vitamin D % DV', "")
# #             data_row['Calcium'] = temp_map.get('Calcium', "")
# #             data_row['Calcium Percent DV'] = temp_map.get('Calcium % DV', "")
# #             data_row['Iron'] = temp_map.get('Iron', "")
# #             data_row['Iron Percent DV'] = temp_map.get('Iron % DV', "")
# #             data_row['Potassium'] = temp_map.get('Potassium', "")
# #             data_row['Potassium Percent DV'] = temp_map.get('Potassium % DV', "")
# #             data_row['Allergen Warning'] = temp_map.get('Warning / Allergen Information', "")

# #         return data_row
# #     except Exception as e:
# #         print(f" Error pada URL {url}: {e}")
# #         return None

# # # --- PROSES UTAMA (LOOPING) ---
# # if __name__ == "__main__":
# #     if not os.path.exists(input_filename):
# #         print(f"File {input_filename} tidak ditemukan!")
# #     else:
# #         with open(input_filename, mode='r', encoding='utf-8') as f_in:
# #             reader = csv.DictReader(f_in)
            
# #             # Persiapkan file output (tulis header jika belum ada)
# #             file_exists = os.path.isfile(output_filename)
            
# #             with open(output_filename, mode='a', newline='', encoding='utf-8') as f_out:
# #                 writer = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
# #                 if not file_exists:
# #                     writer.writeheader()
                
# #                 # Mulai looping URL
# #                 for i, row in enumerate(reader, 1):
# #                     target_url = row.get('url')
# #                     if not target_url:
# #                         continue
                    
# #                     print(f"[{i}] Memproses: {target_url}")
# #                     result = scrape_product(target_url)
                    
# #                     if result:
# #                         writer.writerow(result)
# #                         print(f"    Berhasil: {result['Name']}")
                    
# #                     # Beri jeda 1-2 detik agar tidak diblokir server (opsional)
# #                     time.sleep(1)

# #         print("\n" + "="*30)
# #         print("SEMUA PROSES SELESAI!")
# #         print(f"Data disimpan di: {output_filename}")
# #         print("="*30)



# import requests
# import json
# import csv
# import os
# import time
# from bs4 import BeautifulSoup

# category_name = 'Pantry'
# Sub_category_name = 'Salad dressing'

# # --- KONFIGURASI FILE ---
# input_filename = "url_list.csv"
# output_filename = "thrive_data_fixed.csv"

# proxies = {
#     'http': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
#     'https': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
# }

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# }

# # --- DEFINISI HEADER TETAP ---
# FIELDNAMES = [
#    "Category","Sub Category", 'SKU', 'Name', 'Size', 'Brand',   
#     'URL', 'Image URL', 'Description', 'Ingredients',
#     'Calories', 'Total Fat', 'Total Fat Percent DV', 'Saturated Fat', 'Saturated Fat Percent DV',
#     'Trans Fat', 'Cholesterol', 'Cholesterol Percent DV', 'Sodium', 'Sodium Percent DV',
#     'Total Carbohydrate', 'Total Carbohydrate Percent DV', 'Dietary Fiber', 'Dietary Fiber Percent DV',
#     'Total Sugars', 'Includes Added Sugars', 'Includes Added Sugars Percent DV',
#     'Protein', 'Protein Percent DV', 'Vitamin D', 'Vitamin D Percent DV',
#     'Calcium', 'Calcium Percent DV', 'Iron', 'Iron Percent DV',
#     'Potassium', 'Potassium Percent DV', 'Allergen Warning','Price', 'Rating', 'Review Count'
# ]

# def scrape_product(url):
#     try:
#         response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
#         if response.status_code != 200:
#             print(f" Gagal: {url} (Status: {response.status_code})")
#             return None

#         soup = BeautifulSoup(response.text, 'html.parser')
#         data_row = {field: "" for field in FIELDNAMES} 
#         data_row['URL'] = url

#         script_schema = soup.find('script', id='productSchema')
#         if script_schema:
#             ds = json.loads(script_schema.string)
#             data_row['Name'] = ds.get("name", "")
#             data_row['Brand'] = ds.get("brand", {}).get("name", "")
#             data_row['SKU'] = ds.get("sku", "")
#             data_row['Size'] = ds.get("size", "")
#             data_row['Price'] = ds.get("offers", {}).get("price", "")
            
#             # --- EKSTRAKSI RATING (FORMAT 4.1) ---
#             agg_rating = ds.get("aggregateRating", {})
#             rating_val = agg_rating.get("ratingValue")
#             if rating_val:
#                 try:
#                     data_row['Rating'] = f"{float(rating_val):.1f}"
#                 except:
#                     data_row['Rating'] = rating_val # Jika gagal convert, pakai aslinya
            
#             data_row['Review Count'] = agg_rating.get("ratingCount", "")
            
#             img_data = ds.get("image", [])
#             data_row['Image URL'] = img_data[0] if isinstance(img_data, list) and img_data else ""
#             data_row['Description'] = ds.get("description", "").replace("\n", " ").strip()


#         # 2. Ekstraksi Next_Data (Nutrition & Ingredients)
#         script_next = soup.find('script', id='__NEXT_DATA__')
#         if script_next:
#             data_next = json.loads(script_next.string)
#             product_data = data_next.get("props", {}).get("pageProps", {}).get("product", {})
            
#             ingredients = product_data.get("ingredients", [])
#             data_row['Ingredients'] = ", ".join(ingredients)
            
#             nutrition_raw = product_data.get("nutrition_info", [])
#             temp_map = {item.get("friendly_label"): item.get("value") for item in nutrition_raw}

#             # Mapping nutrisi (Tetap Manual & Konsisten)
#             data_row['Calories'] = temp_map.get('Calories', "")
#             data_row['Total Fat'] = temp_map.get('Total Fat', "")
#             data_row['Total Fat Percent DV'] = temp_map.get('Total Fat % DV', "")
#             data_row['Saturated Fat'] = temp_map.get('Saturated Fat', "")
#             data_row['Saturated Fat Percent DV'] = temp_map.get('Saturated Fat % DV', "")
#             data_row['Trans Fat'] = temp_map.get('Trans Fat', "")
#             data_row['Cholesterol'] = temp_map.get('Cholesterol', "")
#             data_row['Cholesterol Percent DV'] = temp_map.get('Cholesterol % DV', "")
#             data_row['Sodium'] = temp_map.get('Sodium', "")
#             data_row['Sodium Percent DV'] = temp_map.get('Sodium % DV', "")
#             data_row['Total Carbohydrate'] = temp_map.get('Total Carbohydrate', "")
#             data_row['Total Carbohydrate Percent DV'] = temp_map.get('Total Carbohydrate % DV', "")
#             data_row['Dietary Fiber'] = temp_map.get('Dietary Fiber', "")
#             data_row['Dietary Fiber Percent DV'] = temp_map.get('Dietary Fiber % DV', "")
#             data_row['Total Sugars'] = temp_map.get('Total Sugars', "")
#             data_row['Includes Added Sugars'] = temp_map.get('Includes Added Sugars', "")
#             data_row['Includes Added Sugars Percent DV'] = temp_map.get('Includes Added Sugars % DV', "")
#             data_row['Protein'] = temp_map.get('Protein', "")
#             data_row['Protein Percent DV'] = temp_map.get('Protein % DV', "")
#             data_row['Vitamin D'] = temp_map.get('Vitamin D', "")
#             data_row['Vitamin D Percent DV'] = temp_map.get('Vitamin D % DV', "")
#             data_row['Calcium'] = temp_map.get('Calcium', "")
#             data_row['Calcium Percent DV'] = temp_map.get('Calcium % DV', "")
#             data_row['Iron'] = temp_map.get('Iron', "")
#             data_row['Iron Percent DV'] = temp_map.get('Iron % DV', "")
#             data_row['Potassium'] = temp_map.get('Potassium', "")
#             data_row['Potassium Percent DV'] = temp_map.get('Potassium % DV', "")
#             data_row['Allergen Warning'] = temp_map.get('Warning / Allergen Information', "")


#         return data_row
#     except Exception as e:
#         print(f" Error pada URL {url}: {e}")
#         return None


# if __name__ == "__main__":
#     if not os.path.exists(input_filename):
#         print(f"File {input_filename} tidak ditemukan!")
#     else:
#         with open(input_filename, mode='r', encoding='utf-8') as f_in:
#             reader = csv.DictReader(f_in)
#             file_exists = os.path.isfile(output_filename)
            
#             with open(output_filename, mode='a', newline='', encoding='utf-8') as f_out:
#                 writer = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
#                 if not file_exists:
#                     writer.writeheader()
                
#                 for i, row in enumerate(reader, 1):
#                     target_url = row.get('url')
#                     if not target_url: continue
                    
#                     print(f"[{i}] Memproses: {target_url}")
#                     result = scrape_product(target_url)
#                     if result:
#                         writer.writerow(result)
#                         print(f"    Berhasil: {result['Name']} (Rating: {result['Rating']})")
                    
#                     time.sleep(1)

#         print(f"\nSelesai! Data disimpan di: {output_filename}")



import requests
import json
import csv
import os
import time
from bs4 import BeautifulSoup

# --- KONFIGURASI KATEGORI ---
CATEGORY_NAME = 'Meat & Seafood'
SUB_CATEGORY_NAME = 'Beef'

# --- KONFIGURASI FILE ---
input_filename = "url_beef.csv"
output_filename = f"{CATEGORY_NAME}-{SUB_CATEGORY_NAME}.csv"

proxies = {
    'http': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
    'https': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# --- DEFINISI HEADER TETAP ---
FIELDNAMES = [
   "Category","Sub Category", 'SKU', 'Name', 'Size', 'Brand',   
    'URL', 'Image URL', 'Description', 'Ingredients',
    'Calories', 'Total Fat', 'Total Fat Percent DV', 'Saturated Fat', 'Saturated Fat Percent DV',
    'Trans Fat', 'Cholesterol', 'Cholesterol Percent DV', 'Sodium', 'Sodium Percent DV',
    'Total Carbohydrate', 'Total Carbohydrate Percent DV', 'Dietary Fiber', 'Dietary Fiber Percent DV',
    'Total Sugars', 'Includes Added Sugars', 'Includes Added Sugars Percent DV',
    'Protein', 'Protein Percent DV', 'Vitamin D', 'Vitamin D Percent DV',
    'Calcium', 'Calcium Percent DV', 'Iron', 'Iron Percent DV',
    'Potassium', 'Potassium Percent DV', 'Allergen Warning','Price', 'Rating', 'Review Count'
]

def scrape_product(url):
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f" Gagal: {url} (Status: {response.status_code})")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        data_row = {field: "" for field in FIELDNAMES} 
        
        # --- MENGISI DATA KATEGORI ---
        data_row['URL'] = url
        data_row['Category'] = CATEGORY_NAME
        data_row['Sub Category'] = SUB_CATEGORY_NAME

        # 1. Ekstraksi Schema
        script_schema = soup.find('script', id='productSchema')
        if script_schema:
            ds = json.loads(script_schema.string)
            data_row['Name'] = ds.get("name", "")
            data_row['Brand'] = ds.get("brand", {}).get("name", "")
            data_row['SKU'] = ds.get("sku", "")
            data_row['Size'] = ds.get("size", "")
            data_row['Price'] = ds.get("offers", {}).get("price", "")
            
            # Rating
            agg_rating = ds.get("aggregateRating", {})
            rating_val = agg_rating.get("ratingValue")
            if rating_val:
                try:
                    data_row['Rating'] = f"{float(rating_val):.1f}"
                except:
                    data_row['Rating'] = rating_val 
            
            data_row['Review Count'] = agg_rating.get("ratingCount", "")
            
            img_data = ds.get("image", [])
            data_row['Image URL'] = img_data[0] if isinstance(img_data, list) and img_data else ""
            # Bersihkan description
            data_row['Description'] = " ".join(ds.get("description", "").split())


        # 2. Ekstraksi Next_Data
        script_next = soup.find('script', id='__NEXT_DATA__')
        if script_next:
            data_next = json.loads(script_next.string)
            product_data = data_next.get("props", {}).get("pageProps", {}).get("product", {})
            
            ingredients = product_data.get("ingredients", [])
            data_row['Ingredients'] = ", ".join(ingredients)
            
            nutrition_raw = product_data.get("nutrition_info", [])
            temp_map = {item.get("friendly_label"): item.get("value") for item in nutrition_raw}

            # Mapping nutrisi
            data_row['Calories'] = temp_map.get('Calories', "")
            data_row['Total Fat'] = temp_map.get('Total Fat', "")
            data_row['Total Fat Percent DV'] = temp_map.get('Total Fat % DV', "")
            data_row['Saturated Fat'] = temp_map.get('Saturated Fat', "")
            data_row['Saturated Fat Percent DV'] = temp_map.get('Saturated Fat % DV', "")
            data_row['Trans Fat'] = temp_map.get('Trans Fat', "")
            data_row['Cholesterol'] = temp_map.get('Cholesterol', "")
            data_row['Cholesterol Percent DV'] = temp_map.get('Cholesterol % DV', "")
            data_row['Sodium'] = temp_map.get('Sodium', "")
            data_row['Sodium Percent DV'] = temp_map.get('Sodium % DV', "")
            data_row['Total Carbohydrate'] = temp_map.get('Total Carbohydrate', "")
            data_row['Total Carbohydrate Percent DV'] = temp_map.get('Total Carbohydrate % DV', "")
            data_row['Dietary Fiber'] = temp_map.get('Dietary Fiber', "")
            data_row['Dietary Fiber Percent DV'] = temp_map.get('Dietary Fiber % DV', "")
            data_row['Total Sugars'] = temp_map.get('Total Sugars', "")
            data_row['Includes Added Sugars'] = temp_map.get('Includes Added Sugars', "")
            data_row['Includes Added Sugars Percent DV'] = temp_map.get('Includes Added Sugars % DV', "")
            data_row['Protein'] = temp_map.get('Protein', "")
            data_row['Protein Percent DV'] = temp_map.get('Protein % DV', "")
            data_row['Vitamin D'] = temp_map.get('Vitamin D', "")
            data_row['Vitamin D Percent DV'] = temp_map.get('Vitamin D % DV', "")
            data_row['Calcium'] = temp_map.get('Calcium', "")
            data_row['Calcium Percent DV'] = temp_map.get('Calcium % DV', "")
            data_row['Iron'] = temp_map.get('Iron', "")
            data_row['Iron Percent DV'] = temp_map.get('Iron % DV', "")
            data_row['Potassium'] = temp_map.get('Potassium', "")
            data_row['Potassium Percent DV'] = temp_map.get('Potassium % DV', "")
            data_row['Allergen Warning'] = temp_map.get('Warning / Allergen Information', "")

        return data_row
    except Exception as e:
        print(f" Error pada URL {url}: {e}")
        return None

if __name__ == "__main__":
    if not os.path.exists(input_filename):
        print(f"File {input_filename} tidak ditemukan!")
    else:
        with open(input_filename, mode='r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            file_exists = os.path.isfile(output_filename)
            
            with open(output_filename, mode='a', newline='', encoding='utf-8') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
                if not file_exists:
                    writer.writeheader()
                
                for i, row in enumerate(reader, 1):
                    target_url = row.get('url')
                    if not target_url: continue
                    
                    print(f"[{i}] Memproses: {target_url}")
                    result = scrape_product(target_url)
                    if result:
                        writer.writerow(result)
                        print(f"    Berhasil: {result['Name']}")
                    
                    time.sleep(1)

        print(f"\nSelesai! Data disimpan di: {output_filename}")