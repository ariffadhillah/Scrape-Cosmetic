# # # # # # import requests
# # # # # # import json
# # # # # # import re
# # # # # # from bs4 import BeautifulSoup
# # # # # # import sys 
# # # # # # from typing import Optional, Dict, List, Tuple, Any

# # # # # # sys.setrecursionlimit(3000)

# # # # # # # ==============================================================================
# # # # # # # I. FUNGSI HELPER (Ekstraksi dari HTML/JSON-LD)
# # # # # # # (Tidak berubah, tetapi disertakan untuk menjalankan skrip)
# # # # # # # ==============================================================================

# # # # # # def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # # # #     """Fallback: Mencari Product Overview dari tab HTML."""
# # # # # #     target_div = soup.find('div', {'id': 'product-description-0'})
# # # # # #     if not target_div:
# # # # # #         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
# # # # # #     if target_div:
# # # # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # # # #         return clean_text
# # # # # #     return None

# # # # # # def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # # # #     """Fallback: Mencari Ingredients dari tab HTML."""
# # # # # #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
# # # # # #     if target_div:
# # # # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # # # #         return clean_text
# # # # # #     return None

# # # # # # def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # # # #     """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
# # # # # #     breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
# # # # # #     if breadcrumb:
# # # # # #         brand_link = breadcrumb.find_all('li')
# # # # # #         if len(brand_link) > 1:
# # # # # #             brand_name = brand_link[-2].get_text(strip=True)
# # # # # #             if brand_name and brand_name.lower() != 'all brands':
# # # # # #                 return brand_name
# # # # # #     brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
# # # # # #     if brand_link:
# # # # # #         return brand_link.get_text(strip=True)
# # # # # #     return None

# # # # # # def extract_product_data_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
# # # # # #     """Mengekstrak data dasar produk dari JSON-LD schema markup."""
# # # # # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
# # # # # #     for script in json_ld_scripts:
# # # # # #         if script.string:
# # # # # #             try:
# # # # # #                 data = json.loads(script.string)
# # # # # #                 if isinstance(data, list):
# # # # # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
# # # # # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # # # # #                     product_data = {
# # # # # #                         'name': data.get('name'),
# # # # # #                         'sku': data.get('sku'),
# # # # # #                         'description': data.get('description'),
# # # # # #                         'image': data.get('image'),
# # # # # #                         'brand': data.get('brand', {}).get('name'),
# # # # # #                         'offer': data.get('offers')[0] if data.get('offers') else None
# # # # # #                     }
# # # # # #                     return product_data
            
# # # # # #             except json.JSONDecodeError:
# # # # # #                 continue
# # # # # #             except (TypeError, IndexError):
# # # # # #                 continue
                
# # # # # #     return None

# # # # # # def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
# # # # # #     """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
# # # # # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
# # # # # #     rating_data = None
# # # # # #     review_list = []
    
# # # # # #     for script in json_ld_scripts:
# # # # # #         if script.string:
# # # # # #             try:
# # # # # #                 data = json.loads(script.string)
# # # # # #                 if isinstance(data, list):
# # # # # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
# # # # # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # # # # #                     aggregate_rating = data.get("aggregateRating")
# # # # # #                     if aggregate_rating:
# # # # # #                         rating_data = {
# # # # # #                             'value': aggregate_rating.get('ratingValue'), 
# # # # # #                             'count': aggregate_rating.get('reviewCount')
# # # # # #                         }
# # # # # #                     reviews = data.get("review")
# # # # # #                     if reviews:
# # # # # #                         for review in reviews[:3]: 
# # # # # #                             review_list.append({
# # # # # #                                 'rating': review['reviewRating'].get('ratingValue', 'N/A'),
# # # # # #                                 'author': review['author'].get('name', 'Anonymous'),
# # # # # #                                 'body': review.get('reviewBody', 'No body text'),
# # # # # #                                 'date': review.get('datePublished', 'N/A')
# # # # # #                             })
# # # # # #                     if rating_data or review_list:
# # # # # #                         return rating_data, review_list
            
# # # # # #             except json.JSONDecodeError:
# # # # # #                 continue
                
# # # # # #     return rating_data, review_list

# # # # # # # ==============================================================================
# # # # # # # II. FUNGSI UTAMA SCRAPER (Logika Ekstraksi Data)
# # # # # # # ==============================================================================

# # # # # # def scrape_dermstore_data(url: str):
# # # # # #     """Mengambil semua data produk dan menampilkannya dalam format ringkas."""
# # # # # #     headers = {
# # # # # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# # # # # #         "Accept-Language": "en-US,en;q=0.9",
# # # # # #         "Referer": "https://www.google.com/"
# # # # # #     }

# # # # # #     print(f"Sedang mengambil data dari: **{url}** ...")
    
# # # # # #     try:
# # # # # #         response = requests.get(url, headers=headers, timeout=15)
        
# # # # # #         if response.status_code != 200:
# # # # # #             print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
# # # # # #             return

# # # # # #         soup = BeautifulSoup(response.text, 'html.parser')
# # # # # #         scripts = soup.find_all('script')
        
# # # # # #         # Inisialisasi variabel data
# # # # # #         variation_data = None
# # # # # #         ingredients_content = None
# # # # # #         brand_name = None 
# # # # # #         overview_content = None
# # # # # #         json_ld_product_data = None
        
# # # # # #         rating_data, review_list = extract_rating_and_reviews(soup)
        
# # # # # #         # 1. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
# # # # # #         for script in scripts:
# # # # # #             if script.string and "const variationData =" in script.string:
# # # # # #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# # # # # #                 if match:
# # # # # #                     try:
# # # # # #                         variation_data = json.loads(match.group(1))
# # # # # #                         break
# # # # # #                     except json.JSONDecodeError:
# # # # # #                         pass
        
# # # # # #         # 2. Ekstraksi Konten dari Data Variasi (Jika Ditemukan)
# # # # # #         if variation_data:
# # # # # #             print("[INFO] Data variasi ditemukan dari 'variationData' (JS).")
# # # # # #             first_variation = variation_data[0] 
# # # # # #             content_list = first_variation.get('content', [])

# # # # # #             for content_item in content_list:
# # # # # #                 if content_item.get('key') == 'synopsis' and not overview_content:
# # # # # #                     try:
# # # # # #                         content_list_value = content_item['value']['richContentListValue'][0]['content']
# # # # # #                         for html_block in content_list_value:
# # # # # #                             if html_block['type'] == 'HTML':
# # # # # #                                 soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
# # # # # #                                 overview_content = soup_overview.get_text(separator="\n", strip=True)
# # # # # #                                 break
# # # # # #                     except (KeyError, TypeError, IndexError):
# # # # # #                         pass

# # # # # #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# # # # # #                     try:
# # # # # #                         content_html_list = content_item['value']['richContentValue']['content']
# # # # # #                         for html_block in content_html_list:
# # # # # #                             if html_block['type'] == 'HTML':
# # # # # #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# # # # # #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
# # # # # #                                 break
# # # # # #                     except (KeyError, TypeError):
# # # # # #                         pass
                        
# # # # # #                 if content_item.get('key') == 'brand' and not brand_name:
# # # # # #                     try:
# # # # # #                         brand_list = content_item['value']['stringListValue']
# # # # # #                         if brand_list:
# # # # # #                             brand_name = brand_list[0]
# # # # # #                     except (KeyError, TypeError):
# # # # # #                         pass
        
# # # # # #         # 3. FALLBACK: Ekstraksi Data dari JSON-LD (Jika variation_data TIDAK Ditemukan)
# # # # # #         if not variation_data:
# # # # # #             print("[INFO] 'variationData' tidak ditemukan. Mencoba mengekstrak dari JSON-LD.")
# # # # # #             json_ld_product_data = extract_product_data_from_json_ld(soup)
            
# # # # # #             if json_ld_product_data:
# # # # # #                 # Ganti variabel utama dengan data dari JSON-LD jika kosong
# # # # # #                 if not overview_content and json_ld_product_data.get('description'):
# # # # # #                     overview_content = json_ld_product_data['description']
                
# # # # # #                 if not brand_name and json_ld_product_data.get('brand'):
# # # # # #                     brand_name = json_ld_product_data['brand']
                
# # # # # #                 # Buat struktur 'variation_data' tiruan dari 'offer' untuk output yang konsisten
# # # # # #                 if json_ld_product_data.get('offer'):
# # # # # #                     offer = json_ld_product_data['offer']
# # # # # #                     is_in_stock = "InStock" in offer.get('availability', '')
                    
# # # # # #                     simulated_variation = [{
# # # # # #                         'sku': offer.get('sku', json_ld_product_data.get('sku', 'N/A')),
# # # # # #                         'title': json_ld_product_data.get('title', 'N/A'),
# # # # # #                         'inStock': is_in_stock,
# # # # # #                         'price': {'price': {'displayValue': f"{offer.get('price', 'N/A')} {offer.get('priceCurrency', '')}"}},
# # # # # #                         'images': [{'original': json_ld_product_data.get('image')}] if json_ld_product_data.get('image') else []
# # # # # #                     }]
# # # # # #                     variation_data = simulated_variation
# # # # # #             else:
# # # # # #                 print("[INFO] Data produk dari JSON-LD tidak ditemukan.")

# # # # # #         # 4. Fallback HTML (untuk overview, ingredients, brand)
# # # # # #         if not overview_content:
# # # # # #             overview_content = extract_product_overview_from_html(soup)
        
# # # # # #         if not ingredients_content:
# # # # # #             ingredients_content = extract_ingredients_from_html(soup)

# # # # # #         if not brand_name:
# # # # # #             brand_name = extract_brand_from_html(soup)

# # # # # #         # Ambil nama produk dari H1 HTML jika tidak ada dari JSON-LD
# # # # # #         product_name = (
# # # # # #             json_ld_product_data.get('name') if json_ld_product_data and json_ld_product_data.get('name') else
# # # # # #             soup.find('h1', class_=lambda c: c and 'product-title' in c).get_text(strip=True) if soup.find('h1', class_=lambda c: c and 'product-title' in c) else
# # # # # #             'NAMA PRODUK TIDAK DITEMUKAN'
# # # # # #         )

# # # # # #         # ======================================================================
# # # # # #         # III. OUTPUT HASIL EKSTRAKSI (Format Ringkas Baru)
# # # # # #         # ======================================================================

# # # # # #         print("\n" + "="*80)
# # # # # #         print("## ✅ Hasil Ekstraksi Data Produk (Ringkas)")
# # # # # #         print("="*80)

# # # # # #         # 1. Data Utama
# # # # # #         print(f"{'Nama Produk':<18} = {product_name}")
# # # # # #         print(f"{'Brand':<18} = {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
# # # # # #         if rating_data:
# # # # # #             rating_str = f"{rating_data['value']} ({rating_data['count']} reviews)"
# # # # # #             print(f"{'Rating':<18} = {rating_str}")
# # # # # #         else:
# # # # # #             print(f"{'Rating':<18} = TIDAK DITEMUKAN")
        
# # # # # #         # 2. Product Overview (dibatasi 500 karakter)
# # # # # #         overview_print = overview_content[:500].replace('\n', ' ') + '...' if overview_content and len(overview_content) > 500 else (overview_content.replace('\n', ' ') if overview_content else 'TIDAK DITEMUKAN')
# # # # # #         print(f"{'Product Overview':<18} = {overview_print}")
        
# # # # # #         print("\n--- Variasi Produk ---")

# # # # # #         # 3. Variasi Produk (SKU, Harga, Varian, Gambar)
# # # # # #         if variation_data:
            
# # # # # #             # Asumsi: Jika ada variasi, ambil SKU dan Harga dari variasi pertama (atau dari JSON-LD offer)
# # # # # #             first_item = variation_data[0]
# # # # # #             sku = first_item.get('sku', 'N/A')
# # # # # #             try:
# # # # # #                 price = first_item['price']['price']['displayValue']
# # # # # #             except (KeyError, TypeError):
# # # # # #                 price = "N/A"
            
# # # # # #             print(f"{'SKU':<18} = {sku}")
# # # # # #             print(f"{'Harga':<18} = {price}")

# # # # # #             for i, item in enumerate(variation_data):
# # # # # #                 # Ambil nama/varian
# # # # # #                 color_name = 'N/A'
# # # # # #                 try:
# # # # # #                     color_name = item['choices'][0]['title']
# # # # # #                 except (KeyError, IndexError, TypeError):
# # # # # #                     color_name = item.get('title', product_name)
                    
# # # # # #                 # Ekstraksi Image URL
# # # # # #                 image_url = "N/A"
# # # # # #                 try:
# # # # # #                     image_url = item['images'][0]['original']
# # # # # #                 except (KeyError, IndexError, TypeError):
# # # # # #                     # Fallback ke image JSON-LD jika ini single SKU
# # # # # #                     if json_ld_product_data and json_ld_product_data.get('image'):
# # # # # #                         image_url = json_ld_product_data['image']
                        
# # # # # #                 # Cetak Varian dan Image URL
# # # # # #                 print(f"{f'Warna / Varian {i+1}':<18} = {color_name}")
# # # # # #                 print(f"{f'Image url varian {i+1}':<18} = {image_url}")
# # # # # #         else:
# # # # # #             print("Data Variasi Produk tidak ditemukan (SKU/Harga/Varian/Gambar).")

