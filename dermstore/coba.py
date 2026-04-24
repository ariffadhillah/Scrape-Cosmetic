# # # # # import requests
# # # # # import json
# # # # # import re
# # # # # from bs4 import BeautifulSoup
# # # # # import sys 

# # # # # sys.setrecursionlimit(3000)

# # # # # # --- Fungsi Helper: Mencari Ingredients di HTML yang Dimuat ---
# # # # # def extract_ingredients_from_html(soup):
# # # # #     """Mencari blok HTML ingredients berdasarkan atribut unik."""
# # # # #     # Kita cari div yang memiliki id terkait deskripsi/ingredients
# # # # #     # Berdasarkan contoh Anda: id="product-description-3" dan aria-labelledby="Ingredients"
    
# # # # #     # Mencoba mencari elemen berdasarkan aria-labelledby
# # # # #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    
# # # # #     if target_div:
# # # # #         # Kita ambil teks dari seluruh konten di dalamnya, lalu membersihkannya
# # # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # # #         return clean_text
    
# # # # #     return None


# # # # # # --- Fungsi find_ingredient_data dipertahankan untuk membersihkan HTML JSON ---
# # # # # def find_ingredient_data(data):
# # # # #     """Fungsi rekursif untuk mencari blok data 'ingredients' yang spesifik (dari JSON)
# # # # #        dan mengembalikan konten HTML-nya."""
# # # # #     if isinstance(data, dict):
# # # # #         if data.get("key") == 'ingredients':
# # # # #             try:
# # # # #                 content_list = data['value']['richContentValue']['content']
# # # # #                 for item in content_list:
# # # # #                     if item['type'] == 'HTML':
# # # # #                         return item['content']
# # # # #             except (KeyError, TypeError):
# # # # #                 pass
        
# # # # #         for k, v in data.items():
# # # # #             result = find_ingredient_data(v)
# # # # #             if result: return result
            
# # # # #     elif isinstance(data, list):
# # # # #         for item in data:
# # # # #             result = find_ingredient_data(item)
# # # # #             if result: return result
            
# # # # #     return None

# # # # # def scrape_dermstore_data(url):
# # # # #     """Mengambil data variasi produk dan ingredients dari URL Dermstore."""
# # # # #     headers = {
# # # # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# # # # #         "Accept-Language": "en-US,en;q=0.9",
# # # # #         "Referer": "https://www.google.com/"
# # # # #     }

# # # # #     print(f"Sedang mengambil data dari: {url} ...")
    
# # # # #     try:
# # # # #         response = requests.get(url, headers=headers, timeout=15)
        
# # # # #         if response.status_code != 200:
# # # # #             print(f"Gagal membuka halaman. Status code: {response.status_code}")
# # # # #             return

# # # # #         soup = BeautifulSoup(response.text, 'html.parser')
# # # # #         scripts = soup.find_all('script')
        
# # # # #         # Inisialisasi variabel data
# # # # #         variation_data = None
# # # # #         ingredients_content = None # Sekarang menyimpan teks ingredients bersih
        
# # # # #         # 1. Cari Data Variasi (Prioritas Tinggi)
# # # # #         for script in scripts:
# # # # #             if script.string and "const variationData =" in script.string:
# # # # #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# # # # #                 if match:
# # # # #                     try:
# # # # #                         variation_data = json.loads(match.group(1))
# # # # #                         break
# # # # #                     except json.JSONDecodeError:
# # # # #                         pass
        
# # # # #         # 2. Ekstraksi Ingredients dari Data Variasi (Jika Ditemukan)
# # # # #         if variation_data:
# # # # #             first_variation = variation_data[0]
# # # # #             content_list = first_variation.get('content', [])

# # # # #             for content_item in content_list:
# # # # #                 if content_item.get('key') == 'ingredients':
# # # # #                     try:
# # # # #                         content_html_list = content_item['value']['richContentValue']['content']
# # # # #                         for html_block in content_html_list:
# # # # #                             if html_block['type'] == 'HTML':
# # # # #                                 # Bersihkan HTML menjadi teks di sini
# # # # #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# # # # #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
# # # # #                                 break
# # # # #                         break 
# # # # #                     except (KeyError, TypeError):
# # # # #                         pass

# # # # #         # 3. Fallback: Ekstraksi Ingredients dari HTML Langsung (Jika JSON gagal)
# # # # #         if not ingredients_content:
# # # # #             ingredients_content = extract_ingredients_from_html(soup)
# # # # #             if ingredients_content:
# # # # #                 print("[INFO] Ingredients diekstrak langsung dari elemen HTML.")
# # # # #             # Jika HTML juga gagal, kita coba pencarian skrip agresif
# # # # #             elif not variation_data:
# # # # #                 print("[INFO] Mencoba fallback pencarian skrip agresif...")
# # # # #                 for script in scripts:
# # # # #                     if script.string and '"key": "ingredients"' in script.string:
# # # # #                         try:
# # # # #                             # Coba ekstrak JSON array
# # # # #                             match_bracket = re.search(r'(\[.*?\"key\":\s*\"ingredients\".*?\])', script.string, re.DOTALL)
# # # # #                             if match_bracket:
# # # # #                                 json_block = match_bracket.group(1)
# # # # #                                 temp_data = json.loads(json_block)
# # # # #                                 raw_html = find_ingredient_data(temp_data)
# # # # #                                 if raw_html:
# # # # #                                     soup_ingredients = BeautifulSoup(raw_html, 'html.parser')
# # # # #                                     ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
# # # # #                                     break
# # # # #                         except json.JSONDecodeError:
# # # # #                             pass
        
# # # # #         # 4. Menampilkan Hasil Variasi Produk
# # # # #         if variation_data:
# # # # #             print("\n" + "="*70)
# # # # #             print("## 💄 Hasil Ekstraksi Variasi Produk")
# # # # #             print("="*70)
# # # # #             print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian'}")
# # # # #             print("-" * 70)

# # # # #             for item in variation_data:
# # # # #                 sku = item.get('sku')
# # # # #                 in_stock = "Ready" if item.get('inStock') else "Kosong"
                
# # # # #                 try:
# # # # #                     price = item['price']['price']['displayValue']
# # # # #                 except (KeyError, TypeError):
# # # # #                     price = "N/A"
                
# # # # #                 try:
# # # # #                     color_name = item['choices'][0]['title']
# # # # #                 except (KeyError, IndexError, TypeError):
# # # # #                     color_name = item.get('title', 'Unknown')
                
# # # # #                 subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
# # # # #                 subscription_info = ""
# # # # #                 if subscription_contract:
# # # # #                     initial_price = subscription_contract['initialPrice']['price']['displayValue']
# # # # #                     freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
# # # # #                     subscription_info = f" (Subs: {initial_price}/{freq})"

