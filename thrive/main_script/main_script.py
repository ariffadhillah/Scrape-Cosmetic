import requests
import json
import csv
import os
import time
import glob
from bs4 import BeautifulSoup

# --- KONFIGURASI PROXY & HEADERS ---
proxies = {
    'http': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
    'https': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# --- KONFIGURASI OUTPUT TUNGGAL ---
MASTER_OUTPUT = "save_Thrivemarket.csv"
DEFAULT_TEXT = "N/A"
DEFAULT_PRICE = "0.00"

# --- DEFINISI HEADER CSV ---
FIELDNAMES = [
   "Category","Sub Category", 'SKU', 'Name', 'Size', 'Brand',   
    'URL','Serving Size', 'Calories', 'Total Fat', 'Total Fat Percent DV', 'Saturated Fat', 'Saturated Fat Percent DV',
    'Trans Fat', 'Cholesterol', 'Cholesterol Percent DV', 'Sodium', 'Sodium Percent DV',
    'Total Carbohydrate', 'Total Carbohydrate Percent DV', 'Dietary Fiber', 'Dietary Fiber Percent DV',
    'Total Sugars', 'Includes Added Sugars', 'Includes Added Sugars Percent DV',
    'Protein', 'Protein Percent DV', 'Vitamin D', 'Vitamin D Percent DV',
    'Calcium', 'Calcium Percent DV', 'Iron', 'Iron Percent DV',
    'Potassium', 'Potassium Percent DV', 'Ingredients', 'Description', 'Allergen Warning','Image URL','Price', 'Rating', 'Review Count'
]

def scrape_product(url, category, sub_category):
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        data_row = {field: DEFAULT_TEXT for field in FIELDNAMES} 
        
        data_row['URL'] = url
        data_row['Category'] = category
        data_row['Sub Category'] = sub_category

        # 1. Ekstraksi Schema
        script_schema = soup.find('script', id='productSchema')
        if script_schema:
            ds = json.loads(script_schema.string)
            data_row['Name']  = ds.get("name") or DEFAULT_TEXT
            data_row['Brand'] = ds.get("brand", {}).get("name") or DEFAULT_TEXT
            data_row['SKU']   = ds.get("sku") or DEFAULT_TEXT
            data_row['Size']  = ds.get("size") or DEFAULT_TEXT
            
            price_val = ds.get("offers", {}).get("price")
            data_row['Price'] = str(price_val) if price_val else DEFAULT_PRICE
            
            agg_rating = ds.get("aggregateRating", {})
            rating_val = agg_rating.get("ratingValue")
            if rating_val:
                try: data_row['Rating'] = f"{float(rating_val):.1f}"
                except: data_row['Rating'] = DEFAULT_TEXT
            else:
                data_row['Rating'] = "0.0"
            
            data_row['Review Count'] = agg_rating.get("ratingCount") or "0"
            img_data = ds.get("image", [])
            data_row['Image URL'] = img_data[0] if isinstance(img_data, list) and img_data else DEFAULT_TEXT
            data_row['Description'] = " ".join(ds.get("description", "").split()) or DEFAULT_TEXT

        # 2. Ekstraksi Next_Data
        script_next = soup.find('script', id='__NEXT_DATA__')
        if script_next:
            data_next = json.loads(script_next.string)
            product_data = data_next.get("props", {}).get("pageProps", {}).get("product", {})
            ing_list = product_data.get("ingredients", [])
            data_row['Ingredients'] = ", ".join(ing_list) if ing_list else DEFAULT_TEXT
            
            nut_raw = product_data.get("nutrition_info", [])
            temp_map = {item.get("friendly_label"): item.get("value") for item in nut_raw}

            # fields_map = {
            #     'Serving size': 'Serving size', 'Calories': 'Calories', 'Total Fat': 'Total Fat', 'Total Fat Percent DV': 'Total Fat % DV',
            #     'Saturated Fat': 'Saturated Fat', 'Saturated Fat Percent DV': 'Saturated Fat % DV',
            #     'Trans Fat': 'Trans Fat', 'Cholesterol': 'Cholesterol', 'Cholesterol Percent DV': 'Cholesterol % DV',
            #     'Sodium': 'Sodium', 'Sodium Percent DV': 'Sodium % DV',
            #     'Total Carbohydrate': 'Total Carbohydrate', 'Total Carbohydrate Percent DV': 'Total Carbohydrate % DV',
            #     'Dietary Fiber': 'Dietary Fiber', 'Dietary Fiber Percent DV': 'Dietary Fiber % DV',
            #     'Total Sugars': 'Total Sugars', 'Includes Added Sugars': 'Includes Added Sugars',
            #     'Includes Added Sugars Percent DV': 'Includes Added Sugars % DV', 'Protein': 'Protein',
            #     'Protein Percent DV': 'Protein % DV', 'Vitamin D': 'Vitamin D', 'Vitamin D Percent DV': 'Vitamin D % DV',
            #     'Calcium': 'Calcium', 'Calcium Percent DV': 'Calcium % DV', 'Iron': 'Iron',
            #     'Iron Percent DV': 'Iron % DV', 'Potassium': 'Potassium', 'Potassium Percent DV': 'Potassium % DV',
            #     'Allergen Warning': 'Warning / Allergen Information'
            # }

            fields_map = {
                'Serving Size': 'Serving Size', # <--- Ini yang Abang tambahkan
                'Calories': 'Calories', 
                'Total Fat': 'Total Fat', 
                'Total Fat Percent DV': 'Total Fat % DV',
                'Saturated Fat': 'Saturated Fat', 
                'Saturated Fat Percent DV': 'Saturated Fat % DV',
                'Trans Fat': 'Trans Fat', 
                'Cholesterol': 'Cholesterol', 
                'Cholesterol Percent DV': 'Cholesterol % DV',
                'Sodium': 'Sodium', 
                'Sodium Percent DV': 'Sodium % DV',
                'Total Carbohydrate': 'Total Carbohydrate', 
                'Total Carbohydrate Percent DV': 'Total Carbohydrate % DV',
                'Dietary Fiber': 'Dietary Fiber', 
                'Dietary Fiber Percent DV': 'Dietary Fiber % DV',
                'Total Sugars': 'Total Sugars', 
                'Includes Added Sugars': 'Includes Added Sugars',
                'Includes Added Sugars Percent DV': 'Includes Added Sugars % DV', 
                'Protein': 'Protein',
                'Protein Percent DV': 'Protein % DV', 
                'Vitamin D': 'Vitamin D', 
                'Vitamin D Percent DV': 'Vitamin D % DV',
                'Calcium': 'Calcium', 
                'Calcium Percent DV': 'Calcium % DV', 
                'Iron': 'Iron',
                'Iron Percent DV': 'Iron % DV', 
                'Potassium': 'Potassium', 
                'Potassium Percent DV': 'Potassium % DV',
                'Allergen Warning': 'Warning / Allergen Information'
            }
            for csv_key, json_key in fields_map.items():
                data_row[csv_key] = temp_map.get(json_key) or DEFAULT_TEXT

        return data_row
    except Exception as e:
        print(f"      [!] Error pada URL {url}: {e}")
        return None

if __name__ == "__main__":
    csv_files = glob.glob("*/*.csv")

    if not csv_files:
        print("Folder kategori atau file CSV tidak ditemukan!")
    else:
        # Cek apakah file Master sudah ada atau belum
        file_exists = os.path.isfile(MASTER_OUTPUT)
        
        # Buka file Master satu kali saja di awal
        with open(MASTER_OUTPUT, mode='a', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
            
            # Tulis header jika filenya benar-benar baru
            if not file_exists:
                writer.writeheader()
            
            for file_path in csv_files:
                # Ambil Nama Folder sebagai Category dan Nama File sebagai Sub-Category
                folder_name = os.path.dirname(file_path)
                sub_cat_name = os.path.splitext(os.path.basename(file_path))[0]

                print(f"\n>>> PROCESSING: {folder_name} > {sub_cat_name}")

                with open(file_path, mode='r', encoding='utf-8') as f_in:
                    reader = csv.DictReader(f_in)
                    
                    for i, row in enumerate(reader, 1):
                        url = row.get('url')
                        if not url: continue
                        
                        result = scrape_product(url, folder_name, sub_cat_name)
                        if result:
                            writer.writerow(result)
                            # Flush data agar langsung tersimpan di file (mencegah data hilang jika mati lampu/error)
                            f_out.flush()
                            print(f"   [{i}] Berhasil: {result['Name'][:30]}...")
                        
                        time.sleep(1)

    print(f"\nSelesai! Semua data masuk ke: {MASTER_OUTPUT}")