# # # # # #         # 4. Ingredients
# # # # # #         print("\n--- Komposisi ---")
# # # # # #         ingredients_print = ingredients_content[:500].replace('\n', ' ') + '...' if ingredients_content and len(ingredients_content) > 500 else (ingredients_content.replace('\n', ' ') if ingredients_content else 'TIDAK DITEMUKAN')
# # # # # #         print(f"{'Ingredients':<18} = {ingredients_print}")

# # # # # #         print("="*80 + "\n")

# # # # # #     except Exception as e:
# # # # # #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # # # # # ==============================================================================
# # # # # # # IV. EKSEKUSI UJI KASUS
# # # # # # # ==============================================================================
# # # # # # if __name__ == "__main__":
    
# # # # # #     print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK " + "=" * 50)
    
# # # # # #     # UJI KASUS 1: Multiple Variations (variationData ada)
# # # # # #     print("\n" + "#" * 120 + "\n")
# # # # # #     print("--- UJI KASUS 1: Wander Beauty (Multiple Variations - variationData) ---")
# # # # # #     target_url_1 = "https://www.dermstore.com/p/alchimie-forever-protective-day-cream-spf23/11286078/"
# # # # # #     scrape_dermstore_data(target_url_1)

# # # # # #     print("\n" + "#" * 120 + "\n")

# # # # # #     # UJI KASUS 2: Single SKU (variationData tidak ada, menggunakan JSON-LD)
# # # # # #     print("--- UJI KASUS 2: Alchimie Forever (Single SKU - JSON-LD) ---")
# # # # # #     target_url_2 = "https://www.dermstore.com/p/grande-cosmetics-grandelips-hydrating-lip-plumper-gloss-2.4ml-various-shades/13187848/"
# # # # # #     scrape_dermstore_data(target_url_2)

# # # # # #     print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)



# # # # # import requests
# # # # # import json
# # # # # import re
# # # # # from bs4 import BeautifulSoup
# # # # # import sys 
# # # # # from typing import Optional, Dict, List, Tuple, Any

# # # # # sys.setrecursionlimit(3000)

# # # # # # ==============================================================================
# # # # # # I. FUNGSI HELPER (Ekstraksi dari HTML/JSON-LD) - (Tidak Berubah)
# # # # # # ==============================================================================

# # # # # def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # # #     """Fallback: Mencari Product Overview dari tab HTML."""
# # # # #     target_div = soup.find('div', {'id': 'product-description-0'})
# # # # #     if not target_div:
# # # # #         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
# # # # #     if target_div:
# # # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # # #         return clean_text
# # # # #     return None

# # # # # def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # # #     """Fallback: Mencari Ingredients dari tab HTML."""
# # # # #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
# # # # #     if target_div:
# # # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # # #         return clean_text
# # # # #     return None

# # # # # def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # # #     """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
# # # # #     breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
# # # # #     if breadcrumb:
# # # # #         brand_link = breadcrumb.find_all('li')
# # # # #         if len(brand_link) > 1:
# # # # #             brand_name = brand_link[-2].get_text(strip=True)
# # # # #             if brand_name and brand_name.lower() != 'all brands':
# # # # #                 return brand_name
# # # # #     brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
# # # # #     if brand_link:
# # # # #         return brand_link.get_text(strip=True)
# # # # #     return None

# # # # # def extract_product_data_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
# # # # #     """Mengekstrak data dasar produk dari JSON-LD schema markup."""
# # # # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
# # # # #     for script in json_ld_scripts:
# # # # #         if script.string:
# # # # #             try:
# # # # #                 data = json.loads(script.string)
# # # # #                 if isinstance(data, list):
# # # # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
# # # # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # # # #                     product_data = {
# # # # #                         'name': data.get('name'),
# # # # #                         'sku': data.get('sku'),
# # # # #                         'description': data.get('description'),
# # # # #                         'image': data.get('image'),
# # # # #                         'brand': data.get('brand', {}).get('name'),
# # # # #                         'offer': data.get('offers')[0] if data.get('offers') else None
# # # # #                     }
# # # # #                     return product_data
            
# # # # #             except json.JSONDecodeError:
# # # # #                 continue
# # # # #             except (TypeError, IndexError):
# # # # #                 continue
                
# # # # #     return None

# # # # # def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
# # # # #     """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
# # # # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
# # # # #     rating_data = None
# # # # #     review_list = []
    
# # # # #     for script in json_ld_scripts:
# # # # #         if script.string:
# # # # #             try:
# # # # #                 data = json.loads(script.string)
# # # # #                 if isinstance(data, list):
# # # # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
# # # # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # # # #                     aggregate_rating = data.get("aggregateRating")
# # # # #                     if aggregate_rating:
# # # # #                         rating_data = {
# # # # #                             'value': aggregate_rating.get('ratingValue'), 
# # # # #                             'count': aggregate_rating.get('reviewCount')
# # # # #                         }
# # # # #                     reviews = data.get("review")
# # # # #                     if reviews:
# # # # #                         for review in reviews[:3]: 
# # # # #                             review_list.append({
# # # # #                                 'rating': review['reviewRating'].get('ratingValue', 'N/A'),
# # # # #                                 'author': review['author'].get('name', 'Anonymous'),
# # # # #                                 'body': review.get('reviewBody', 'No body text'),
# # # # #                                 'date': review.get('datePublished', 'N/A')
# # # # #                             })
# # # # #                     if rating_data or review_list:
# # # # #                         return rating_data, review_list
            
# # # # #             except json.JSONDecodeError:
# # # # #                 continue
                
# # # # #     return rating_data, review_list

# # # # # # ==============================================================================
# # # # # # II. FUNGSI UTAMA SCRAPER (Logika Ekstraksi Data)
# # # # # # ==============================================================================

# # # # # def scrape_dermstore_data(url: str):
# # # # #     """Mengambil semua data produk dan menampilkannya dalam format ringkas."""
# # # # #     headers = {
# # # # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# # # # #         "Accept-Language": "en-US,en;q=0.9",
# # # # #         "Referer": "https://www.google.com/"
# # # # #     }

# # # # #     print(f"Sedang mengambil data dari: **{url}** ...")
    
# # # # #     try:
# # # # #         response = requests.get(url, headers=headers, timeout=15)
        
# # # # #         if response.status_code != 200:
# # # # #             print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
# # # # #             return

# # # # #         soup = BeautifulSoup(response.text, 'html.parser')
# # # # #         scripts = soup.find_all('script')
        
# # # # #         # Inisialisasi variabel data
# # # # #         variation_data = None
# # # # #         ingredients_content = None
# # # # #         brand_name = None 
# # # # #         overview_content = None
# # # # #         json_ld_product_data = None
        
# # # # #         rating_data, review_list = extract_rating_and_reviews(soup)
        
# # # # #         # --- LANGKAH REVISI: Ekstraksi Nama Produk Awal ---
# # # # #         product_name = 'NAMA PRODUK TIDAK DITEMUKAN'
        
# # # # #         # 1. Coba dari H1 (Tag Judul Produk Utama)
# # # # #         h1_tag = soup.find('h1', class_=lambda c: c and 'product-title' in c)
# # # # #         if h1_tag:
# # # # #             product_name = h1_tag.get_text(strip=True)
        
# # # # #         # 2. Fallback ke HTML <title> jika H1 gagal
# # # # #         if product_name == 'NAMA PRODUK TIDAK DITEMUKAN':
# # # # #             title_tag = soup.find('title')
# # # # #             if title_tag:
# # # # #                 full_title = title_tag.get_text(strip=True)
# # # # #                 # Coba ambil bagian pertama dari judul yang dipisahkan oleh '-' atau '|'
# # # # #                 if '-' in full_title:
# # # # #                     product_name = full_title.split('-')[0].strip()
# # # # #                 elif '|' in full_title:
# # # # #                     product_name = full_title.split('|')[0].strip()
# # # # #                 else:
# # # # #                     product_name = full_title
                
# # # # #                 if not product_name:
# # # # #                     product_name = full_title
# # # # #         # -----------------------------------------------------

        
# # # # #         # 1. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
# # # # #         for script in scripts:
# # # # #             if script.string and "const variationData =" in script.string:
# # # # #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# # # # #                 if match:
# # # # #                     try:
# # # # #                         variation_data = json.loads(match.group(1))
# # # # #                         break
# # # # #                     except json.JSONDecodeError:
# # # # #                         pass
        
# # # # #         # 2. Ekstraksi Konten dari Data Variasi (Jika Ditemukan)
# # # # #         if variation_data:
# # # # #             print("[INFO] Data variasi ditemukan dari 'variationData' (JS).")
# # # # #             first_variation = variation_data[0] 
# # # # #             content_list = first_variation.get('content', [])

# # # # #             for content_item in content_list:
# # # # #                 if content_item.get('key') == 'synopsis' and not overview_content:
# # # # #                     try:
# # # # #                         content_list_value = content_item['value']['richContentListValue'][0]['content']
# # # # #                         for html_block in content_list_value:
# # # # #                             if html_block['type'] == 'HTML':
# # # # #                                 soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
# # # # #                                 overview_content = soup_overview.get_text(separator="\n", strip=True)
# # # # #                                 break
# # # # #                     except (KeyError, TypeError, IndexError):
# # # # #                         pass

# # # # #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# # # # #                     try:
# # # # #                         content_html_list = content_item['value']['richContentValue']['content']
# # # # #                         for html_block in content_html_list:
# # # # #                             if html_block['type'] == 'HTML':
# # # # #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# # # # #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
# # # # #                                 break
# # # # #                     except (KeyError, TypeError):
# # # # #                         pass
                        
# # # # #                 if content_item.get('key') == 'brand' and not brand_name:
# # # # #                     try:
# # # # #                         brand_list = content_item['value']['stringListValue']
# # # # #                         if brand_list:
# # # # #                             brand_name = brand_list[0]
# # # # #                     except (KeyError, TypeError):
# # # # #                         pass
        
# # # # #         # 3. FALLBACK: Ekstraksi Data dari JSON-LD (Jika variation_data TIDAK Ditemukan)
# # # # #         if not variation_data:
# # # # #             print("[INFO] 'variationData' tidak ditemukan. Mencoba mengekstrak dari JSON-LD.")
# # # # #             json_ld_product_data = extract_product_data_from_json_ld(soup)
            
# # # # #             if json_ld_product_data:
# # # # #                 # Ganti variabel utama dengan data dari JSON-LD jika kosong
# # # # #                 if not overview_content and json_ld_product_data.get('description'):
# # # # #                     overview_content = json_ld_product_data['description']
                
# # # # #                 if not brand_name and json_ld_product_data.get('brand'):
# # # # #                     brand_name = json_ld_product_data['brand']
                
# # # # #                 # Update Nama Produk jika ditemukan di JSON-LD dan sebelumnya belum ditemukan
# # # # #                 if product_name == 'NAMA PRODUK TIDAK DITEMUKAN' and json_ld_product_data.get('name'):
# # # # #                     product_name = json_ld_product_data['name']
                
# # # # #                 # Buat struktur 'variation_data' tiruan dari 'offer' untuk output yang konsisten
# # # # #                 if json_ld_product_data.get('offer'):
# # # # #                     offer = json_ld_product_data['offer']
# # # # #                     is_in_stock = "InStock" in offer.get('availability', '')
                    
# # # # #                     simulated_variation = [{
# # # # #                         'sku': offer.get('sku', json_ld_product_data.get('sku', 'N/A')),
# # # # #                         'title': json_ld_product_data.get('name', 'N/A'),
# # # # #                         'inStock': is_in_stock,
# # # # #                         'price': {'price': {'displayValue': f"{offer.get('price', 'N/A')} {offer.get('priceCurrency', '')}"}},
# # # # #                         'images': [{'original': json_ld_product_data.get('image')}] if json_ld_product_data.get('image') else []
# # # # #                     }]
# # # # #                     variation_data = simulated_variation
# # # # #             else:
# # # # #                 print("[INFO] Data produk dari JSON-LD tidak ditemukan.")

# # # # #         # 4. Fallback HTML (untuk overview, ingredients, brand)
# # # # #         if not overview_content:
# # # # #             overview_content = extract_product_overview_from_html(soup)
        
# # # # #         if not ingredients_content:
# # # # #             ingredients_content = extract_ingredients_from_html(soup)

# # # # #         if not brand_name:
# # # # #             brand_name = extract_brand_from_html(soup)

# # # # #         # ======================================================================
# # # # #         # III. OUTPUT HASIL EKSTRAKSI (Format Ringkas Baru)
# # # # #         # ======================================================================

# # # # #         print("\n" + "="*80)
# # # # #         print("## ✅ Hasil Ekstraksi Data Produk (Ringkas)")
# # # # #         print("="*80)

# # # # #         # 1. Data Utama
# # # # #         print(f"{'Nama Produk':<18} = {product_name}") # Gunakan product_name yang sudah diisi
# # # # #         print(f"{'Brand':<18} = {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
# # # # #         if rating_data:
# # # # #             rating_str = f"{rating_data['value']} ({rating_data['count']} reviews)"
# # # # #             print(f"{'Rating':<18} = {rating_str}")
# # # # #         else:
# # # # #             print(f"{'Rating':<18} = TIDAK DITEMUKAN")
        