# # # # #                 print(f"{sku:<10} | {in_stock:<10} | {price:<8} | {color_name}{subscription_info}")
# # # # #         else:
# # # # #             print("\n[INFO] Data variasi produk tidak ditemukan.")


# # # # #         # 5. Menampilkan Hasil Ingredients
# # # # #         if ingredients_content:
# # # # #             print("\n" + "="*70)
# # # # #             print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
# # # # #             print("="*70)
# # # # #             print(ingredients_content)
# # # # #             print("\n" + "="*70)
# # # # #         else:
# # # # #             print("\n[INFO] Key 'ingredients' tidak ditemukan di seluruh sumber data (JSON/HTML).")

# # # # #     except Exception as e:
# # # # #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # # # # --- Eksekusi Script ---
# # # # # print("--- UJI KASUS 1: RevitaLash (JSON Berhasil) ---")
# # # # # target_url_1 = "https://www.dermstore.com/p/revitalash-revitabrow-advanced-eyebrow-conditioner-3ml-4-month-supply/15724058/"
# # # # # scrape_dermstore_data(target_url_1)

# # # # # print("\n" + "#" * 70 + "\n")

# # # # # print("--- UJI KASUS 2: Wander Beauty (HTML Langsung) ---")
# # # # # target_url_2 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# # # # # scrape_dermstore_data(target_url_2)




# # # # import requests
# # # # import json
# # # # import re
# # # # from bs4 import BeautifulSoup
# # # # import sys 

# # # # sys.setrecursionlimit(3000)

# # # # # --- Fungsi Helper: Mencari Ingredients di HTML yang Dimuat ---
# # # # def extract_ingredients_from_html(soup):
# # # #     """Mencari blok HTML ingredients berdasarkan atribut unik."""
# # # #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    
# # # #     if target_div:
# # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # #         return clean_text
    
# # # #     return None

# # # # # --- Fungsi Helper: Mencari Brand di HTML yang Dimuat (Fallback) ---
# # # # def extract_brand_from_html(soup):
# # # #     """Mencari nama brand di HTML, biasanya di breadcrumb atau judul."""
# # # #     # Mencoba mencari elemen breadcrumb yang mengandung nama brand
# # # #     # Struktur umum Dermstore menggunakan link di breadcrumb
# # # #     breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
# # # #     if breadcrumb:
# # # #         # Nama brand seringkali adalah elemen <a> kedua di breadcrumb setelah "Home"
# # # #         brand_link = breadcrumb.find_all('li')
# # # #         if len(brand_link) > 1:
# # # #             # Mengambil link kedua atau ketiga
# # # #             brand_name = brand_link[-2].get_text(strip=True)
# # # #             if brand_name and brand_name.lower() != 'all brands':
# # # #                 return brand_name

# # # #     # Mencoba mencari tag <a> di dekat <h1> atau di atas judul produk
# # # #     brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
# # # #     if brand_link:
# # # #         return brand_link.get_text(strip=True)
        
# # # #     return None

# # # # # --- Fungsi find_ingredient_data dipertahankan ---
# # # # def find_ingredient_data(data):
# # # #     """Fungsi rekursif untuk mencari blok data 'ingredients' yang spesifik (dari JSON)."""
# # # #     if isinstance(data, dict):
# # # #         if data.get("key") == 'ingredients':
# # # #             try:
# # # #                 content_list = data['value']['richContentValue']['content']
# # # #                 for item in content_list:
# # # #                     if item['type'] == 'HTML':
# # # #                         return item['content']
# # # #             except (KeyError, TypeError):
# # # #                 pass
        
# # # #         for k, v in data.items():
# # # #             result = find_ingredient_data(v)
# # # #             if result: return result
            
# # # #     elif isinstance(data, list):
# # # #         for item in data:
# # # #             result = find_ingredient_data(item)
# # # #             if result: return result
            
# # # #     return None

# # # # def scrape_dermstore_data(url):
# # # #     """Mengambil data variasi produk, ingredients, dan brand dari URL Dermstore."""
# # # #     headers = {
# # # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# # # #         "Accept-Language": "en-US,en;q=0.9",
# # # #         "Referer": "https://www.google.com/"
# # # #     }

# # # #     print(f"Sedang mengambil data dari: {url} ...")
    
# # # #     try:
# # # #         response = requests.get(url, headers=headers, timeout=15)
        
# # # #         if response.status_code != 200:
# # # #             print(f"Gagal membuka halaman. Status code: {response.status_code}")
# # # #             return

# # # #         soup = BeautifulSoup(response.text, 'html.parser')
# # # #         scripts = soup.find_all('script')
        
# # # #         # Inisialisasi variabel data
# # # #         variation_data = None
# # # #         ingredients_content = None
# # # #         brand_name = None # <--- Variabel Brand Baru
        
# # # #         # 1. Cari Data Variasi (Prioritas Tinggi)
# # # #         for script in scripts:
# # # #             print(script)
# # # #             if script.string and "const variationData =" in script.string:
# # # #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# # # #                 if match:
# # # #                     try:
# # # #                         variation_data = json.loads(match.group(1))
# # # #                         break
# # # #                     except json.JSONDecodeError:
# # # #                         pass
        
# # # #         # 2. Ekstraksi Ingredients dan Brand dari Data Variasi (Jika Ditemukan)
# # # #         if variation_data:
# # # #             first_variation = variation_data[0]
# # # #             content_list = first_variation.get('content', [])

# # # #             for content_item in content_list:
# # # #                 # A. Ekstraksi Ingredients
# # # #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# # # #                     try:
# # # #                         content_html_list = content_item['value']['richContentValue']['content']
# # # #                         for html_block in content_html_list:
# # # #                             if html_block['type'] == 'HTML':
# # # #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# # # #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
                                
# # # #                     except (KeyError, TypeError):
# # # #                         pass
                
# # # #                 # B. Ekstraksi Brand
# # # #                 if content_item.get('key') == 'brand' and not brand_name:
# # # #                     try:
# # # #                         brand_list = content_item['value']['stringListValue']
# # # #                         if brand_list:
# # # #                             brand_name = brand_list[0]
# # # #                     except (KeyError, TypeError):
# # # #                         pass

# # # #         # 3. Fallback: Ekstraksi Ingredients dari HTML Langsung
# # # #         if not ingredients_content:
# # # #             ingredients_content = extract_ingredients_from_html(soup)
# # # #             if ingredients_content:
# # # #                 print("[INFO] Ingredients diekstrak langsung dari elemen HTML.")

# # # #         # 4. Fallback: Ekstraksi Brand dari HTML Langsung
# # # #         if not brand_name:
# # # #             brand_name = extract_brand_from_html(soup)
# # # #             if brand_name:
# # # #                 print(f"[INFO] Brand name '{brand_name}' diekstrak dari HTML.")