# # # # #         # 2. Product Overview (dibatasi 500 karakter)
# # # # #         overview_print = overview_content[:500].replace('\n', ' ') + '...' if overview_content and len(overview_content) > 500 else (overview_content.replace('\n', ' ') if overview_content else 'TIDAK DITEMUKAN')
# # # # #         print(f"{'Product Overview':<18} = {overview_print}")
        
# # # # #         print("\n--- Variasi Produk ---")

# # # # #         # 3. Variasi Produk (SKU, Harga, Varian, Gambar)
# # # # #         if variation_data:
            
# # # # #             # Asumsi: Jika ada variasi, ambil SKU dan Harga dari variasi pertama (atau dari JSON-LD offer)
# # # # #             first_item = variation_data[0]
# # # # #             sku = first_item.get('sku', 'N/A')
# # # # #             try:
# # # # #                 price = first_item['price']['price']['displayValue']
# # # # #             except (KeyError, TypeError):
# # # # #                 price = "N/A"
            
# # # # #             print(f"{'SKU':<18} = {sku}")
# # # # #             print(f"{'Harga':<18} = {price}")

# # # # #             for i, item in enumerate(variation_data):
# # # # #                 # Ambil nama/varian
# # # # #                 color_name = 'N/A'
# # # # #                 try:
# # # # #                     color_name = item['choices'][0]['title']
# # # # #                 except (KeyError, IndexError, TypeError):
# # # # #                     # Jika choices gagal, gunakan title dari item variasi (biasanya nama produk + varian)
# # # # #                     color_name = item.get('title', 'Varian Tidak Dikenal')
                    
# # # # #                     # Coba hapus nama produk utama dari title varian jika terlalu panjang
# # # # #                     if color_name != 'Varian Tidak Dikenal' and product_name != 'NAMA PRODUK TIDAK DITEMUKAN':
# # # # #                         color_name = color_name.replace(product_name, '').strip()
# # # # #                         if not color_name:
# # # # #                             color_name = 'Varian Utama'
                        
# # # # #                 # Ekstraksi Image URL
# # # # #                 image_url = "N/A"
# # # # #                 try:
# # # # #                     image_url = item['images'][0]['original']
# # # # #                 except (KeyError, IndexError, TypeError):
# # # # #                     if json_ld_product_data and json_ld_product_data.get('image'):
# # # # #                         image_url = json_ld_product_data['image']
                        
# # # # #                 # Cetak Varian dan Image URL
# # # # #                 print(f"{f'Warna / Varian {i+1}':<18} = {color_name}")
# # # # #                 print(f"{f'Image url varian {i+1}':<18} = {image_url}")
# # # # #         else:
# # # # #             print("Data Variasi Produk tidak ditemukan (SKU/Harga/Varian/Gambar).")

# # # # #         # 4. Ingredients
# # # # #         print("\n--- Komposisi ---")
# # # # #         ingredients_print = ingredients_content[:500].replace('\n', ' ') + '...' if ingredients_content and len(ingredients_content) > 500 else (ingredients_content.replace('\n', ' ') if ingredients_content else 'TIDAK DITEMUKAN')
# # # # #         print(f"{'Ingredients':<18} = {ingredients_print}")

# # # # #         print("="*80 + "\n")

# # # # #     except Exception as e:
# # # # #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # # # # ==============================================================================
# # # # # # IV. EKSEKUSI UJI KASUS (Tetap Sama)
# # # # # # ==============================================================================
# # # # # if __name__ == "__main__":
    
# # # # #     print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK " + "=" * 50)
    
# # # # #     # UJI KASUS 1: Multiple Variations (variationData ada)
# # # # #     print("\n" + "#" * 120 + "\n")
# # # # #     print("--- UJI KASUS 1: Wander Beauty (Multiple Variations - variationData) ---")
# # # # #     target_url_1 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# # # # #     scrape_dermstore_data(target_url_1)

# # # # #     print("\n" + "#" * 120 + "\n")

# # # # #     # UJI KASUS 2: Single SKU (variationData tidak ada, menggunakan JSON-LD)
# # # # #     print("--- UJI KASUS 2: Alchimie Forever (Single SKU - JSON-LD) ---")
# # # # #     target_url_2 = "https://www.dermstore.com/p/alchimie-forever-protective-day-cream-spf23/11286078/"
# # # # #     scrape_dermstore_data(target_url_2)

# # # # #     print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)



# # # # import requests
# # # # import json
# # # # import re
# # # # from bs4 import BeautifulSoup
# # # # import sys 
# # # # from typing import Optional, Dict, List, Tuple, Any

# # # # sys.setrecursionlimit(3000)

# # # # # ==============================================================================
# # # # # I. FUNGSI HELPER (Ekstraksi dari HTML/JSON-LD) - (Tetap Sama)
# # # # # ==============================================================================

# # # # def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # #     """Fallback: Mencari Product Overview dari tab HTML."""
# # # #     target_div = soup.find('div', {'id': 'product-description-0'})
# # # #     if not target_div:
# # # #         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
# # # #     if target_div:
# # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # #         return clean_text
# # # #     return None

# # # # def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # #     """Fallback: Mencari Ingredients dari tab HTML."""
# # # #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
# # # #     if target_div:
# # # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # # #         return clean_text
# # # #     return None

# # # # def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
# # # #     """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
# # # #     breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
# # # #     if breadcrumb:
# # # #         brand_link = breadcrumb.find_all('li')
# # # #         if len(brand_link) > 1:
# # # #             brand_name = brand_link[-2].get_text(strip=True)
# # # #             if brand_name and brand_name.lower() != 'all brands':
# # # #                 return brand_name
# # # #     brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
# # # #     if brand_link:
# # # #         return brand_link.get_text(strip=True)
# # # #     return None

# # # # def extract_product_data_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
# # # #     """Mengekstrak data dasar produk dari JSON-LD schema markup."""
# # # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
# # # #     for script in json_ld_scripts:
# # # #         if script.string:
# # # #             try:
# # # #                 data = json.loads(script.string)
# # # #                 if isinstance(data, list):
# # # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
# # # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # # #                     product_data = {
# # # #                         'name': data.get('name'),
# # # #                         'sku': data.get('sku'),
# # # #                         'description': data.get('description'),
# # # #                         'image': data.get('image'),
# # # #                         'brand': data.get('brand', {}).get('name'),
# # # #                         'offer': data.get('offers')[0] if data.get('offers') else None
# # # #                     }
# # # #                     return product_data
            
# # # #             except json.JSONDecodeError:
# # # #                 continue
# # # #             except (TypeError, IndexError):
# # # #                 continue
                
# # # #     return None

# # # # def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
# # # #     """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
# # # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
# # # #     rating_data = None
# # # #     review_list = []
    
# # # #     for script in json_ld_scripts:
# # # #         if script.string:
# # # #             try:
# # # #                 data = json.loads(script.string)
# # # #                 if isinstance(data, list):
# # # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
# # # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # # #                     aggregate_rating = data.get("aggregateRating")
# # # #                     if aggregate_rating:
# # # #                         rating_data = {
# # # #                             'value': aggregate_rating.get('ratingValue'), 
# # # #                             'count': aggregate_rating.get('reviewCount')
# # # #                         }
# # # #                     reviews = data.get("review")
# # # #                     if reviews:
# # # #                         for review in reviews[:3]: 
# # # #                             review_list.append({
# # # #                                 'rating': review['reviewRating'].get('ratingValue', 'N/A'),
# # # #                                 'author': review['author'].get('name', 'Anonymous'),
# # # #                                 'body': review.get('reviewBody', 'No body text'),
# # # #                                 'date': review.get('datePublished', 'N/A')
# # # #                             })
# # # #                     if rating_data or review_list:
# # # #                         return rating_data, review_list
            
# # # #             except json.JSONDecodeError:
# # # #                 continue
                
# # # #     return rating_data, review_list

# # # # # ==============================================================================
# # # # # II. FUNGSI UTAMA SCRAPER
# # # # # ==============================================================================

# # # # def scrape_dermstore_data(url: str):
# # # #     """Mengambil semua data produk dan memprosesnya menjadi daftar varian/SKU."""
# # # #     headers = {
# # # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# # # #         "Accept-Language": "en-US,en;q=0.9",
# # # #         "Referer": "https://www.google.com/"
# # # #     }

# # # #     print(f"Sedang mengambil data dari: **{url}** ...")
    
# # # #     try:
# # # #         response = requests.get(url, headers=headers, timeout=15)
        
# # # #         if response.status_code != 200:
# # # #             print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
# # # #             return

# # # #         soup = BeautifulSoup(response.text, 'html.parser')
# # # #         scripts = soup.find_all('script')
        
# # # #         # Inisialisasi variabel data
# # # #         variation_data = None
# # # #         ingredients_content = None
# # # #         brand_name = None 
# # # #         overview_content = None
# # # #         json_ld_product_data = None
        
# # # #         rating_data, review_list = extract_rating_and_reviews(soup)
        
# # # #         # --- Ekstraksi Nama Produk Induk (Parent Name) ---
# # # #         product_name = 'NAMA PRODUK TIDAK DITEMUKAN'
        
# # # #         # 1. Coba dari H1 (Tag Judul Produk Utama)
# # # #         h1_tag = soup.find('h1', class_=lambda c: c and 'product-title' in c)
# # # #         if h1_tag:
# # # #             product_name = h1_tag.get_text(strip=True)
        
# # # #         # 2. Fallback ke HTML <title> jika H1 gagal
# # # #         if product_name == 'NAMA PRODUK TIDAK DITEMUKAN':
# # # #             title_tag = soup.find('title')
# # # #             if title_tag:
# # # #                 full_title = title_tag.get_text(strip=True)
# # # #                 if '-' in full_title:
# # # #                     product_name = full_title.split('-')[0].strip()
# # # #                 elif '|' in full_title:
# # # #                     product_name = full_title.split('|')[0].strip()
# # # #                 else:
# # # #                     product_name = full_title
                
# # # #                 if not product_name:
# # # #                     product_name = full_title
# # # #         # -----------------------------------------------------

        
# # # #         # 1. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
# # # #         for script in scripts:
# # # #             if script.string and "const variationData =" in script.string:
# # # #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# # # #                 if match:
# # # #                     try:
# # # #                         variation_data = json.loads(match.group(1))
# # # #                         break
# # # #                     except json.JSONDecodeError:
# # # #                         pass
        
# # # #         # 2. Ekstraksi Konten Utama dari Data Variasi
# # # #         if variation_data:
# # # #             print("[INFO] Data variasi ditemukan dari 'variationData' (JS).")
# # # #             first_variation = variation_data[0] 
# # # #             content_list = first_variation.get('content', [])

# # # #             for content_item in content_list:
# # # #                 if content_item.get('key') == 'synopsis' and not overview_content:
# # # #                     try:
# # # #                         content_list_value = content_item['value']['richContentListValue'][0]['content']
# # # #                         for html_block in content_list_value:
# # # #                             if html_block['type'] == 'HTML':
# # # #                                 soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
# # # #                                 overview_content = soup_overview.get_text(separator="\n", strip=True)
# # # #                                 break
# # # #                     except (KeyError, TypeError, IndexError):
# # # #                         pass

# # # #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# # # #                     try:
# # # #                         content_html_list = content_item['value']['richContentValue']['content']
# # # #                         for html_block in content_html_list:
# # # #                             if html_block['type'] == 'HTML':
# # # #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# # # #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
# # # #                                 break
# # # #                     except (KeyError, TypeError):
# # # #                         pass
                        
# # # #                 if content_item.get('key') == 'brand' and not brand_name:
# # # #                     try:
# # # #                         brand_list = content_item['value']['stringListValue']
# # # #                         if brand_list:
# # # #                             brand_name = brand_list[0]
# # # #                     except (KeyError, TypeError):
# # # #                         pass
        
# # # #         # 3. FALLBACK: Ekstraksi Data dari JSON-LD (Jika variation_data TIDAK Ditemukan)
# # # #         if not variation_data:
# # # #             print("[INFO] 'variationData' tidak ditemukan. Mencoba mengekstrak dari JSON-LD.")
# # # #             json_ld_product_data = extract_product_data_from_json_ld(soup)
            
# # # #             if json_ld_product_data:
# # # #                 # Ganti variabel utama dengan data dari JSON-LD jika kosong
# # # #                 if not overview_content and json_ld_product_data.get('description'):
# # # #                     overview_content = json_ld_product_data['description']
                
# # # #                 if not brand_name and json_ld_product_data.get('brand'):
# # # #                     brand_name = json_ld_product_data['brand']
                
# # # #                 # Update Nama Produk jika ditemukan di JSON-LD dan sebelumnya belum ditemukan
# # # #                 if product_name == 'NAMA PRODUK TIDAK DITEMUKAN' and json_ld_product_data.get('name'):
# # # #                     product_name = json_ld_product_data['name']
                
# # # #                 # Buat struktur 'variation_data' tiruan dari 'offer' untuk single SKU (agar logika pemrosesan varian tetap berjalan)
# # # #                 if json_ld_product_data.get('offer'):
# # # #                     offer = json_ld_product_data['offer']
# # # #                     simulated_variation = [{
# # # #                         'sku': offer.get('sku', json_ld_product_data.get('sku', 'N/A')),
# # # #                         'title': json_ld_product_data.get('name', 'N/A'),
# # # #                         'price': {'price': {'displayValue': f"{offer.get('price', 'N/A')} {offer.get('priceCurrency', '')}"}},
# # # #                         'images': [{'original': json_ld_product_data.get('image')}] if json_ld_product_data.get('image') else [],
# # # #                         'choices': [{'title': product_name}] # Tambahkan title untuk nama varian
# # # #                     }]
# # # #                     variation_data = simulated_variation
# # # #             else:
# # # #                 print("[INFO] Data produk dari JSON-LD tidak ditemukan.")