# # # #         # 5. Menampilkan Hasil Metadata
# # # #         print("\n" + "="*70)
# # # #         print("## 🏷️ Hasil Ekstraksi Metadata")
# # # #         print("="*70)
# # # #         print(f"{'Brand':<15}: {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
# # # #         # 6. Menampilkan Hasil Variasi Produk
# # # #         if variation_data:
# # # #             print("\n" + "="*70)
# # # #             print("## 💄 Hasil Ekstraksi Variasi Produk")
# # # #             print("="*70)
# # # #             print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian'}")
# # # #             print("-" * 70)

# # # #             for item in variation_data:
# # # #                 sku = item.get('sku')
# # # #                 in_stock = "Ready" if item.get('inStock') else "Kosong"
                
# # # #                 try:
# # # #                     price = item['price']['price']['displayValue']
# # # #                 except (KeyError, TypeError):
# # # #                     price = "N/A"
                
# # # #                 try:
# # # #                     color_name = item['choices'][0]['title']
# # # #                 except (KeyError, IndexError, TypeError):
# # # #                     color_name = item.get('title', 'Unknown')
                
# # # #                 subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
# # # #                 subscription_info = ""
# # # #                 if subscription_contract:
# # # #                     initial_price = subscription_contract['initialPrice']['price']['displayValue']
# # # #                     freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
# # # #                     subscription_info = f" (Subs: {initial_price}/{freq})"

# # # #                 print(f"{sku:<10} | {in_stock:<10} | {price:<8} | {color_name}{subscription_info}")
# # # #         else:
# # # #             print("\n[INFO] Data variasi produk tidak ditemukan.")


# # # #         # 7. Menampilkan Hasil Ingredients
# # # #         if ingredients_content:
# # # #             print("\n" + "="*70)
# # # #             print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
# # # #             print("="*70)
# # # #             print(ingredients_content)
# # # #             print("\n" + "="*70)
# # # #         else:
# # # #             print("\n[INFO] Key 'ingredients' tidak ditemukan di seluruh sumber data (JSON/HTML).")

# # # #     except Exception as e:
# # # #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # # # --- Eksekusi Script ---
# # # # print("--- UJI KASUS 1: RevitaLash (Brand dari JSON) ---")
# # # # target_url_1 = "https://www.dermstore.com/p/revitalash-revitabrow-advanced-eyebrow-conditioner-3ml-4-month-supply/15724058/"
# # # # scrape_dermstore_data(target_url_1)

# # # # print("\n" + "#" * 70 + "\n")

# # # # print("--- UJI KASUS 2: Wander Beauty (Brand dari HTML) ---")
# # # # target_url_2 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# # # # scrape_dermstore_data(target_url_2)



# # # import requests
# # # import json
# # # import re
# # # from bs4 import BeautifulSoup
# # # import sys 

# # # sys.setrecursionlimit(3000)

# # # # --- FUNGSI BARU: Mencari dan Mengekstrak Rating/Review dari JSON-LD ---
# # # def extract_rating_and_reviews(soup):
# # #     """Mencari dan mengekstrak data Rating dan Review dari blok JSON-LD (Schema.org)."""
    
# # #     # 1. Cari semua script tag dengan tipe application/ld+json
# # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
# # #     rating_data = None
# # #     review_list = []

# # #     for script in json_ld_scripts:
# # #         if script.string:
# # #             try:
# # #                 data = json.loads(script.string)
                
# # #                 # Cek jika data adalah list (kadang ada beberapa objek di root)
# # #                 if isinstance(data, list):
# # #                     data = next((item for item in data if item.get("@type") == "Product"), None)

# # #                 # Pastikan ini adalah objek Product
# # #                 if isinstance(data, dict) and data.get("@type") == "Product":
                    
# # #                     # Ekstrak Aggregate Rating
# # #                     aggregate_rating = data.get("aggregateRating")
# # #                     if aggregate_rating:
# # #                         rating_data = {
# # #                             'value': aggregate_rating.get('ratingValue'),
# # #                             'count': aggregate_rating.get('reviewCount')
# # #                         }
                    
# # #                     # Ekstrak Individual Reviews
# # #                     reviews = data.get("review")
# # #                     if reviews:
# # #                         # Kita hanya ambil 3 review pertama sebagai contoh
# # #                         for review in reviews[:3]: 
# # #                             review_list.append({
# # #                                 'rating': review['reviewRating'].get('ratingValue', 'N/A'),
# # #                                 'author': review['author'].get('name', 'Anonymous'),
# # #                                 'body': review.get('reviewBody', 'No body text'),
# # #                                 'date': review.get('datePublished', 'N/A')
# # #                             })
                    
# # #                     # Setelah menemukan data produk, kita bisa berhenti
# # #                     if rating_data or review_list:
# # #                         return rating_data, review_list
                        
# # #             except json.JSONDecodeError:
# # #                 # Abaikan jika ada blok JSON-LD yang rusak
# # #                 continue
    
# # #     return rating_data, review_list

# # # # --- FUNGSI HELPER LAINNYA DI PERTAHANKAN (omitted for brevity) ---
# # # def extract_ingredients_from_html(soup):
# # #     """Mencari blok HTML ingredients berdasarkan atribut unik."""
# # #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
# # #     if target_div:
# # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # #         return clean_text
# # #     return None

# # # def extract_brand_from_html(soup):
# # #     """Mencari nama brand di HTML, biasanya di breadcrumb atau judul."""
# # #     breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
# # #     if breadcrumb:
# # #         brand_link = breadcrumb.find_all('li')
# # #         if len(brand_link) > 1:
# # #             brand_name = brand_link[-2].get_text(strip=True)
# # #             if brand_name and brand_name.lower() != 'all brands':
# # #                 return brand_name
# # #     brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
# # #     if brand_link:
# # #         return brand_link.get_text(strip=True)
# # #     return None

# # # def find_ingredient_data(data):
# # #     """Fungsi rekursif untuk mencari blok data 'ingredients' yang spesifik (dari JSON)."""
# # #     if isinstance(data, dict):
# # #         if data.get("key") == 'ingredients':
# # #             try:
# # #                 content_list = data['value']['richContentValue']['content']
# # #                 for item in content_list:
# # #                     if item['type'] == 'HTML':
# # #                         return item['content']
# # #             except (KeyError, TypeError):
# # #                 pass
# # #         for k, v in data.items():
# # #             result = find_ingredient_data(v)
# # #             if result: return result
# # #     elif isinstance(data, list):
# # #         for item in data:
# # #             result = find_ingredient_data(item)
# # #             if result: return result
# # #     return None

# # # def scrape_dermstore_data(url):
# # #     """Mengambil data variasi, ingredients, brand, rating, dan reviews dari URL Dermstore."""
# # #     headers = {
# # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# # #         "Accept-Language": "en-US,en;q=0.9",
# # #         "Referer": "https://www.google.com/"
# # #     }

# # #     print(f"Sedang mengambil data dari: {url} ...")
    