# # # #         # 4. Fallback HTML (untuk overview, ingredients, brand)
# # # #         if not overview_content:
# # # #             overview_content = extract_product_overview_from_html(soup)
        
# # # #         if not ingredients_content:
# # # #             ingredients_content = extract_ingredients_from_html(soup)

# # # #         if not brand_name:
# # # #             brand_name = extract_brand_from_html(soup)
        
# # # #         # ======================================================================
# # # #         # III. LOGIKA PEMROSESAN VARIAN (Membuat List Objek Output)
# # # #         # ======================================================================

# # # #         final_product_list = []
        
# # # #         # Formatting data produk induk (yang akan disalin ke setiap varian)
# # # #         brand_val = brand_name if brand_name else 'N/A'
# # # #         overview_val = overview_content.replace('\n', ' ') if overview_content else 'N/A'
# # # #         ingredients_val = ingredients_content.replace('\n', ' ') if ingredients_content else 'N/A'
# # # #         rating_val = f"{rating_data['value']} ({rating_data['count']} reviews)" if rating_data else 'N/A'
# # # #         reviews_val = f"{rating_data['count']}" if rating_data else '0'
        
        
# # # #         if variation_data:
# # # #             for item in variation_data:
# # # #                 # 1. Ekstraksi Varian Name
# # # #                 variant_name_raw = 'Varian Tidak Dikenal'
# # # #                 try:
# # # #                     # Ambil dari choices[0]['title'] (Paling akurat)
# # # #                     variant_name_raw = item['choices'][0]['title']
# # # #                 except (KeyError, IndexError, TypeError):
# # # #                     # Fallback ke title item (Bisa berupa "Nama Produk Induk + Varian")
# # # #                     variant_name_raw = item.get('title', product_name)
                
# # # #                 # 2. Format Nama Varian (Full Name)
# # # #                 # Jika nama produk induk TIDAK ada di nama varian mentah, tambahkan.
# # # #                 if product_name != 'NAMA PRODUK TIDAK DITEMUKAN' and product_name not in variant_name_raw:
# # # #                     full_name = f"{product_name} - {variant_name_raw}"
# # # #                 else:
# # # #                     full_name = variant_name_raw

# # # #                 # 3. Ekstraksi Detail Varian
# # # #                 sku_val = item.get('sku', 'N/A')
# # # #                 price_val = item['price']['price']['displayValue'] if 'price' in item and 'price' in item['price'] else 'N/A'
# # # #                 image_url_val = item['images'][0]['original'] if item.get('images') and len(item['images']) > 0 else 'N/A'
                
# # # #                 # CATATAN: URL varian tidak tersedia dalam data JSON yang diekstrak,
# # # #                 # jadi kita akan menggunakan URL induk yang kita scrape.
# # # #                 variant_url_val = url
                
# # # #                 # 4. Konstruksi Objek Varian
# # # #                 variant_object = {
# # # #                     'name': full_name,
# # # #                     'sku varian': sku_val,
# # # #                     'Harga': price_val,
# # # #                     'image url': image_url_val,
# # # #                     'url varian': variant_url_val,
# # # #                     'Ingredients': ingredients_val,
# # # #                     'Brand': brand_val,
# # # #                     'Product Overview': overview_val,
# # # #                     'Rating': rating_val,
# # # #                     'reviews': reviews_val
# # # #                 }
# # # #                 final_product_list.append(variant_object)
        
# # # #         else:
# # # #             # Jika tidak ada variation_data sama sekali (kasus anomali), gunakan data induk
# # # #             print("[WARNING] Tidak ada data varian (variation_data). Menggunakan data induk.")
# # # #             default_object = {
# # # #                 'name': product_name,
# # # #                 'sku varian': 'N/A', 
# # # #                 'Harga': 'N/A',
# # # #                 'image url': 'N/A',
# # # #                 'url varian': url,
# # # #                 'Ingredients': ingredients_val,
# # # #                 'Brand': brand_val,
# # # #                 'Product Overview': overview_val,
# # # #                 'Rating': rating_val,
# # # #                 'reviews': reviews_val
# # # #             }
# # # #             final_product_list.append(default_object)


# # # #         # ======================================================================
# # # #         # IV. OUTPUT HASIL EKSTRAKSI (Format Per Varian Baru)
# # # #         # ======================================================================

# # # #         print("\n" + "="*80)
# # # #         print("## ✅ Hasil Ekstraksi Data Produk (Format Per Varian/SKU)")
# # # #         print("="*80)
        
# # # #         for i, data in enumerate(final_product_list):
# # # #             print(f"\n--- Varian {i+1} ---")
            
# # # #             # Formatting untuk output yang rapi
# # # #             print(f"{'name':<18} = {data['name']}")
# # # #             print(f"{'sku varian':<18} = {data['sku varian']}")
# # # #             print(f"{'Harga':<18} = {data['Harga']}")
# # # #             print(f"{'image url':<18} = {data['image url']}")
# # # #             print(f"{'url varian':<18} = {data['url varian']}")
            
# # # #             # Data Induk (Disalin)
# # # #             print(f"{'Brand':<18} = {data['Brand']}")
# # # #             print(f"{'Rating':<18} = {data['Rating']}")
# # # #             print(f"{'reviews':<18} = {data['reviews']}")
            
# # # #             # Konten panjang dipotong agar tetap rapi
# # # #             overview_print = data['Product Overview'][:500] + '...' if len(data['Product Overview']) > 500 else data['Product Overview']
# # # #             ingredients_print = data['Ingredients'][:500] + '...' if len(data['Ingredients']) > 500 else data['Ingredients']
            
# # # #             print(f"{'Product Overview':<18} = {overview_print}")
# # # #             print(f"{'Ingredients':<18} = {ingredients_print}")

# # # #         print("="*80 + "\n")

# # # #     except Exception as e:
# # # #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # # # ==============================================================================
# # # # # V. EKSEKUSI UJI KASUS
# # # # # ==============================================================================
# # # # if __name__ == "__main__":
    
# # # #     print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK " + "=" * 50)
    
# # # #     # UJI KASUS 1: Multiple Variations (variationData ada)
# # # #     print("\n" + "#" * 120 + "\n")
# # # #     print("--- UJI KASUS 1: Wander Beauty (Multiple Variations - variationData) ---")
# # # #     target_url_1 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# # # #     scrape_dermstore_data(target_url_1)

# # # #     print("\n" + "#" * 120 + "\n")

# # # #     # UJI KASUS 2: Single SKU (variationData tidak ada, menggunakan JSON-LD)
# # # #     print("--- UJI KASUS 2: Alchimie Forever (Single SKU - JSON-LD) ---")
# # # #     target_url_2 = "https://www.dermstore.com/p/act-acre-microbiome-cooling-scalp-serum-65ml/14920973/"
# # # #     scrape_dermstore_data(target_url_2)

# # # #     print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)



# # # import requests
# # # import json
# # # import re
# # # from bs4 import BeautifulSoup
# # # import sys 
# # # from typing import Optional, Dict, List, Tuple, Any

# # # sys.setrecursionlimit(3000)

# # # # ==============================================================================
# # # # I. FUNGSI HELPER (Ekstraksi dari HTML/JSON-LD) - (Tetap Sama)
# # # # ==============================================================================
# # # # (Semua fungsi helper (extract_product_overview_from_html, extract_ingredients_from_html,
# # # # extract_brand_from_html, extract_product_data_from_json_ld, extract_rating_and_reviews) 
# # # # tidak berubah dan tetap berada di bagian atas kode.)
# # # # ...

# # # def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
# # #     # ... (kode tetap sama)
# # #     target_div = soup.find('div', {'id': 'product-description-0'})
# # #     if not target_div:
# # #         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
# # #     if target_div:
# # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # #         return clean_text
# # #     return None

# # # def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
# # #     # ... (kode tetap sama)
# # #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
# # #     if target_div:
# # #         clean_text = target_div.get_text(separator='\n', strip=True)
# # #         return clean_text
# # #     return None

# # # def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
# # #     # ... (kode tetap sama)
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

# # # def extract_product_data_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
# # #     # ... (kode tetap sama)
# # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
# # #     for script in json_ld_scripts:
# # #         if script.string:
# # #             try:
# # #                 data = json.loads(script.string)
# # #                 if isinstance(data, list):
# # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
# # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # #                     product_data = {
# # #                         'name': data.get('name'),
# # #                         'sku': data.get('sku'),
# # #                         'description': data.get('description'),
# # #                         'image': data.get('image'),
# # #                         'brand': data.get('brand', {}).get('name'),
# # #                         'offer': data.get('offers')[0] if data.get('offers') else None
# # #                     }
# # #                     return product_data
# # #             except json.JSONDecodeError:
# # #                 continue
# # #             except (TypeError, IndexError):
# # #                 continue
# # #     return None

# # # def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
# # #     # ... (kode tetap sama)
# # #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
# # #     rating_data = None
# # #     review_list = []
# # #     for script in json_ld_scripts:
# # #         if script.string:
# # #             try:
# # #                 data = json.loads(script.string)
# # #                 if isinstance(data, list):
# # #                     data = next((item for item in data if item.get("@type") == "Product"), None)
# # #                 if isinstance(data, dict) and data.get("@type") == "Product":
# # #                     aggregate_rating = data.get("aggregateRating")
# # #                     if aggregate_rating:
# # #                         rating_data = {
# # #                             'value': aggregate_rating.get('ratingValue'), 
# # #                             'count': aggregate_rating.get('reviewCount')
# # #                         }
# # #                     reviews = data.get("review")
# # #                     if reviews:
# # #                         for review in reviews[:3]: 
# # #                             review_list.append({
# # #                                 'rating': review['reviewRating'].get('ratingValue', 'N/A'),
# # #                                 'author': review['author'].get('name', 'Anonymous'),
# # #                                 'body': review.get('reviewBody', 'No body text'),
# # #                                 'date': review.get('datePublished', 'N/A')
# # #                             })
# # #                     if rating_data or review_list:
# # #                         return rating_data, review_list
# # #             except json.JSONDecodeError:
# # #                 continue
# # #     return rating_data, review_list

# # # # ==============================================================================
# # # # II. FUNGSI UTAMA SCRAPER (Logika Ekstraksi Data)
# # # # ==============================================================================

# # # def scrape_dermstore_data(url: str):
# # #     """Mengambil semua data produk dan memprosesnya menjadi daftar varian/SKU."""
# # #     headers = {
# # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# # #         "Accept-Language": "en-US,en;q=0.9",
# # #         "Referer": "https://www.google.com/"
# # #     }

# # #     print(f"Sedang mengambil data dari: **{url}** ...")
    
# # #     try:
# # #         response = requests.get(url, headers=headers, timeout=15)
        
# # #         if response.status_code != 200:
# # #             print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
# # #             return

# # #         soup = BeautifulSoup(response.text, 'html.parser')
# # #         scripts = soup.find_all('script')
        
# # #         # Inisialisasi variabel data
# # #         variation_data = None
# # #         ingredients_content = None
# # #         brand_name = None 
# # #         overview_content = None
# # #         json_ld_product_data = None
        
# # #         rating_data, review_list = extract_rating_and_reviews(soup)
        
# # #         # Nama Produk Induk (Parent Name) - Akan diisi ulang nanti jika variationData ditemukan
# # #         product_name = 'NAMA PRODUK INDUK TIDAK DITEMUKAN (FALLBACK HTML)'
        
# # #         # 1. Coba dari H1 (Tag Judul Produk Utama)
# # #         h1_tag = soup.find('h1', class_=lambda c: c and 'product-title' in c)
# # #         if h1_tag:
# # #             product_name = h1_tag.get_text(strip=True)
        
# # #         # 2. Fallback ke HTML <title> jika H1 gagal
# # #         if 'TIDAK DITEMUKAN' in product_name:
# # #             title_tag = soup.find('title')
# # #             if title_tag:
# # #                 full_title = title_tag.get_text(strip=True)
# # #                 if '-' in full_title:
# # #                     product_name = full_title.split('-')[0].strip()
# # #                 elif '|' in full_title:
# # #                     product_name = full_title.split('|')[0].strip()
# # #                 else:
# # #                     product_name = full_title
                
# # #                 if not product_name:
# # #                     product_name = full_title
        
# # #         # 3. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
# # #         for script in scripts:
# # #             if script.string and "const variationData =" in script.string:
# # #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# # #                 if match:
# # #                     try:
# # #                         variation_data = json.loads(match.group(1))
# # #                         break
# # #                     except json.JSONDecodeError:
# # #                         pass
        
# # #         # 4. Jika variationData ditemukan, ambil NAMA PRODUK INDUK dari Title varian pertama
# # #         if variation_data and 'title' in variation_data[0] and '-' in variation_data[0]['title']:
# # #             # Contoh: "Wander Beauty Lipsetter Dual Lipstick and Liner - Red Over Heels"
# # #             # Nama Produk Induk adalah bagian sebelum tanda '-'
# # #             product_name = variation_data[0]['title'].split(' - ')[0].strip()
# # #             print(f"[INFO] Nama Produk Induk diperbarui dari variationData: {product_name}")


# # #         # 5. Ekstraksi Konten Utama (Overview, Ingredients, Brand)
# # #         if variation_data:
# # #             print("[INFO] Menggunakan data variasi untuk konten utama.")
# # #             first_variation = variation_data[0] 
# # #             content_list = first_variation.get('content', [])

# # #             for content_item in content_list:
# # #                 if content_item.get('key') == 'synopsis' and not overview_content:
# # #                     try:
# # #                         content_list_value = content_item['value']['richContentListValue'][0]['content']
# # #                         for html_block in content_list_value:
# # #                             if html_block['type'] == 'HTML':
# # #                                 soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
# # #                                 overview_content = soup_overview.get_text(separator="\n", strip=True)
# # #                                 break
# # #                     except (KeyError, TypeError, IndexError):
# # #                         pass

# # #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# # #                     try:
# # #                         content_html_list = content_item['value']['richContentValue']['content']
# # #                         for html_block in content_html_list:
# # #                             if html_block['type'] == 'HTML':
# # #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# # #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
# # #                                 break
# # #                     except (KeyError, TypeError):
# # #                         pass
                        
# # #                 if content_item.get('key') == 'brand' and not brand_name:
# # #                     try:
# # #                         brand_list = content_item['value']['stringListValue']
# # #                         if brand_list:
# # #                             brand_name = brand_list[0]
# # #                     except (KeyError, TypeError):
# # #                         pass
        
# # #         # 6. FALLBACK: Ekstraksi Data dari JSON-LD (Jika variation_data TIDAK Ditemukan)
# # #         if not variation_data:
# # #             print("[INFO] 'variationData' tidak ditemukan. Mencoba mengekstrak dari JSON-LD.")
# # #             json_ld_product_data = extract_product_data_from_json_ld(soup)
            
# # #             if json_ld_product_data:
# # #                 # Ganti variabel utama dengan data dari JSON-LD jika kosong
# # #                 if not overview_content and json_ld_product_data.get('description'):
# # #                     overview_content = json_ld_product_data['description']
                
# # #                 if not brand_name and json_ld_product_data.get('brand'):
# # #                     brand_name = json_ld_product_data['brand']
                
# # #                 # Update Nama Produk Induk jika ditemukan di JSON-LD dan sebelumnya belum ditemukan
# # #                 if product_name == 'NAMA PRODUK INDUK TIDAK DITEMUKAN (FALLBACK HTML)' and json_ld_product_data.get('name'):
# # #                     product_name = json_ld_product_data['name']
                
# # #                 # Buat struktur 'variation_data' tiruan untuk single SKU (agar logika pemrosesan varian tetap berjalan)
# # #                 if json_ld_product_data.get('offer'):
# # #                     offer = json_ld_product_data['offer']
                    
# # #                     # Membuat title varian tunggal sama dengan nama produk induk
# # #                     variant_title = json_ld_product_data.get('name', product_name)
                    
# # #                     simulated_variation = [{
# # #                         'sku': offer.get('sku', json_ld_product_data.get('sku', 'N/A')),
# # #                         'title': variant_title, # Menggunakan nama produk sebagai title
# # #                         'price': {'price': {'displayValue': f"{offer.get('price', 'N/A')} {offer.get('priceCurrency', '')}"}},
# # #                         'images': [{'original': json_ld_product_data.get('image')}] if json_ld_product_data.get('image') else [],
# # #                     }]
# # #                     variation_data = simulated_variation
# # #             else:
# # #                 print("[INFO] Data produk dari JSON-LD tidak ditemukan.")

# # #         # 7. Fallback HTML (untuk overview, ingredients, brand)
# # #         if not overview_content:
# # #             overview_content = extract_product_overview_from_html(soup)
        
# # #         if not ingredients_content:
# # #             ingredients_content = extract_ingredients_from_html(soup)

# # #         if not brand_name:
# # #             brand_name = extract_brand_from_html(soup)
        
# # #         # ======================================================================
# # #         # III. LOGIKA PEMROSESAN VARIAN (Membuat List Objek Output) - REVISI
# # #         # ======================================================================

# # #         final_product_list = []
        
# # #         # Formatting data produk induk (yang akan disalin ke setiap varian)
# # #         brand_val = brand_name if brand_name else 'N/A'
# # #         overview_val = overview_content.replace('\n', ' ') if overview_content else 'N/A'
# # #         ingredients_val = ingredients_content.replace('\n', ' ') if ingredients_content else 'N/A'
# # #         rating_val = f"{rating_data['value']} ({rating_data['count']} reviews)" if rating_data else 'N/A'
# # #         reviews_val = f"{rating_data['count']}" if rating_data else '0'
        
        
# # #         if variation_data:
# # #             for item in variation_data:
                
# # #                 # 1. Ekstraksi Nama Varian & Nama Lengkap BARU (berdasarkan 'title')
# # #                 variant_title_full = item.get('title', product_name)
# # #                 variant_name_raw = 'Varian Utama'
                
# # #                 if '-' in variant_title_full:
# # #                     # Ambil bagian setelah tanda '-' sebagai nama varian/warna
# # #                     parts = variant_title_full.split(' - ')
# # #                     variant_name_raw = parts[-1].strip()
# # #                     # Nama Varian Lengkap (Menggunakan title dari variationData)
# # #                     full_name = variant_title_full.strip()
# # #                 else:
# # #                     # Kasus single SKU / title tidak terpisah, nama varian = nama produk
# # #                     full_name = variant_title_full
                
# # #                 # 2. Ekstraksi Detail Varian
# # #                 sku_val = item.get('sku', 'N/A')
# # #                 price_val = item['price']['price']['displayValue'] if 'price' in item and 'price' in item['price'] else 'N/A'
# # #                 image_url_val = item['images'][0]['original'] if item.get('images') and len(item['images']) > 0 else 'N/A'
# # #                 variant_url_val = url # URL varian tidak tersedia dalam data, menggunakan URL induk
                
# # #                 # 3. Konstruksi Objek Varian
# # #                 variant_object = {
# # #                     'name': full_name,
# # #                     'sku varian': sku_val,
# # #                     'Harga': price_val,
# # #                     'image url': image_url_val,
# # #                     'url varian': variant_url_val,
# # #                     'Ingredients': ingredients_val,
# # #                     'Brand': brand_val,
# # #                     'Product Overview': overview_val,
# # #                     'Rating': rating_val,
# # #                     'reviews': reviews_val
# # #                 }
# # #                 final_product_list.append(variant_object)
        
# # #         else:
# # #             # Jika tidak ada variation_data sama sekali (kasus anomali), gunakan data induk
# # #             print("[WARNING] Tidak ada data varian (variation_data). Menggunakan data induk.")
# # #             default_object = {
# # #                 'name': product_name,
# # #                 'sku varian': 'N/A', 
# # #                 'Harga': 'N/A',
# # #                 'image url': 'N/A',
# # #                 'url varian': url,
# # #                 'Ingredients': ingredients_val,
# # #                 'Brand': brand_val,
# # #                 'Product Overview': overview_val,
# # #                 'Rating': rating_val,
# # #                 'reviews': reviews_val
# # #             }
# # #             final_product_list.append(default_object)


# # #         # ======================================================================
# # #         # IV. OUTPUT HASIL EKSTRAKSI (Format Per Varian Baru) - Tetap Sama
# # #         # ======================================================================

# # #         print("\n" + "="*80)
# # #         print("## ✅ Hasil Ekstraksi Data Produk (Format Per Varian/SKU)")
# # #         print("="*80)
        
# # #         for i, data in enumerate(final_product_list):
# # #             print(f"\n--- Varian {i+1} ---")
            
# # #             # Formatting untuk output yang rapi
# # #             print(f"{'name':<18} = {data['name']}")
# # #             print(f"{'sku varian':<18} = {data['sku varian']}")
# # #             print(f"{'Harga':<18} = {data['Harga']}")
# # #             print(f"{'image url':<18} = {data['image url']}")
# # #             print(f"{'url varian':<18} = {data['url varian']}")
            
# # #             # Data Induk (Disalin)
# # #             print(f"{'Brand':<18} = {data['Brand']}")
# # #             print(f"{'Rating':<18} = {data['Rating']}")
# # #             print(f"{'reviews':<18} = {data['reviews']}")
            
# # #             # Konten panjang dipotong agar tetap rapi
# # #             overview_print = data['Product Overview'][:500] + '...' if len(data['Product Overview']) > 500 else data['Product Overview']
# # #             ingredients_print = data['Ingredients'][:500] + '...' if len(data['Ingredients']) > 500 else data['Ingredients']
            
# # #             print(f"{'Product Overview':<18} = {overview_print}")
# # #             print(f"{'Ingredients':<18} = {ingredients_print}")

# # #         print("="*80 + "\n")

# # #     except Exception as e:
# # #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # # # ==============================================================================
# # # # V. EKSESEKUSI UJI KASUS
# # # # ==============================================================================
# # # if __name__ == "__main__":
    
# # #     print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK " + "=" * 50)
    
# # #     # UJI KASUS 1: Multiple Variations (variationData ada)
# # #     print("\n" + "#" * 120 + "\n")
# # #     print("--- UJI KASUS 1: Wander Beauty (Multiple Variations - variationData) ---")
# # #     target_url_1 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# # #     scrape_dermstore_data(target_url_1)

# # #     print("\n" + "#" * 120 + "\n")

# # #     # UJI KASUS 2: Single SKU (variationData tidak ada, menggunakan JSON-LD)
# # #     print("--- UJI KASUS 2: Alchimie Forever (Single SKU - JSON-LD) ---")
# # #     target_url_2 = "https://www.dermstore.com/p/alchimie-forever-protective-day-cream-spf23/11286078/"
# # #     scrape_dermstore_data(target_url_2)

# # #     print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)



# # import requests
# # import json
# # import re
# # from bs4 import BeautifulSoup
# # import sys 
# # from typing import Optional, Dict, List, Tuple, Any
# # import csv # <--- MODUL BARU: Untuk operasi CSV
# # import os  # <--- MODUL BARU: Untuk mengecek jalur file

# # sys.setrecursionlimit(3000)

# # # ==============================================================================
# # # I. FUNGSI HELPER (Ekstraksi dari HTML/JSON-LD) - (Tetap Sama)
# # # ==============================================================================

# # def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
# #     """Fallback: Mencari Product Overview dari tab HTML."""
# #     target_div = soup.find('div', {'id': 'product-description-0'})
# #     if not target_div:
# #         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
# #     if target_div:
# #         clean_text = target_div.get_text(separator='\n', strip=True)
# #         return clean_text
# #     return None

# # def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
# #     """Fallback: Mencari Ingredients dari tab HTML."""
# #     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
# #     if target_div:
# #         clean_text = target_div.get_text(separator='\n', strip=True)
# #         return clean_text
# #     return None

# # def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
# #     """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
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

# # def extract_product_data_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
# #     """Mengekstrak data dasar produk dari JSON-LD schema markup."""
# #     json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
# #     for script in json_ld_scripts:
# #         if script.string:
# #             try:
# #                 data = json.loads(script.string)
# #                 if isinstance(data, list):
# #                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
# #                 if isinstance(data, dict) and data.get("@type") == "Product":
# #                     product_data = {
# #                         'name': data.get('name'),
# #                         'sku': data.get('sku'),
# #                         'description': data.get('description'),
# #                         'image': data.get('image'),
# #                         'brand': data.get('brand', {}).get('name'),
# #                         'offer': data.get('offers')[0] if data.get('offers') else None
# #                     }
# #                     return product_data
            
# #             except json.JSONDecodeError:
# #                 continue
# #             except (TypeError, IndexError):
# #                 continue
                
# #     return None

# # def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
# #     """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
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
# #                         rating_data = {
# #                             'value': aggregate_rating.get('ratingValue'), 
# #                             'count': aggregate_rating.get('reviewCount')
# #                         }
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

# # # ==============================================================================
# # # II. FUNGSI UTAMA SCRAPER
# # # ==============================================================================

# # def scrape_dermstore_data(url: str, output_filename: str):
# #     """Mengambil semua data produk dan memprosesnya menjadi daftar varian/SKU."""
# #     headers = {
# #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# #         "Accept-Language": "en-US,en;q=0.9",
# #         "Referer": "https://www.google.com/"
# #     }

# #     print(f"Sedang mengambil data dari: **{url}** ...")
    
# #     try:
# #         response = requests.get(url, headers=headers, timeout=15)
        
# #         if response.status_code != 200:
# #             print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
# #             return

# #         soup = BeautifulSoup(response.text, 'html.parser')
# #         scripts = soup.find_all('script')
        
# #         # Inisialisasi variabel data
# #         variation_data = None
# #         ingredients_content = None
# #         brand_name = None 
# #         overview_content = None
        
# #         rating_data, review_list = extract_rating_and_reviews(soup)
        
# #         # Nama Produk Induk (Parent Name) - Akan diisi ulang nanti jika variationData ditemukan
# #         product_name = 'NAMA PRODUK INDUK TIDAK DITEMUKAN (FALLBACK HTML)'
        