# # #     try:
# # #         response = requests.get(url, headers=headers, timeout=15)
        
# # #         if response.status_code != 200:
# # #             print(f"Gagal membuka halaman. Status code: {response.status_code}")
# # #             return

# # #         soup = BeautifulSoup(response.text, 'html.parser')
# # #         scripts = soup.find_all('script')
        
# # #         # Inisialisasi variabel data
# # #         variation_data = None
# # #         ingredients_content = None
# # #         brand_name = None 
        
# # #         # 0. Ekstraksi Rating dan Reviews (Pencarian JSON-LD)
# # #         rating_data, review_list = extract_rating_and_reviews(soup)
        
# # #         # 1. Cari Data Variasi (Prioritas Tinggi)
# # #         for script in scripts:
# # #             if script.string and "const variationData =" in script.string:
# # #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# # #                 if match:
# # #                     try:
# # #                         variation_data = json.loads(match.group(1))
# # #                         break
# # #                     except json.JSONDecodeError:
# # #                         pass
        
# # #         # 2. Ekstraksi Ingredients dan Brand dari Data Variasi (Jika Ditemukan)
# # #         if variation_data:
# # #             first_variation = variation_data[0]
# # #             content_list = first_variation.get('content', [])

# # #             for content_item in content_list:
# # #                 # A. Ekstraksi Ingredients
# # #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# # #                     try:
# # #                         content_html_list = content_item['value']['richContentValue']['content']
# # #                         for html_block in content_html_list:
# # #                             if html_block['type'] == 'HTML':
# # #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# # #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
                                
# # #                     except (KeyError, TypeError):
# # #                         pass
                
# # #                 # B. Ekstraksi Brand
# # #                 if content_item.get('key') == 'brand' and not brand_name:
# # #                     try:
# # #                         brand_list = content_item['value']['stringListValue']
# # #                         if brand_list:
# # #                             brand_name = brand_list[0]
# # #                     except (KeyError, TypeError):
# # #                         pass

# # #         # 3. Fallback: Ekstraksi Ingredients dari HTML Langsung
# # #         if not ingredients_content:
# # #             ingredients_content = extract_ingredients_from_html(soup)
# # #             if ingredients_content:
# # #                 pass

# # #         # 4. Fallback: Ekstraksi Brand dari HTML Langsung
# # #         if not brand_name:
# # #             brand_name = extract_brand_from_html(soup)
# # #             if brand_name:
# # #                 pass


# # #         # 5. Menampilkan Hasil Metadata
# # #         print("\n" + "="*70)
# # #         print("## 🏷️ Hasil Ekstraksi Metadata")
# # #         print("="*70)
# # #         print(f"{'Brand':<15}: {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
# # #         if rating_data:
# # #             print(f"{'Rating':<15}: {rating_data['value']} ({rating_data['count']} reviews)")
# # #         else:
# # #             print(f"{'Rating':<15}: TIDAK DITEMUKAN")


# # #         # 6. Menampilkan Hasil Variasi Produk
# # #         if variation_data:
# # #             # (Output Variasi Produk tetap sama)
# # #             print("\n" + "="*70)
# # #             print("## 💄 Hasil Ekstraksi Variasi Produk")
# # #             print("="*70)
# # #             print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian'}")
# # #             print("-" * 70)

# # #             for item in variation_data:
# # #                 sku = item.get('sku')
# # #                 in_stock = "Ready" if item.get('inStock') else "Kosong"
# # #                 try:
# # #                     price = item['price']['price']['displayValue']
# # #                 except (KeyError, TypeError):
# # #                     price = "N/A"
# # #                 try:
# # #                     color_name = item['choices'][0]['title']
# # #                 except (KeyError, IndexError, TypeError):
# # #                     color_name = item.get('title', 'Unknown')
# # #                 subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
# # #                 subscription_info = ""
# # #                 if subscription_contract:
# # #                     initial_price = subscription_contract['initialPrice']['price']['displayValue']
# # #                     freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
# # #                     subscription_info = f" (Subs: {initial_price}/{freq})"

# # #                 print(f"{sku:<10} | {in_stock:<10} | {price:<8} | {color_name}{subscription_info}")
# # #         else:
# # #             print("\n[INFO] Data variasi produk tidak ditemukan.")


# # #         # 7. Menampilkan Hasil Ingredients
# # #         if ingredients_content:
# # #             # (Output Ingredients tetap sama)
# # #             print("\n" + "="*70)
# # #             print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
# # #             print("="*70)
# # #             print(ingredients_content)
# # #             print("\n" + "="*70)
        
# # #         # 8. Menampilkan Ulasan (Review)
# # #         if review_list:
# # #             print("\n" + "="*70)
# # #             print("## ⭐ Ulasan Terbaru (Reviews)")
# # #             print("="*70)
# # #             for i, review in enumerate(review_list):
# # #                 print(f"--- Review {i+1} ({review['date']}) ---")
# # #                 print(f"Rating: {review['rating']}/5 by {review['author']}")
# # #                 print(f"Ulasan: {review['body']}")
# # #             print("\n" + "="*70)
# # #         else:
# # #             print("\n[INFO] Data ulasan (review) tidak ditemukan.")


# # #     except Exception as e:
# # #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # # --- Eksekusi Script ---
# # # print("--- UJI KASUS 1: RevitaLash (JSON-LD & JSON Variasi Berhasil) ---")
# # # target_url_1 = "https://www.dermstore.com/p/revitalash-revitabrow-advanced-eyebrow-conditioner-3ml-4-month-supply/15724058/"
# # # scrape_dermstore_data(target_url_1)

# # # print("\n" + "#" * 70 + "\n")

# # # print("--- UJI KASUS 2: Wander Beauty (HTML Fallback) ---")
# # # target_url_2 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# # # scrape_dermstore_data(target_url_2)



# # import requests
# # import json
# # import re
# # from bs4 import BeautifulSoup
# # import sys 

# # sys.setrecursionlimit(3000)

# # # --- FUNGSI HELPER BARU: Product Overview dari HTML ---
# # def extract_product_overview_from_html(soup):
# #     """Mencari blok HTML Product Overview berdasarkan atribut unik (Fallback)."""
# #     # Mencari div konten yang terkait dengan 'Product Overview'
# #     target_div = soup.find('div', {'id': 'product-description-0'})
    
# #     if not target_div:
# #         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})

# #     if target_div:
# #         # Kita ambil teks dari seluruh konten di dalamnya, lalu membersihkannya
# #         clean_text = target_div.get_text(separator='\n', strip=True)
# #         return clean_text
    
# #     return None

# # # --- FUNGSI HELPER LAINNYA ---
# # def extract_ingredients_from_html(soup):
# #     """Mencari blok HTML ingredients berdasarkan atribut unik."""
# #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
# #     if target_div:
# #         clean_text = target_div.get_text(separator='\n', strip=True)
# #         return clean_text
# #     return None