# #         # 1. Coba dari H1 (Tag Judul Produk Utama)
# #         h1_tag = soup.find('h1', class_=lambda c: c and 'product-title' in c)
# #         if h1_tag:
# #             product_name = h1_tag.get_text(strip=True)
        
# #         # 2. Fallback ke HTML <title> jika H1 gagal
# #         if 'TIDAK DITEMUKAN' in product_name:
# #             title_tag = soup.find('title')
# #             if title_tag:
# #                 full_title = title_tag.get_text(strip=True)
# #                 if '-' in full_title:
# #                     product_name = full_title.split('-')[0].strip()
# #                 elif '|' in full_title:
# #                     product_name = full_title.split('|')[0].strip()
# #                 else:
# #                     product_name = full_title
                
# #                 if not product_name:
# #                     product_name = full_title
        
# #         # 3. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
# #         for script in scripts:
# #             if script.string and "const variationData =" in script.string:
# #                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
# #                 if match:
# #                     try:
# #                         variation_data = json.loads(match.group(1))
# #                         break
# #                     except json.JSONDecodeError:
# #                         pass
        
# #         # 4. Jika variationData ditemukan, ambil NAMA PRODUK INDUK dari Title varian pertama
# #         if variation_data and 'title' in variation_data[0] and '-' in variation_data[0]['title']:
# #             product_name = variation_data[0]['title'].split(' - ')[0].strip()
# #             print(f"[INFO] Nama Produk Induk diperbarui dari variationData: {product_name}")

# #         # 5. Ekstraksi Konten Utama (Overview, Ingredients, Brand) - Logika tetap sama
# #         if variation_data:
# #             print("[INFO] Menggunakan data variasi untuk konten utama.")
# #             first_variation = variation_data[0] 
# #             content_list = first_variation.get('content', [])

# #             for content_item in content_list:
# #                 if content_item.get('key') == 'synopsis' and not overview_content:
# #                     try:
# #                         content_list_value = content_item['value']['richContentListValue'][0]['content']
# #                         for html_block in content_list_value:
# #                             if html_block['type'] == 'HTML':
# #                                 soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
# #                                 overview_content = soup_overview.get_text(separator="\n", strip=True)
# #                                 break
# #                     except (KeyError, TypeError, IndexError):
# #                         pass

# #                 if content_item.get('key') == 'ingredients' and not ingredients_content:
# #                     try:
# #                         content_html_list = content_item['value']['richContentValue']['content']
# #                         for html_block in content_html_list:
# #                             if html_block['type'] == 'HTML':
# #                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
# #                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
# #                                 break
# #                     except (KeyError, TypeError):
# #                         pass
                        
# #                 if content_item.get('key') == 'brand' and not brand_name:
# #                     try:
# #                         brand_list = content_item['value']['stringListValue']
# #                         if brand_list:
# #                             brand_name = brand_list[0]
# #                     except (KeyError, TypeError):
# #                         pass
        
# #         # 6. FALLBACK: Ekstraksi Data dari JSON-LD (Jika variation_data TIDAK Ditemukan)
# #         if not variation_data:
# #             print("[INFO] 'variationData' tidak ditemukan. Mencoba mengekstrak dari JSON-LD.")
# #             json_ld_product_data = extract_product_data_from_json_ld(soup)
            
# #             if json_ld_product_data:
# #                 # Ganti variabel utama dengan data dari JSON-LD jika kosong
# #                 if not overview_content and json_ld_product_data.get('description'):
# #                     overview_content = json_ld_product_data['description']
                
# #                 if not brand_name and json_ld_product_data.get('brand'):
# #                     brand_name = json_ld_product_data['brand']
                
# #                 # Update Nama Produk Induk
# #                 if 'TIDAK DITEMUKAN' in product_name and json_ld_product_data.get('name'):
# #                     product_name = json_ld_product_data['name']
                
# #                 # Buat struktur 'variation_data' tiruan untuk single SKU
# #                 if json_ld_product_data.get('offer'):
# #                     offer = json_ld_product_data['offer']
# #                     variant_title = json_ld_product_data.get('name', product_name)
                    
# #                     simulated_variation = [{
# #                         'sku': offer.get('sku', json_ld_product_data.get('sku', 'N/A')),
# #                         'title': variant_title, 
# #                         'price': {'price': {'displayValue': f"{offer.get('price', 'N/A')} {offer.get('priceCurrency', '')}"}},
# #                         'images': [{'original': json_ld_product_data.get('image')}] if json_ld_product_data.get('image') else [],
# #                     }]
# #                     variation_data = simulated_variation
# #             else:
# #                 print("[INFO] Data produk dari JSON-LD tidak ditemukan.")

# #         # 7. Fallback HTML (untuk overview, ingredients, brand)
# #         if not overview_content:
# #             overview_content = extract_product_overview_from_html(soup)
        
# #         if not ingredients_content:
# #             ingredients_content = extract_ingredients_from_html(soup)

# #         if not brand_name:
# #             brand_name = extract_brand_from_html(soup)
        
# #         # ======================================================================
# #         # III. LOGIKA PEMROSESAN VARIAN (Membuat List Objek Output)
# #         # ======================================================================

# #         final_product_list = []
        
# #         # Formatting data produk induk (yang akan disalin ke setiap varian)
# #         brand_val = brand_name if brand_name else 'N/A'
# #         # Hapus baris baru/ganti dengan spasi di konten panjang agar rapi di CSV
# #         overview_val = overview_content.replace('\n', ' ').replace('\r', '') if overview_content else 'N/A'
# #         ingredients_val = ingredients_content.replace('\n', ' ').replace('\r', '') if ingredients_content else 'N/A'
# #         rating_val = f"{rating_data['value']} ({rating_data['count']} reviews)" if rating_data else 'N/A'
# #         reviews_val = f"{rating_data['count']}" if rating_data else '0'
        
        
# #         if variation_data:
# #             for item in variation_data:
                
# #                 # 1. Ekstraksi Nama Varian & Nama Lengkap BARU (berdasarkan 'title')
# #                 variant_title_full = item.get('title', product_name)
                
# #                 # Menggunakan title dari variationData sebagai nama produk lengkap
# #                 full_name = variant_title_full.strip()
                
# #                 # 2. Ekstraksi Detail Varian
# #                 sku_val = item.get('sku', 'N/A')
# #                 price_val = item['price']['price']['displayValue'] if 'price' in item and 'price' in item['price'] else 'N/A'
# #                 image_url_val = item['images'][0]['original'] if item.get('images') and len(item['images']) > 0 else 'N/A'
# #                 variant_url_val = url
                
# #                 # 3. Konstruksi Objek Varian
# #                 variant_object = {
# #                     'name': full_name,
# #                     'sku varian': sku_val,
# #                     'Harga': price_val,
# #                     'image url': image_url_val,
# #                     'url varian': variant_url_val,
# #                     'Ingredients': ingredients_val,
# #                     'Brand': brand_val,
# #                     'Product Overview': overview_val,
# #                     'Rating': rating_val,
# #                     'reviews': reviews_val
# #                 }
# #                 final_product_list.append(variant_object)
        
# #         else:
# #             # Jika tidak ada variation_data sama sekali (kasus anomali/single SKU yang tidak terdeteksi)
# #             print("[WARNING] Tidak ada data varian (variation_data). Menggunakan data induk.")
# #             default_object = {
# #                 'name': product_name,
# #                 'sku varian': 'N/A', 
# #                 'Harga': 'N/A',
# #                 'image url': 'N/A',
# #                 'url varian': url,
# #                 'Ingredients': ingredients_val,
# #                 'Brand': brand_val,
# #                 'Product Overview': overview_val,
# #                 'Rating': rating_val,
# #                 'reviews': reviews_val
# #             }
# #             final_product_list.append(default_object)


# #         # ======================================================================
# #         # IV. OUTPUT HASIL EKSTRAKSI & EKSPOR CSV
# #         # ======================================================================

# #         if final_product_list:
# #             # 1. Tampilkan output di console
# #             print("\n" + "="*80)
# #             print("## ✅ Hasil Ekstraksi Data Produk (Format Per Varian/SKU)")
# #             print("="*80)
            
# #             for i, data in enumerate(final_product_list):
# #                 print(f"\n--- Varian {i+1} ---")
                
# #                 # Formatting untuk output console yang rapi (menggunakan overview_val sebelum dipotong)
# #                 print(f"{'name':<18} = {data['name']}")
# #                 print(f"{'sku varian':<18} = {data['sku varian']}")
# #                 print(f"{'Harga':<18} = {data['Harga']}")
# #                 print(f"{'image url':<18} = {data['image url']}")
# #                 print(f"{'url varian':<18} = {data['url varian']}")
# #                 print(f"{'Brand':<18} = {data['Brand']}")
# #                 print(f"{'Rating':<18} = {data['Rating']}")
# #                 print(f"{'reviews':<18} = {data['reviews']}")
                
# #                 overview_print = data['Product Overview'][:500] + '...' if len(data['Product Overview']) > 500 else data['Product Overview']
# #                 ingredients_print = data['Ingredients'][:500] + '...' if len(data['Ingredients']) > 500 else data['Ingredients']
                
# #                 print(f"{'Product Overview':<18} = {overview_print}")
# #                 print(f"{'Ingredients':<18} = {ingredients_print}")

# #             print("="*80 + "\n")

# #             # 2. Ekspor ke CSV
# #             export_to_csv(final_product_list, output_filename)
        
# #     except Exception as e:
# #         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")


# # # ==============================================================================
# # # V. FUNGSI EKSPOR CSV BARU
# # # ==============================================================================

# # def export_to_csv(data_list: List[Dict[str, Any]], filename: str):
# #     """Mengekspor daftar data produk/varian ke file CSV."""
# #     if not data_list:
# #         print("[WARNING] Daftar data kosong, tidak ada file CSV yang dibuat.")
# #         return

# #     # Tentukan header (mengambil kunci dari objek pertama)
# #     fieldnames = list(data_list[0].keys())

# #     # Mode 'w' akan menimpa file jika sudah ada.
# #     # newline='' diperlukan untuk mencegah baris kosong ekstra pada Windows
# #     try:
# #         with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
# #             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
# #             # Menulis header
# #             writer.writeheader()
            
# #             # Menulis data
# #             writer.writerows(data_list)
            
# #         print(f"\n🎉 **BERHASIL!** Data {len(data_list)} varian/SKU telah disimpan ke file: **{os.path.abspath(filename)}**")
        
# #     except Exception as e:
# #         print(f"\n[ERROR] Gagal mengekspor data ke CSV: {e}")


# # # ==============================================================================
# # # VI. EKSEKUSI UJI KASUS
# # # ==============================================================================
# # if __name__ == "__main__":
    
# #     print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK (DENGAN EKSPOR CSV) " + "=" * 50)
    
# #     # UJI KASUS 1: Multiple Variations (akan disimpan ke 'wander_beauty_variants.csv')
# #     print("\n" + "#" * 120 + "\n")
# #     print("--- UJI KASUS 1: Wander Beauty (Multiple Variations) ---")
# #     target_url_1 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# #     scrape_dermstore_data(target_url_1, "wander_beauty_variants.csv")

# #     print("\n" + "#" * 120 + "\n")

# #     # UJI KASUS 2: Single SKU (akan disimpan ke 'alchimie_forever_single.csv')
# #     print("--- UJI KASUS 2: Alchimie Forever (Single SKU) ---")
# #     target_url_2 = "https://www.dermstore.com/p/alchimie-forever-protective-day-cream-spf23/11286078/"
# #     scrape_dermstore_data(target_url_2, "alchimie_forever_single.csv")

# #     print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)



# import requests
# import json
# import re
# from bs4 import BeautifulSoup
# import sys 
# from typing import Optional, Dict, List, Tuple, Any
# import csv
# import os

# sys.setrecursionlimit(3000)

# # ==============================================================================
# # I. FUNGSI HELPER (Ekstraksi dari HTML/JSON-LD)
# # ==============================================================================

# def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
#     """Fallback: Mencari Product Overview dari tab HTML."""
#     target_div = soup.find('div', {'id': 'product-description-0'})
#     if not target_div:
#         target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
#     if target_div:
#         clean_text = target_div.get_text(separator='\n', strip=True)
#         return clean_text
#     return None

# def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
#     """Fallback: Mencari Ingredients dari tab HTML."""
#     target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
#     if target_div:
#         clean_text = target_div.get_text(separator='\n', strip=True)
#         return clean_text
#     return None

# def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
#     """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
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

# def extract_product_data_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
#     """Mengekstrak data dasar produk dari JSON-LD schema markup."""
#     json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
#     for script in json_ld_scripts:
#         if script.string:
#             try:
#                 data = json.loads(script.string)
#                 if isinstance(data, list):
#                     data = next((item for item in data if item.get("@type") == "Product"), None)
                
#                 if isinstance(data, dict) and data.get("@type") == "Product":
#                     product_data = {
#                         'name': data.get('name'),
#                         'sku': data.get('sku'),
#                         'description': data.get('description'),
#                         'image': data.get('image'),
#                         'brand': data.get('brand', {}).get('name'),
#                         'offer': data.get('offers')[0] if data.get('offers') else None
#                     }
#                     return product_data
            
#             except json.JSONDecodeError:
#                 continue
#             except (TypeError, IndexError):
#                 continue
                
#     return None

# def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
#     """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
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
#                         rating_data = {
#                             'value': aggregate_rating.get('ratingValue'), 
#                             'count': aggregate_rating.get('reviewCount')
#                         }
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

# # ==============================================================================
# # II. FUNGSI UTAMA SCRAPER
# # ==============================================================================

# def extract_product_id(url: str) -> str:
#     """Mengekstrak product_id (8 digit angka terakhir) dari URL."""
#     # Mencari 8 digit angka setelah path produk (/p/...)
#     match = re.search(r'/(\d{8})/?$', url)
#     if match:
#         return match.group(1)
#     return 'ID_TIDAK_DITEMUKAN'

# def scrape_dermstore_data(url: str, output_filename: str, first_run: bool):
#     """Mengambil semua data produk dan memprosesnya menjadi daftar varian/SKU."""
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": "https://www.google.com/"
#     }

#     print(f"\nSedang mengambil data dari: **{url}** ...")
    
#     try:
#         response = requests.get(url, headers=headers, timeout=15)
        
#         if response.status_code != 200:
#             print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
#             return

#         soup = BeautifulSoup(response.text, 'html.parser')
#         scripts = soup.find_all('script')
        
#         # Ekstraksi Product ID
#         product_id_val = extract_product_id(url)
#         print(f"[INFO] Product ID ditemukan: {product_id_val}")
        
#         # Inisialisasi variabel data
#         variation_data = None
#         ingredients_content = None
#         brand_name = None 
#         overview_content = None
        
#         rating_data, review_list = extract_rating_and_reviews(soup)
        
#         # Nama Produk Induk (Parent Name) - Akan diisi ulang nanti jika variationData ditemukan
#         product_name = 'NAMA PRODUK INDUK TIDAK DITEMUKAN (FALLBACK HTML)'
        
#         # ... (Logika ekstraksi Brand, Overview, Ingredients, VariationData tetap sama) ...
#         # 1. Coba dari H1 (Tag Judul Produk Utama)
#         h1_tag = soup.find('h1', class_=lambda c: c and 'product-title' in c)
#         if h1_tag:
#             product_name = h1_tag.get_text(strip=True)
        
#         # 2. Fallback ke HTML <title> jika H1 gagal
#         if 'TIDAK DITEMUKAN' in product_name:
#             title_tag = soup.find('title')
#             if title_tag:
#                 full_title = title_tag.get_text(strip=True)
#                 if '-' in full_title:
#                     product_name = full_title.split('-')[0].strip()
#                 elif '|' in full_title:
#                     product_name = full_title.split('|')[0].strip()
#                 else:
#                     product_name = full_title
                
#                 if not product_name:
#                     product_name = full_title
        
#         # 3. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
#         for script in scripts:
#             if script.string and "const variationData =" in script.string:
#                 match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
#                 if match:
#                     try:
#                         variation_data = json.loads(match.group(1))
#                         break
#                     except json.JSONDecodeError:
#                         pass
        
#         # 4. Jika variationData ditemukan, ambil NAMA PRODUK INDUK dari Title varian pertama
#         if variation_data and 'title' in variation_data[0] and '-' in variation_data[0]['title']:
#             product_name = variation_data[0]['title'].split(' - ')[0].strip()
#             print(f"[INFO] Nama Produk Induk diperbarui dari variationData: {product_name}")

#         # 5. Ekstraksi Konten Utama (Overview, Ingredients, Brand) - Logika tetap sama
#         if variation_data:
#             first_variation = variation_data[0] 
#             content_list = first_variation.get('content', [])

#             for content_item in content_list:
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

#                 if content_item.get('key') == 'ingredients' and not ingredients_content:
#                     try:
#                         content_html_list = content_item['value']['richContentValue']['content']
#                         for html_block in content_html_list:
#                             if html_block['type'] == 'HTML':
#                                 soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
#                                 ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
#                                 break
#                     except (KeyError, TypeError):
#                         pass
                        
#                 if content_item.get('key') == 'brand' and not brand_name:
#                     try:
#                         brand_list = content_item['value']['stringListValue']
#                         if brand_list:
#                             brand_name = brand_list[0]
#                     except (KeyError, TypeError):
#                         pass
        
#         # 6. FALLBACK: Ekstraksi Data dari JSON-LD (Jika variation_data TIDAK Ditemukan)
#         if not variation_data:
#             json_ld_product_data = extract_product_data_from_json_ld(soup)
            
#             if json_ld_product_data:
#                 # Ganti variabel utama dengan data dari JSON-LD jika kosong
#                 if not overview_content and json_ld_product_data.get('description'):
#                     overview_content = json_ld_product_data['description']
                
#                 if not brand_name and json_ld_product_data.get('brand'):
#                     brand_name = json_ld_product_data['brand']
                
#                 # Update Nama Produk Induk
#                 if 'TIDAK DITEMUKAN' in product_name and json_ld_product_data.get('name'):
#                     product_name = json_ld_product_data['name']
                
#                 # Buat struktur 'variation_data' tiruan untuk single SKU
#                 if json_ld_product_data.get('offer'):
#                     offer = json_ld_product_data['offer']
#                     variant_title = json_ld_product_data.get('name', product_name)
                    
#                     simulated_variation = [{
#                         'sku': offer.get('sku', json_ld_product_data.get('sku', 'N/A')),
#                         'title': variant_title, 
#                         'price': {'price': {'displayValue': f"{offer.get('price', 'N/A')} {offer.get('priceCurrency', '')}"}},
#                         'images': [{'original': json_ld_product_data.get('image')}] if json_ld_product_data.get('image') else [],
#                     }]
#                     variation_data = simulated_variation
#             else:
#                 pass # JSON-LD tidak ditemukan.

#         # 7. Fallback HTML (untuk overview, ingredients, brand)
#         if not overview_content:
#             overview_content = extract_product_overview_from_html(soup)
        
#         if not ingredients_content:
#             ingredients_content = extract_ingredients_from_html(soup)

#         if not brand_name:
#             brand_name = extract_brand_from_html(soup)
        
#         # ======================================================================
#         # III. LOGIKA PEMROSESAN VARIAN (Membuat List Objek Output)
#         # ======================================================================

#         final_product_list = []
        
#         # Formatting data produk induk (yang akan disalin ke setiap varian)
#         brand_val = brand_name if brand_name else 'N/A'
#         # Hapus baris baru/ganti dengan spasi di konten panjang agar rapi di CSV
#         overview_val = overview_content.replace('\n', ' ').replace('\r', '') if overview_content else 'N/A'
#         ingredients_val = ingredients_content.replace('\n', ' ').replace('\r', '') if ingredients_content else 'N/A'
#         rating_val = f"{rating_data['value']} ({rating_data['count']} reviews)" if rating_data else 'N/A'
#         reviews_val = f"{rating_data['count']}" if rating_data else '0'
        
        
#         if variation_data:
#             for item in variation_data:
                
#                 # 1. Ekstraksi Nama Varian & Nama Lengkap BARU (berdasarkan 'title')
#                 variant_title_full = item.get('title', product_name)
#                 full_name = variant_title_full.strip()
                
#                 # 2. Ekstraksi Detail Varian
#                 sku_val = item.get('sku', 'N/A')
#                 price_val = item['price']['price']['displayValue'] if 'price' in item and 'price' in item['price'] else 'N/A'
#                 image_url_val = item['images'][0]['original'] if item.get('images') and len(item['images']) > 0 else 'N/A'
#                 variant_url_val = url
                
#                 # 3. Konstruksi Objek Varian (MENAMBAH product_id)
#                 variant_object = {
#                     'product_id': product_id_val, # <--- BARU: Product ID
#                     'name': full_name,
#                     'sku varian': sku_val,
#                     'Harga': price_val,
#                     'image url': image_url_val,
#                     'url varian': variant_url_val,
#                     'Ingredients': ingredients_val,
#                     'Brand': brand_val,
#                     'Product Overview': overview_val,
#                     'Rating': rating_val,
#                     'reviews': reviews_val
#                 }
#                 final_product_list.append(variant_object)
        
#         else:
#             # Kasus single SKU yang tidak terdeteksi oleh variation_data
#             default_object = {
#                 'product_id': product_id_val, # <--- BARU: Product ID
#                 'name': product_name,
#                 'sku varian': 'N/A', 
#                 'Harga': 'N/A',
#                 'image url': 'N/A',
#                 'url varian': url,
#                 'Ingredients': ingredients_val,
#                 'Brand': brand_val,
#                 'Product Overview': overview_val,
#                 'Rating': rating_val,
#                 'reviews': reviews_val
#             }
#             final_product_list.append(default_object)


#         # ======================================================================
#         # IV. OUTPUT HASIL EKSTRAKSI & EKSPOR CSV (Menggunakan mode APPEND)
#         # ======================================================================

#         if final_product_list:
#             # Tampilkan output di console
#             print("\n" + "="*80)
#             print("## ✅ Hasil Ekstraksi Data Produk (Format Per Varian/SKU)")
#             print("="*80)
            
#             for i, data in enumerate(final_product_list):
#                 print(f"\n--- Varian {i+1} ---")
                
#                 # Formatting untuk output console yang rapi
#                 print(f"{'product_id':<18} = {data['product_id']}") # Menampilkan ID
#                 print(f"{'name':<18} = {data['name']}")
#                 print(f"{'sku varian':<18} = {data['sku varian']}")
#                 print(f"{'Harga':<18} = {data['Harga']}")
#                 print(f"{'image url':<18} = {data['image url']}")
#                 print(f"{'url varian':<18} = {data['url varian']}")
#                 print(f"{'Brand':<18} = {data['Brand']}")
#                 print(f"{'Rating':<18} = {data['Rating']}")
#                 print(f"{'reviews':<18} = {data['reviews']}")
                
#                 overview_print = data['Product Overview'][:500] + '...' if len(data['Product Overview']) > 500 else data['Product Overview']
#                 ingredients_print = data['Ingredients'][:500] + '...' if len(data['Ingredients']) > 500 else data['Ingredients']
                
#                 print(f"{'Product Overview':<18} = {overview_print}")
#                 print(f"{'Ingredients':<18} = {ingredients_print}")

#             print("="*80 + "\n")

#             # Ekspor ke CSV
#             export_to_csv(final_product_list, output_filename, first_run)
        
#     except Exception as e:
#         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")


# # ==============================================================================
# # V. FUNGSI EKSPOR CSV DIREVISI (Untuk mode append/tambah)
# # ==============================================================================

# def export_to_csv(data_list: List[Dict[str, Any]], filename: str, first_run: bool):
#     """Mengekspor daftar data produk/varian ke file CSV, APPEND jika bukan run pertama."""
#     if not data_list:
#         return

#     # Tentukan header (mengambil kunci dari objek pertama)
#     fieldnames = list(data_list[0].keys())
    
#     # Tentukan mode: 'w' (write/tulis) jika run pertama, 'a' (append/tambah) jika bukan
#     write_mode = 'w' if first_run else 'a'
    
#     # Perlu menulis header hanya jika: (1) ini adalah run pertama, ATAU (2) file belum ada
#     write_header = first_run or not os.path.exists(filename) 
    
#     try:
#         with open(filename, write_mode, newline='', encoding='utf-8') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
#             if write_header:
#                 writer.writeheader()
                
#             writer.writerows(data_list)
            
#         action = "dibuat dan diisi" if first_run else "ditambahkan"
#         print(f"\n🎉 **BERHASIL!** Data {len(data_list)} varian/SKU telah {action} ke file: **{os.path.abspath(filename)}**")
        
#     except Exception as e:
#         print(f"\n[ERROR] Gagal mengekspor data ke CSV: {e}")


# # ==============================================================================
# # VI. EKSEKUSI UJI KASUS
# # ==============================================================================
# if __name__ == "__main__":
    
#     OUTPUT_FILE = "data_dermstore.csv"
    
#     # Hapus file lama jika ada, untuk memastikan pengujian dimulai dari awal (bersih)
#     if os.path.exists(OUTPUT_FILE):
#         os.remove(OUTPUT_FILE)
#         print(f"File lama '{OUTPUT_FILE}' dihapus untuk memulai pengujian baru.")

#     print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK DAN GABUNGAN CSV " + "=" * 50)
    
#     # UJI KASUS 1: Multiple Variations (Ini adalah 'first_run' = True)
#     print("\n" + "#" * 120 + "\n")
#     print("--- UJI KASUS 1: Wander Beauty (Multiple Variations) ---")
#     target_url_1 = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
#     scrape_dermstore_data(target_url_1, OUTPUT_FILE, first_run=True)

#     print("\n" + "#" * 120 + "\n")

#     # UJI KASUS 2: Single SKU (Ini adalah 'first_run' = False, data akan ditambahkan)
#     print("--- UJI KASUS 2: Alchimie Forever (Single SKU) ---")
#     target_url_2 = "https://www.dermstore.com/p/alchimie-forever-protective-day-cream-spf23/11286078/"
#     scrape_dermstore_data(target_url_2, OUTPUT_FILE, first_run=False)

#     print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)
#     print(f"Silakan periksa file **{OUTPUT_FILE}** yang berisi gabungan data dari kedua URL.")



import requests
import json
import re
from bs4 import BeautifulSoup
import sys 
from typing import Optional, Dict, List, Tuple, Any
import csv
import os