# # def extract_brand_from_html(soup):
# #     """Mencari nama brand di HTML."""
# #     breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
# #     if breadcrumb:
# #         brand_link = breadcrumb.find_all('li')
# #         if len(brand_link) > 1:
# #             brand_name = brand_link[-2].get_text(strip=True)
# #             if brand_name and brand_name.lower() != 'all brands':
# #                 return brand_name
# #     brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
# #     if brand_link:
# #         return brand_link.get_text(strip=True)
# #     return None

# # def extract_rating_and_reviews(soup):
# #     """Mencari dan mengekstrak data Rating dan Review dari blok JSON-LD."""
# #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
# #     rating_data = None
# #     review_list = []
# #     for script in json_ld_scripts:
# #         if script.string:
# #             try:
# #                 data = json.loads(script.string)
# #                 if isinstance(data, list):
# #                     data = next((item for item in data if item.get("@type") == "Product"), None)
# #                 if isinstance(data, dict) and data.get("@type") == "Product":
# #                     aggregate_rating = data.get("aggregateRating")
# #                     if aggregate_rating:
# #                         rating_data = {'value': aggregate_rating.get('ratingValue'), 'count': aggregate_rating.get('reviewCount')}
# #                     reviews = data.get("review")
# #                     if reviews:
# #                         for review in reviews[:3]: 
# #                             review_list.append({
# #                                 'rating': review['reviewRating'].get('ratingValue', 'N/A'),
# #                                 'author': review['author'].get('name', 'Anonymous'),
# #                                 'body': review.get('reviewBody', 'No body text'),
# #                                 'date': review.get('datePublished', 'N/A')
# #                             })
# #                     if rating_data or review_list:
# #                         return rating_data, review_list
# #             except json.JSONDecodeError:
# #                 continue
# #     return rating_data, review_list

# # def find_ingredient_data(data):
# #     """Fungsi rekursif untuk mencari blok data 'ingredients' yang spesifik (dari JSON)."""
# #     if isinstance(data, dict):
# #         if data.get("key") == 'ingredients':
# #             try:
# #                 content_list = data['value']['richContentValue']['content']
# #                 for item in content_list:
# #                     if item['type'] == 'HTML':
# #                         return item['content']
# #             except (KeyError, TypeError):
# #                 pass
# #         for k, v in data.items():
# #             result = find_ingredient_data(v)
# #             if result: return result
# #     elif isinstance(data, list):
# #         for item in data:
# #             result = find_ingredient_data(item)
# #             if result: return result
# #     return None

# # def scrape_dermstore_data(url):
# #     """Mengambil semua data produk (variasi, ingredients, brand, rating, overview) dari URL Dermstore."""
# #     headers = {
# #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# #         "Accept-Language": "en-US,en;q=0.9",
# #         "Referer": "https://www.google.com/"
# #     }

# #     print(f"Sedang mengambil data dari: {url} ...")
    
# #     try:
# #         response = requests.get(url, headers=headers, timeout=15)
        
# #         if response.status_code != 200:
# #             print(f"Gagal membuka halaman. Status code: {response.status_code}")
# #             return

# #         soup = BeautifulSoup(response.text, 'html.parser')
# #         scripts = soup.find_all('script')
        
# #         # Inisialisasi variabel data
# #         variation_data = None
# #         ingredients_content = None
# #         brand_name = None 
# #         overview_content = None # <--- Variabel Overview Baru
        
# #         # 0. Ekstraksi Rating dan Reviews (JSON-LD)
# #         rating_data, review_list = extract_rating_and_reviews(soup)
        
# #         # 1. Cari Data Variasi (Prioritas Tinggi)
# #         for script in scripts:
# #             if script.string and "const variationData =" in script.string:
# #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# #                 if match:
# #                     try:
# #                         variation_data = json.loads(match.group(1))
# #                         break
# #                     except json.JSONDecodeError:
# #                         pass
        
# #         # 2. Ekstraksi Overview, Ingredients, dan Brand dari Data Variasi (Jika Ditemukan)
# #         if variation_data:
# #             first_variation = variation_data[0]
# #             content_list = first_variation.get('content', [])

# #             for content_item in content_list:
                
# #                 # A. Ekstraksi Product Overview (synopsis)
# #                 if content_item.get('key') == 'synopsis' and not overview_content:
# #                     try:
# #                         # Path untuk mendapatkan konten HTML (ProductContentRichContentListValue)
# #                         content_list_value = content_item['value']['richContentListValue'][0]['content']
# #                         for html_block in content_list_value:
# #                             if html_block['type'] == 'HTML':
# #                                 soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
# #                                 overview_content = soup_overview.get_text(separator="\n", strip=True)
# #                                 break
# #                     except (KeyError, TypeError, IndexError):
# #                         pass

# #                 # B. Ekstraksi Ingredients
# #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# #                     try:
# #                         content_html_list = content_item['value']['richContentValue']['content']
# #                         for html_block in content_html_list:
# #                             if html_block['type'] == 'HTML':
# #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
                                
# #                     except (KeyError, TypeError):
# #                         pass
                
# #                 # C. Ekstraksi Brand
# #                 if content_item.get('key') == 'brand' and not brand_name:
# #                     try:
# #                         brand_list = content_item['value']['stringListValue']
# #                         if brand_list:
# #                             brand_name = brand_list[0]
# #                     except (KeyError, TypeError):
# #                         pass

# #         # 3. Fallback: Ekstraksi Overview dari HTML Langsung
# #         if not overview_content:
# #             overview_content = extract_product_overview_from_html(soup)
        
# #         # 4. Fallback: Ekstraksi Ingredients dari HTML Langsung
# #         if not ingredients_content:
# #             ingredients_content = extract_ingredients_from_html(soup)

# #         # 5. Fallback: Ekstraksi Brand dari HTML Langsung
# #         if not brand_name:
# #             brand_name = extract_brand_from_html(soup)


# #         # 6. Menampilkan Hasil Metadata
# #         print("\n" + "="*70)
# #         print("## 🏷️ Hasil Ekstraksi Metadata")
# #         print("="*70)
# #         print(f"{'Brand':<15}: {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
# #         if rating_data:
# #             print(f"{'Rating':<15}: {rating_data['value']} ({rating_data['count']} reviews)")
# #         else:
# #             print(f"{'Rating':<15}: TIDAK DITEMUKAN")
            
        
# #         # 7. Menampilkan Product Overview
# #         if overview_content:
# #             print("\n" + "="*70)
# #             print("## 📄 Product Overview")
# #             print("="*70)
# #             print(overview_content)
# #         else:
# #             print("\n[INFO] Product Overview tidak ditemukan.")

        
# #         # 8. Menampilkan Hasil Variasi Produk
# #         if variation_data:
# #             print("\n" + "="*70)
# #             print("## 💄 Hasil Ekstraksi Variasi Produk")
# #             print("="*70)
# #             print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian'}")
# #             print("-" * 70)