sys.setrecursionlimit(3000)

# ==============================================================================
# I. FUNGSI HELPER (Ekstraksi dari HTML/JSON-LD) - (Tetap Sama)
# ==============================================================================
# ... (Semua fungsi helper tetap sama) ...
def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
    """Fallback: Mencari Product Overview dari tab HTML."""
    target_div = soup.find('div', {'id': 'product-description-0'})
    if not target_div:
        target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return None

def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
    """Fallback: Mencari Ingredients dari tab HTML."""
    target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return None

def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
    """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
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

def extract_product_data_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """Mengekstrak data dasar produk dari JSON-LD schema markup."""
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    for script in json_ld_scripts:
        if script.string:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = next((item for item in data if item.get("@type") == "Product"), None)
                
                if isinstance(data, dict) and data.get("@type") == "Product":
                    product_data = {
                        'name': data.get('name'),
                        'sku': data.get('sku'),
                        'description': data.get('description'),
                        'image': data.get('image'),
                        'brand': data.get('brand', {}).get('name'),
                        'offer': data.get('offers')[0] if data.get('offers') else None
                    }
                    return product_data
            
            except json.JSONDecodeError:
                continue
            except (TypeError, IndexError):
                continue
                
    return None

def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
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
                        rating_data = {
                            'value': aggregate_rating.get('ratingValue'), 
                            'count': aggregate_rating.get('reviewCount')
                        }
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

# ==============================================================================
# II. FUNGSI UTAMA SCRAPER
# ==============================================================================

def extract_product_id(url: str) -> str:
    """Mengekstrak product_id (8 digit angka terakhir) dari URL."""
    match = re.search(r'/(\d{8})/?$', url)
    if match:
        return match.group(1)
    return 'ID_TIDAK_DITEMUKAN'

def scrape_dermstore_data(url: str, output_filename: str, first_run: bool):
    """Mengambil semua data produk dan memprosesnya menjadi daftar varian/SKU."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"\nSedang mengambil data dari: **{url}** ...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        # Ekstraksi Product ID
        product_id_val = extract_product_id(url)
        print(f"[INFO] Product ID ditemukan: {product_id_val}")
        
        # Inisialisasi variabel data
        variation_data = None
        ingredients_content = None
        brand_name = None 
        overview_content = None
        
        rating_data, review_list = extract_rating_and_reviews(soup)
        
        # Nama Produk Induk (Parent Name) - Akan diisi ulang nanti jika variationData ditemukan
        product_name = 'NAMA PRODUK INDUK TIDAK DITEMUKAN (FALLBACK HTML)'
        
        # 1. Coba dari H1 (Tag Judul Produk Utama)
        h1_tag = soup.find('h1', class_=lambda c: c and 'product-title' in c)
        if h1_tag:
            product_name = h1_tag.get_text(strip=True)
        
        # 2. Fallback ke HTML <title> jika H1 gagal
        if 'TIDAK DITEMUKAN' in product_name:
            title_tag = soup.find('title')
            if title_tag:
                full_title = title_tag.get_text(strip=True)
                if '-' in full_title:
                    product_name = full_title.split('-')[0].strip()
                elif '|' in full_title:
                    product_name = full_title.split('|')[0].strip()
                else:
                    product_name = full_title
                
                if not product_name:
                    product_name = full_title
        
        # 3. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
        for script in scripts:
            if script.string and "const variationData =" in script.string:
                match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if match:
                    try:
                        variation_data = json.loads(match.group(1))
                        break
                    except json.JSONDecodeError:
                        pass
        
        # 4. Jika variationData ditemukan, ambil NAMA PRODUK INDUK dari Title varian pertama
        if variation_data and 'title' in variation_data[0] and '-' in variation_data[0]['title']:
            product_name = variation_data[0]['title'].split(' - ')[0].strip()
            print(f"[INFO] Nama Produk Induk diperbarui dari variationData: {product_name}")

        # 5. Ekstraksi Konten Utama (Overview, Ingredients, Brand) - Logika tetap sama
        if variation_data:
            first_variation = variation_data[0] 
            content_list = first_variation.get('content', [])

            for content_item in content_list:
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

                if content_item.get('key') == 'ingredients' and not ingredients_content:
                    try:
                        content_html_list = content_item['value']['richContentValue']['content']
                        for html_block in content_html_list:
                            if html_block['type'] == 'HTML':
                                soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
                                ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
                                break
                    except (KeyError, TypeError):
                        pass
                        
                if content_item.get('key') == 'brand' and not brand_name:
                    try:
                        brand_list = content_item['value']['stringListValue']
                        if brand_list:
                            brand_name = brand_list[0]
                    except (KeyError, TypeError):
                        pass
        
        # 6. FALLBACK: Ekstraksi Data dari JSON-LD (Jika variation_data TIDAK Ditemukan)
        if not variation_data:
            json_ld_product_data = extract_product_data_from_json_ld(soup)
            
            if json_ld_product_data:
                # Ganti variabel utama dengan data dari JSON-LD jika kosong
                if not overview_content and json_ld_product_data.get('description'):
                    overview_content = json_ld_product_data['description']
                
                if not brand_name and json_ld_product_data.get('brand'):
                    brand_name = json_ld_product_data['brand']
                
                # Update Nama Produk Induk
                if 'TIDAK DITEMUKAN' in product_name and json_ld_product_data.get('name'):
                    product_name = json_ld_product_data['name']
                
                # Buat struktur 'variation_data' tiruan untuk single SKU
                if json_ld_product_data.get('offer'):
                    offer = json_ld_product_data['offer']
                    variant_title = json_ld_product_data.get('name', product_name)
                    
                    simulated_variation = [{
                        'sku': offer.get('sku', json_ld_product_data.get('sku', 'N/A')),
                        'title': variant_title, 
                        'price': {'price': {'displayValue': f"{offer.get('price', 'N/A')} {offer.get('priceCurrency', '')}"}},
                        'images': [{'original': json_ld_product_data.get('image')}] if json_ld_product_data.get('image') else [],
                    }]
                    variation_data = simulated_variation
            else:
                pass

        # 7. Fallback HTML (untuk overview, ingredients, brand)
        if not overview_content:
            overview_content = extract_product_overview_from_html(soup)
        
        if not ingredients_content:
            ingredients_content = extract_ingredients_from_html(soup)

        if not brand_name:
            brand_name = extract_brand_from_html(soup)
        
        # ======================================================================
        # III. LOGIKA PEMROSESAN VARIAN (Membuat List Objek Output) - REVISI RATING
        # ======================================================================

        final_product_list = []
        
        # Formatting data produk induk (yang akan disalin ke setiap varian)
        brand_val = brand_name if brand_name else 'N/A'
        overview_val = overview_content.replace('\n', ' ').replace('\r', '') if overview_content else 'N/A'
        ingredients_val = ingredients_content.replace('\n', ' ').replace('\r', '') if ingredients_content else 'N/A'
        
        # --- REVISI FORMAT RATING DI SINI ---
        rating_val = 'N/A'
        if rating_data and rating_data.get('value') is not None:
            try:
                # Ambil nilai rating, konversi ke float, lalu format menjadi 1 desimal
                raw_rating = float(rating_data['value'])
                rating_val = f"{raw_rating:.1f}"
            except (ValueError, TypeError):
                rating_val = 'N/A'
        # ------------------------------------
        
        reviews_val = f"{rating_data['count']}" if rating_data else '0'
        
        
        if variation_data:
            for item in variation_data:
                
                # 1. Ekstraksi Nama Varian & Nama Lengkap BARU (berdasarkan 'title')
                variant_title_full = item.get('title', product_name)
                full_name = variant_title_full.strip()
                
                # 2. Ekstraksi Detail Varian
                sku_val = item.get('sku', 'N/A')
                price_val = item['price']['price']['displayValue'] if 'price' in item and 'price' in item['price'] else 'N/A'
                image_url_val = item['images'][0]['original'] if item.get('images') and len(item['images']) > 0 else 'N/A'
                variant_url_val = url
                
                # 3. Konstruksi Objek Varian (dengan Product ID dan Rating Baru)
                variant_object = {
                    'product_id': product_id_val, 
                    'name': full_name,
                    'sku varian': sku_val,
                    'Harga': price_val,
                    'image url': image_url_val,
                    'url varian': variant_url_val,
                    'Ingredients': ingredients_val,
                    'Brand': brand_val,
                    'Product Overview': overview_val,
                    'Rating': rating_val, # <--- Nilai Rating yang sudah diformat
                    'reviews': reviews_val
                }
                final_product_list.append(variant_object)
        
        else:
            # Kasus single SKU yang tidak terdeteksi oleh variation_data
            default_object = {
                'product_id': product_id_val, 
                'name': product_name,
                'sku varian': 'N/A', 
                'Harga': 'N/A',
                'image url': 'N/A',
                'url varian': url,
                'Ingredients': ingredients_val,
                'Brand': brand_val,
                'Product Overview': overview_val,
                'Rating': rating_val, # <--- Nilai Rating yang sudah diformat
                'reviews': reviews_val
            }
            final_product_list.append(default_object)


        # ======================================================================
        # IV. OUTPUT HASIL EKSTRAKSI & EKSPOR CSV
        # ======================================================================

        if final_product_list:
            # Tampilkan output di console
            print("\n" + "="*80)
            print("## ✅ Hasil Ekstraksi Data Produk (Format Per Varian/SKU)")
            print("="*80)
            
            for i, data in enumerate(final_product_list):
                print(f"\n--- Varian {i+1} ---")
                
                # Formatting untuk output console yang rapi
                print(f"{'product_id':<18} = {data['product_id']}") 
                print(f"{'name':<18} = {data['name']}")
                print(f"{'sku varian':<18} = {data['sku varian']}")
                print(f"{'Harga':<18} = {data['Harga']}")
                print(f"{'image url':<18} = {data['image url']}")
                print(f"{'url varian':<18} = {data['url varian']}")
                print(f"{'Brand':<18} = {data['Brand']}")
                print(f"{'Rating':<18} = {data['Rating']}") # Menampilkan Rating baru
                print(f"{'reviews':<18} = {data['reviews']}")
                
                overview_print = data['Product Overview'][:500] + '...' if len(data['Product Overview']) > 500 else data['Product Overview']
                ingredients_print = data['Ingredients'][:500] + '...' if len(data['Ingredients']) > 500 else data['Ingredients']
                
                print(f"{'Product Overview':<18} = {overview_print}")
                print(f"{'Ingredients':<18} = {ingredients_print}")

            print("="*80 + "\n")

            # Ekspor ke CSV
            export_to_csv(final_product_list, output_filename, first_run)
        
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")


# ==============================================================================
# V. FUNGSI EKSPOR CSV DIREVISI (Untuk mode append/tambah) - (Tetap Sama)
# ==============================================================================

def export_to_csv(data_list: List[Dict[str, Any]], filename: str, first_run: bool):
    """Mengekspor daftar data produk/varian ke file CSV, APPEND jika bukan run pertama."""
    if not data_list:
        return

    fieldnames = list(data_list[0].keys())
    write_mode = 'w' if first_run else 'a'
    write_header = first_run or not os.path.exists(filename) 
    
    try:
        with open(filename, write_mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if write_header:
                writer.writeheader()
                
            writer.writerows(data_list)
            
        action = "dibuat dan diisi" if first_run else "ditambahkan"
        print(f"\n🎉 **BERHASIL!** Data {len(data_list)} varian/SKU telah {action} ke file: **{os.path.abspath(filename)}**")
        
    except Exception as e:
        print(f"\n[ERROR] Gagal mengekspor data ke CSV: {e}")


# ==============================================================================
# VI. EKSEKUSI UJI KASUS
# ==============================================================================
if __name__ == "__main__":
    
    OUTPUT_FILE = "data_dermstore.csv"
    
    # Hapus file lama jika ada, untuk memastikan pengujian dimulai dari awal (bersih)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"File lama '{OUTPUT_FILE}' dihapus untuk memulai pengujian baru.")

    print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK DAN GABUNGAN CSV " + "=" * 50)
    
    # UJI KASUS 1: Wander Beauty (Multiple Variations)
    # Catatan: Wander Beauty memiliki rating 4.6667, yang akan dibulatkan menjadi 4.7
    print("\n" + "#" * 120 + "\n")
    print("--- UJI KASUS 1: Wander Beauty (Multiple Variations, Rating: 4.6667 -> 4.7) ---")
    target_url_1 = "https://www.dermstore.com/p/111skin-celestial-black-diamond-lifting-and-firming-treatment-mask-box-155-ml/13651650/"
    scrape_dermstore_data(target_url_1, OUTPUT_FILE, first_run=True)

    print("\n" + "#" * 120 + "\n")

    # UJI KASUS 2: Alchimie Forever (Single SKU)
    # Catatan: Alchimie Forever memiliki rating 4.5, yang akan diformat menjadi 4.5
    print("--- UJI KASUS 2: Alchimie Forever (Single SKU, Rating: 4.5 -> 4.5) ---")
    target_url_2 = "https://www.dermstore.com/p/111skin-cryo-de-puffing-energy-mask-box-pack-of-5/12588508/"
    scrape_dermstore_data(target_url_2, OUTPUT_FILE, first_run=False)

    print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)
    print(f"Silakan periksa file **{OUTPUT_FILE}** untuk melihat format rating yang baru.")