# #             for item in variation_data:
# #                 sku = item.get('sku')
# #                 in_stock = "Ready" if item.get('inStock') else "Kosong"
                
# #                 try:
# #                     price = item['price']['price']['displayValue']
# #                 except (KeyError, TypeError):
# #                     price = "N/A"
                
# #                 try:
# #                     color_name = item['choices'][0]['title']
# #                 except (KeyError, IndexError, TypeError):
# #                     color_name = item.get('title', 'Unknown')
                
# #                 subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
# #                 subscription_info = ""
# #                 if subscription_contract:
# #                     initial_price = subscription_contract['initialPrice']['price']['displayValue']
# #                     freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
# #                     subscription_info = f" (Subs: {initial_price}/{freq})"

# #                 print(f"{sku:<10} | {in_stock:<10} | {price:<8} | {color_name}{subscription_info}")
# #         else:
# #             pass # Sudah ditangani di awal


# #         # 9. Menampilkan Hasil Ingredients
# #         if ingredients_content:
# #             print("\n" + "="*70)
# #             print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
# #             print("="*70)
# #             print(ingredients_content)
# #             print("\n" + "="*70)
# #         else:
# #             print("\n[INFO] Key 'ingredients' tidak ditemukan.")
        
# #         # 10. Menampilkan Ulasan (Review)
# #         if review_list:
# #             print("\n" + "="*70)
# #             print("## ⭐ Ulasan Terbaru (Reviews)")
# #             print("="*70)
# #             for i, review in enumerate(review_list):
# #                 print(f"--- Review {i+1} ({review['date']}) ---")
# #                 print(f"Rating: {review['rating']}/5 by {review['author']}")
# #                 print(f"Ulasan: {review['body']}")
# #             print("\n" + "="*70)
# #         else:
# #             print("\n[INFO] Data ulasan (review) tidak ditemukan.")


# #     except Exception as e:
# #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # --- Eksekusi Script ---
# # print("--- UJI KASUS 1: RevitaLash (Overview dari JSON) ---")
# # target_url_1 = "https://www.dermstore.com/p/revitalash-revitabrow-advanced-eyebrow-conditioner-3ml-4-month-supply/15724058/"
# # scrape_dermstore_data(target_url_1)

# # print("\n" + "#" * 70 + "\n")

# # print("--- UJI KASUS 2: Wander Beauty (Overview diharapkan dari HTML/JSON-LD) ---")
# # target_url_2 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# # scrape_dermstore_data(target_url_2)




# import requests
# import json
# import re
# from bs4 import BeautifulSoup
# import sys 

# sys.setrecursionlimit(3000)

# # --- FUNGSI HELPER LAINNYA DI PERTAHANKAN (omitted for brevity) ---
# def extract_product_overview_from_html(soup):
#     target_div = soup.find('div', {'id': 'product-description-0'})
#     if not target_div:
#         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
#     if target_div:
#         clean_text = target_div.get_text(separator='\n', strip=True)
#         return clean_text
#     return None

# def extract_ingredients_from_html(soup):
#     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
#     if target_div:
#         clean_text = target_div.get_text(separator='\n', strip=True)
#         return clean_text
#     return None

# def extract_brand_from_html(soup):
#     breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
#     if breadcrumb:
#         brand_link = breadcrumb.find_all('li')
#         if len(brand_link) > 1:
#             brand_name = brand_link[-2].get_text(strip=True)
#             if brand_name and brand_name.lower() != 'all brands':
#                 return brand_name
#     brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
#     if brand_link:
#         return brand_link.get_text(strip=True)
#     return None

# def extract_rating_and_reviews(soup):
#     json_ld_scripts = soup.find_all('script', type='application/ld+json')
#     rating_data = None
#     review_list = []
#     for script in json_ld_scripts:
#         if script.string:
#             try:
#                 data = json.loads(script.string)
#                 if isinstance(data, list):
#                     data = next((item for item in data if item.get("@type") == "Product"), None)
#                 if isinstance(data, dict) and data.get("@type") == "Product":
#                     aggregate_rating = data.get("aggregateRating")
#                     if aggregate_rating:
#                         rating_data = {'value': aggregate_rating.get('ratingValue'), 'count': aggregate_rating.get('reviewCount')}
#                     reviews = data.get("review")
#                     if reviews:
#                         for review in reviews[:3]: 
#                             review_list.append({
#                                 'rating': review['reviewRating'].get('ratingValue', 'N/A'),
#                                 'author': review['author'].get('name', 'Anonymous'),
#                                 'body': review.get('reviewBody', 'No body text'),
#                                 'date': review.get('datePublished', 'N/A')
#                             })
#                     if rating_data or review_list:
#                         return rating_data, review_list
#             except json.JSONDecodeError:
#                 continue
#     return rating_data, review_list

# def find_ingredient_data(data):
#     if isinstance(data, dict):
#         if data.get("key") == 'ingredients':
#             try:
#                 content_list = data['value']['richContentValue']['content']
#                 for item in content_list:
#                     if item['type'] == 'HTML':
#                         return item['content']
#             except (KeyError, TypeError):
#                 pass
#         for k, v in data.items():
#             result = find_ingredient_data(v)
#             if result: return result
#     elif isinstance(data, list):
#         for item in data:
#             result = find_ingredient_data(item)
#             if result: return result
#     return None
# # -----------------------------------------------

# def scrape_dermstore_data(url):
#     """Mengambil semua data produk (variasi, ingredients, brand, rating, overview, image URL) dari URL Dermstore."""
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": "https://www.google.com/"
#     }

#     print(f"Sedang mengambil data dari: {url} ...")
    
#     try:
#         response = requests.get(url, headers=headers, timeout=15)
        
#         if response.status_code != 200:
#             print(f"Gagal membuka halaman. Status code: {response.status_code}")
#             return

#         soup = BeautifulSoup(response.text, 'html.parser')
#         scripts = soup.find_all('script')
        
#         # Inisialisasi variabel data
#         variation_data = None
#         ingredients_content = None
#         brand_name = None 
#         overview_content = None
        
#         # 0. Ekstraksi Rating dan Reviews (JSON-LD)
#         rating_data, review_list = extract_rating_and_reviews(soup)
        
#         # 1. Cari Data Variasi (Prioritas Tinggi)
#         for script in scripts:
#             if script.string and "const variationData =" in script.string:
#                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
#                 if match:
#                     try:
#                         variation_data = json.loads(match.group(1))
#                         break
#                     except json.JSONDecodeError:
#                         pass
        
#         # 2. Ekstraksi Konten (Overview, Ingredients, Brand) dari Data Variasi (Jika Ditemukan)
#         if variation_data:
#             first_variation = variation_data[0]
#             content_list = first_variation.get('content', [])

#             for content_item in content_list:
                
#                 # A. Ekstraksi Product Overview (synopsis)
#                 if content_item.get('key') == 'synopsis' and not overview_content:
#                     try:
#                         content_list_value = content_item['value']['richContentListValue'][0]['content']
#                         for html_block in content_list_value:
#                             if html_block['type'] == 'HTML':
#                                 soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
#                                 overview_content = soup_overview.get_text(separator="\n", strip=True)
#                                 break
#                     except (KeyError, TypeError, IndexError):
#                         pass

#                 # B. Ekstraksi Ingredients
#                 if content_item.get('key') == 'ingredients' and not ingredients_content:
#                     try:
#                         content_html_list = content_item['value']['richContentValue']['content']
#                         for html_block in content_html_list:
#                             if html_block['type'] == 'HTML':
#                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
#                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
                                
#                     except (KeyError, TypeError):
#                         pass
                
#                 # C. Ekstraksi Brand
#                 if content_item.get('key') == 'brand' and not brand_name:
#                     try:
#                         brand_list = content_item['value']['stringListValue']
#                         if brand_list:
#                             brand_name = brand_list[0]
#                     except (KeyError, TypeError):
#                         pass

#         # 3. Fallback: Ekstraksi Overview dari HTML Langsung
#         if not overview_content:
#             overview_content = extract_product_overview_from_html(soup)
        
#         # 4. Fallback: Ekstraksi Ingredients dari HTML Langsung
#         if not ingredients_content:
#             ingredients_content = extract_ingredients_from_html(soup)

#         # 5. Fallback: Ekstraksi Brand dari HTML Langsung
#         if not brand_name:
#             brand_name = extract_brand_from_html(soup)


#         # 6. Menampilkan Hasil Metadata
#         print("\n" + "="*120)
#         print("## 🏷️ Hasil Ekstraksi Metadata")
#         print("="*120)
#         print(f"{'Brand':<15}: {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
#         if rating_data:
#             print(f"{'Rating':<15}: {rating_data['value']} ({rating_data['count']} reviews)")
#         else:
#             print(f"{'Rating':<15}: TIDAK DITEMUKAN")
            
        
#         # 7. Menampilkan Product Overview
#         if overview_content:
#             print("\n" + "="*120)
#             print("## 📄 Product Overview")
#             print("="*120)
#             print(overview_content)
#         else:
#             print("\n[INFO] Product Overview tidak ditemukan.")

        
#         # 8. Menampilkan Hasil Variasi Produk (DENGAN IMAGE URL)
#         if variation_data:
#             print("\n" + "="*120)
#             print("## 💄 Hasil Ekstraksi Variasi Produk")
#             print("="*120)
#             # Menyesuaikan lebar kolom untuk menampung URL
#             print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian':<40} | {'Image URL'}")
#             print("-" * 120)

#             for item in variation_data:
#                 sku = item.get('sku')
#                 in_stock = "Ready" if item.get('inStock') else "Kosong"
                
#                 try:
#                     price = item['price']['price']['displayValue']
#                 except (KeyError, TypeError):
#                     price = "N/A"
                
#                 try:
#                     color_name = item['choices'][0]['title']
#                 except (KeyError, IndexError, TypeError):
#                     color_name = item.get('title', 'Unknown')
                
#                 # --- EKSTRAKSI IMAGE URL BARU ---
#                 image_url = "N/A"
#                 try:
#                     # Ambil URL 'original' dari gambar pertama di array 'images'
#                     image_url = item['images'][0]['original']
#                 except (KeyError, IndexError, TypeError):
#                     pass # Biarkan N/A jika tidak ditemukan
#                 # --------------------------------

#                 subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
#                 subscription_info = ""
#                 if subscription_contract:
#                     initial_price = subscription_contract['initialPrice']['price']['displayValue']
#                     freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
#                     subscription_info = f" (Subs: {initial_price}/{freq})"

#                 print(f"{sku:<10} | {in_stock:<10} | {price:<8} | {color_name + subscription_info:<40} | {image_url}")
#         else:
#             pass 


#         # 9. Menampilkan Hasil Ingredients
#         if ingredients_content:
#             print("\n" + "="*120)
#             print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
#             print("="*120)
#             print(ingredients_content)
#             print("\n" + "="*120)
#         else:
#             print("\n[INFO] Key 'ingredients' tidak ditemukan.")
        
#         # 10. Menampilkan Ulasan (Review)
#         if review_list:
#             print("\n" + "="*120)
#             print("## ⭐ Ulasan Terbaru (Reviews)")
#             print("="*120)
#             for i, review in enumerate(review_list):
#                 print(f"--- Review {i+1} ({review['date']}) ---")
#                 print(f"Rating: {review['rating']}/5 by {review['author']}")
#                 print(f"Ulasan: {review['body']}")
#             print("\n" + "="*120)
#         else:
#             print("\n[INFO] Data ulasan (review) tidak ditemukan.")


#     except Exception as e:
#         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # --- Eksekusi Script ---
# print("--- UJI KASUS 1: RevitaLash ---")
# target_url_1 = "https://www.dermstore.com/p/revitalash-revitabrow-advanced-eyebrow-conditioner-3ml-4-month-supply/15724058/"
# scrape_dermstore_data(target_url_1)

# print("\n" + "#" * 120 + "\n")

# print("--- UJI KASUS 2: Wander Beauty ---")
# target_url_2 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# scrape_dermstore_data(target_url_2)




import requests
import json
import re
from bs4 import BeautifulSoup
import sys 

sys.setrecursionlimit(3000)

# --- FUNGSI HELPER LAINNYA DI PERTAHANKAN (omitted for brevity) ---
def extract_product_overview_from_html(soup):
    target_div = soup.find('div', {'id': 'product-description-0'})
    if not target_div:
        target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return None

def extract_ingredients_from_html(soup):
    target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return None

def extract_brand_from_html(soup):
    breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
    if breadcrumb:
        brand_link = breadcrumb.find_all('li')
        if len(brand_link) > 1:
            brand_name = brand_link[-2].get_text(strip=True)
            if brand_name and brand_name.lower() != 'all brands':
                return brand_name
    brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
    if brand_link:
        return brand_link.get_text(strip=True)
    return None

def extract_rating_and_reviews(soup):
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    rating_data = None
    review_list = []
    for script in json_ld_scripts:
        if script.string:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = next((item for item in data if item.get("@type") == "Product"), None)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    aggregate_rating = data.get("aggregateRating")
                    if aggregate_rating:
                        rating_data = {'value': aggregate_rating.get('ratingValue'), 'count': aggregate_rating.get('reviewCount')}
                    reviews = data.get("review")
                    if reviews:
                        for review in reviews[:3]: 
                            review_list.append({
                                'rating': review['reviewRating'].get('ratingValue', 'N/A'),
                                'author': review['author'].get('name', 'Anonymous'),
                                'body': review.get('reviewBody', 'No body text'),
                                'date': review.get('datePublished', 'N/A')
                            })
                    if rating_data or review_list:
                        return rating_data, review_list
            except json.JSONDecodeError:
                continue
    return rating_data, review_list

def find_ingredient_data(data):
    if isinstance(data, dict):
        if data.get("key") == 'ingredients':
            try:
                content_list = data['value']['richContentValue']['content']
                for item in content_list:
                    if item['type'] == 'HTML':
                        return item['content']
            except (KeyError, TypeError):
                pass
        for k, v in data.items():
            result = find_ingredient_data(v)
            if result: return result
    elif isinstance(data, list):
        for item in data:
            result = find_ingredient_data(item)
            if result: return result
    return None
# -----------------------------------------------

def scrape_dermstore_data(url):
    """Mengambil semua data produk (variasi, ingredients, brand, rating, overview, image URL) dari URL Dermstore."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"Sedang mengambil data dari: {url} ...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Gagal membuka halaman. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        # Inisialisasi variabel data
        variation_data = None
        ingredients_content = None
        brand_name = None 
        overview_content = None
        
        # 0. Ekstraksi Rating dan Reviews (JSON-LD)
        rating_data, review_list = extract_rating_and_reviews(soup)
        
        # 1. Cari Data Variasi (Prioritas Tinggi)
        for script in scripts:
            if script.string and "const variationData =" in script.string:
                match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if match:
                    try:
                        variation_data = json.loads(match.group(1))
                        break
                    except json.JSONDecodeError:
                        pass
        
        # 2. Ekstraksi Konten (Overview, Ingredients, Brand) dari Data Variasi (Jika Ditemukan)
        if variation_data:
            first_variation = variation_data[0]
            content_list = first_variation.get('content', [])

            for content_item in content_list:
                
                # A. Ekstraksi Product Overview (synopsis)
                if content_item.get('key') == 'synopsis' and not overview_content:
                    try:
                        content_list_value = content_item['value']['richContentListValue'][0]['content']
                        for html_block in content_list_value:
                            if html_block['type'] == 'HTML':
                                soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
                                overview_content = soup_overview.get_text(separator="\n", strip=True)
                                break
                    except (KeyError, TypeError, IndexError):
                        pass

                # B. Ekstraksi Ingredients
                if content_item.get('key') == 'ingredients' and not ingredients_content:
                    try:
                        content_html_list = content_item['value']['richContentValue']['content']
                        for html_block in content_html_list:
                            if html_block['type'] == 'HTML':
                                soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
                                ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
                                
                    except (KeyError, TypeError):
                        pass
                
                # C. Ekstraksi Brand
                if content_item.get('key') == 'brand' and not brand_name:
                    try:
                        brand_list = content_item['value']['stringListValue']
                        if brand_list:
                            brand_name = brand_list[0]
                    except (KeyError, TypeError):
                        pass

        # 3. Fallback: Ekstraksi Overview dari HTML Langsung
        if not overview_content:
            overview_content = extract_product_overview_from_html(soup)
        
        # 4. Fallback: Ekstraksi Ingredients dari HTML Langsung
        if not ingredients_content:
            ingredients_content = extract_ingredients_from_html(soup)

        # 5. Fallback: Ekstraksi Brand dari HTML Langsung
        if not brand_name:
            brand_name = extract_brand_from_html(soup)


        # 6. Menampilkan Hasil Metadata
        print("\n" + "="*120)
        print("## 🏷️ Hasil Ekstraksi Metadata")
        print("="*120)
        print(f"{'Brand':<15}: {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
        if rating_data:
            print(f"{'Rating':<15}: {rating_data['value']} ({rating_data['count']} reviews)")
        else:
            print(f"{'Rating':<15}: TIDAK DITEMUKAN")
            
        
        # 7. Menampilkan Product Overview
        if overview_content:
            print("\n" + "="*120)
            print("## 📄 Product Overview")
            print("="*120)
            print(overview_content)
        else:
            print("\n[INFO] Product Overview tidak ditemukan.")

        
        # 8. Menampilkan Hasil Variasi Produk (DENGAN IMAGE URL)
        if variation_data:
            print("\n" + "="*120)
            print("## 💄 Hasil Ekstraksi Variasi Produk")
            print("="*120)
            # Menyesuaikan lebar kolom untuk menampung URL
            print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian':<40} | {'Image URL'}")
            print("-" * 120)

            for item in variation_data:
                sku = item.get('sku')
                in_stock = "Ready" if item.get('inStock') else "Kosong"
                
                try:
                    price = item['price']['price']['displayValue']
                except (KeyError, TypeError):
                    price = "N/A"
                
                try:
                    color_name = item['choices'][0]['title']
                except (KeyError, IndexError, TypeError):
                    color_name = item.get('title', 'Unknown')
                
                # --- EKSTRAKSI IMAGE URL BARU ---
                image_url = "N/A"
                try:
                    # Ambil URL 'original' dari gambar pertama di array 'images'
                    image_url = item['images'][0]['original']
                except (KeyError, IndexError, TypeError):
                    pass # Biarkan N/A jika tidak ditemukan
                # --------------------------------

                subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
                subscription_info = ""
                if subscription_contract:
                    initial_price = subscription_contract['initialPrice']['price']['displayValue']
                    freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
                    subscription_info = f" (Subs: {initial_price}/{freq})"

                print(f"{sku:<10} | {in_stock:<10} | {price:<8} | {color_name + subscription_info:<40} | {image_url}")
        else:
            pass 


        # 9. Menampilkan Hasil Ingredients
        if ingredients_content:
            print("\n" + "="*120)
            print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
            print("="*120)
            print(ingredients_content)
            print("\n" + "="*120)
        else:
            print("\n[INFO] Key 'ingredients' tidak ditemukan.")
        
        # 10. Menampilkan Ulasan (Review)
        if review_list:
            print("\n" + "="*120)
            print("## ⭐ Ulasan Terbaru (Reviews)")
            print("="*120)
            for i, review in enumerate(review_list):
                print(f"--- Review {i+1} ({review['date']}) ---")
                print(f"Rating: {review['rating']}/5 by {review['author']}")
                print(f"Ulasan: {review['body']}")
            print("\n" + "="*120)
        else:
            print("\n[INFO] Data ulasan (review) tidak ditemukan.")


    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# --- Eksekusi Script ---
print("--- UJI KASUS 1: RevitaLash ---")
target_url_1 = "https://www.dermstore.com/p/revitalash-revitabrow-advanced-eyebrow-conditioner-3ml-4-month-supply/15724058/"
scrape_dermstore_data(target_url_1)

print("\n" + "#" * 120 + "\n")

print("--- UJI KASUS 2: Wander Beauty ---")
target_url_2 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
scrape_dermstore_data(target_url_2)


