# import requests
# import json
# import re
# from bs4 import BeautifulSoup

# def find_key_recursive(data, target_key):
#     """Fungsi rekursif untuk mencari blok data spesifik (misalnya 'ingredients')
#     di dalam struktur JSON yang rumit."""
#     if isinstance(data, dict):
#         # Cek apakah dictionary ini adalah blok yang kita cari
#         if data.get("key") == target_key:
#             # Jika ketemu, ambil value -> richContentValue -> content -> HTML
#             try:
#                 # Struktur berdasarkan data yang Anda kirim
#                 content_list = data['value']['richContentValue']['content']
#                 for item in content_list:
#                     if item['type'] == 'HTML':
#                         return item['content']
#             except (KeyError, TypeError):
#                 pass
        
#         # Jika bukan, cari di anak-anaknya
#         for k, v in data.items():
#             result = find_key_recursive(v, target_key)
#             if result: return result
            
#     elif isinstance(data, list):
#         for item in data:
#             result = find_key_recursive(item, target_key)
#             if result: return result
            
#     return None

# def scrape_dermstore_data(url):
#     """Mengambil data variasi produk dan ingredients dari URL Dermstore."""
#     # 1. Setup Request Headers
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": "https://www.google.com/"
#     }

#     print(f"Sedang mengambil data dari: {url} ...")
    
#     try:
#         response = requests.get(url, headers=headers, timeout=15) # Tingkatkan timeout sedikit
        
#         if response.status_code != 200:
#             print(f"Gagal membuka halaman. Status code: {response.status_code}")
#             return

#         soup = BeautifulSoup(response.text, 'html.parser')
#         scripts = soup.find_all('script')
        
#         # Inisialisasi variabel data
#         variation_data = None
#         preloaded_state_data = None

#         ## Bagian 1: Mencari Data Variasi Produk (variationData)
#         for script in scripts:
#             if script.string:
#                 # Cari Variation Data
#                 if not variation_data and "const variationData =" in script.string:
#                     match = re.search(r'const variationData = (\[.*?\]);', script.string, re.DOTALL)
#                     if match:
#                         try:
#                             variation_data = json.loads(match.group(1))
#                         except json.JSONDecodeError as e:
#                             print(f"Error parsing variationData: {e}")
                
#                 # Cari Preloaded State (tempat ingredients)
#                 if not preloaded_state_data and "window.__PRELOADED_STATE__ =" in script.string:
#                     match = re.search(r'window\.__PRELOADED_STATE__ = ({.*?});', script.string, re.DOTALL)
#                     if match:
#                         try:
#                             preloaded_state_data = json.loads(match.group(1))
#                         except json.JSONDecodeError as e:
#                             print(f"Error parsing PRELOADED_STATE: {e}")
        
#         # --- Bagian 2: Menampilkan Hasil Variasi Produk ---
#         if variation_data:
#             print("\n" + "="*70)
#             print("## 💄 Hasil Ekstraksi Variasi Produk")
#             print("="*70)
#             print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian'}")
#             print("-" * 70)

#             for item in variation_data:
#                 sku = item.get('sku')
#                 title = item.get('title')
#                 in_stock = "Ready" if item.get('inStock') else "Kosong"
                
#                 try:
#                     price = item['price']['price']['displayValue']
#                 except (KeyError, TypeError):
#                     price = "N/A"
                
#                 try:
#                     color_name = item['choices'][0]['title']
#                 except (KeyError, IndexError, TypeError):
#                     color_name = item.get('title', 'Unknown')

#                 print(f"{sku:<10} | {title} | {in_stock:<10} | {price:<8} | {color_name}")
#         else:
#             print("\n[INFO] Data variasi produk tidak ditemukan.")

#         # --- Bagian 3: Menampilkan Hasil Ingredients ---
#         if preloaded_state_data:
#             ingredients_raw_html = find_key_recursive(preloaded_state_data, "ingredients")
            
#             if ingredients_raw_html:
#                 print("\n" + "="*70)
#                 print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
#                 print("="*70)
                
#                 # Bersihkan HTML tags menjadi teks biasa
#                 soup_ingredients = BeautifulSoup(ingredients_raw_html, 'html.parser')
#                 clean_text = soup_ingredients.get_text(separator="\n").strip()
                
#                 print(clean_text)
#                 print("\n" + "="*70)
#             else:
#                 print("\n[INFO] Data Ingredients tidak ditemukan dalam PRELOADED_STATE.")

#         else:
#             print("\n[INFO] Data PRELOADED_STATE (sumber ingredients) tidak ditemukan.")
            
#     except Exception as e:
#         print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# # --- Eksekusi Script ---
# target_url = "https://www.dermstore.com/p/wander-beauty-lipsetter-dual-lipstick-and-liner-various-shades/15150680/"
# scrape_dermstore_data(target_url)


import requests
import json
import re
from bs4 import BeautifulSoup
import sys 
from typing import Optional, Dict, List, Tuple, Any
import csv
import os
import math
import time

sys.setrecursionlimit(3000)

# ==============================================================================
# I. FUNGSI UNTUK PENCARIAN PRODUK/KATEGORI (Dari search_product.py)
# ==============================================================================

# Base URL untuk Dermstore (digunakan untuk membuat URL absolut)
BASE_URL = "https://www.dermstore.com"
# Asumsi: Jumlah produk per halaman adalah 36 (standar PLP Dermstore)
PRODUCTS_PER_PAGE = 36 

def get_total_products(soup: BeautifulSoup) -> int:
    """
    Mencari total jumlah produk di halaman kategori untuk menghitung total halaman
    berdasarkan struktur HTML yang ditemukan.
    """
    total_products_span = soup.find('span', class_='total-products') 
    
    if total_products_span:
        try:
            total = int(total_products_span.get_text(strip=True))
            return total
        except ValueError:
            print("[INFO] Ditemukan tag 'total-products', tetapi nilainya bukan angka valid.")
    
    try:
        text_match = soup.find(string=re.compile(r'\d+ results'))
        if text_match:
             match = re.search(r'of\s*(\d+)\s*results', text_match.strip())
             if match:
                 return int(match.group(1))
    except Exception:
         pass

    print("[INFO] Tidak dapat menemukan total jumlah produk. Mengasumsikan 1 halaman penuh.")
    return PRODUCTS_PER_PAGE 


def search_products_in_category(category_url: str) -> List[Dict[str, str]]:
    """
    Mengambil daftar Product URL dan Nama Produk dari halaman kategori (termasuk pagination).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"\n--- Memulai scraping kategori: {category_url} ---")
    
    product_list = []
    
    # --- 1. Ambil Halaman Pertama untuk Menghitung Total Halaman ---
    try:
        response = requests.get(category_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Gagal membuka halaman kategori utama. Status code: {response.status_code}")
            return product_list
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        total_products = get_total_products(soup)
        total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
        
        if total_pages == 0:
            total_pages = 1 
            
        print(f"[INFO] Ditemukan {total_products} produk total. Akan discrape {total_pages} halaman.")
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Terjadi kesalahan koneksi saat mengambil halaman pertama: {e}")
        return product_list
    
    # --- 2. Loop Semua Halaman ---
    for page in range(1, total_pages + 1):
        if page == 1:
            current_url = category_url
        else:
            separator = '&' if '?' in category_url else '?'
            current_url = f"{category_url}{separator}pageNumber={page}"
                
        print(f"  > Scraping Halaman {page}/{total_pages} dari: {current_url}")
        
        try:
            if page > 1:
                response = requests.get(current_url, headers=headers, timeout=20)
                if response.status_code != 200:
                    print(f"    [WARNING] Gagal mengambil Halaman {page}. Status code: {response.status_code}. Melanjutkan...")
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                time.sleep(1) # Jeda Etis
            
            product_list_container = soup.find('div', id='product-list')
            
            if product_list_container:
                product_links = product_list_container.find_all('a', class_='product-item')

                for anchor in product_links:
                    href = anchor.get('href')
                    title = anchor.get('data-title') 

                    if href and title:
                        full_url = BASE_URL + href if not href.startswith('http') else href
                            
                        # Mencegah duplikasi
                        if full_url not in [p['product_url'] for p in product_list]:
                             product_list.append({
                                'product_name': title,
                                'product_url': full_url
                            })

            else:
                 print(f"    [WARNING] Product container tidak ditemukan di Halaman {page}.")

        except requests.exceptions.RequestException as e:
            print(f"\n    [ERROR] Terjadi kesalahan koneksi saat scraping Halaman {page}: {e}")
            
    print(f"\n--- Selesai scraping kategori. Total {len(product_list)} URL produk unik ditemukan. ---")
    return product_list


# ==============================================================================
# II. FUNGSI HELPER EKSTRAKSI PRODUK (JSON-LD, HTML) - (Tetap Sama)
# ==============================================================================

# ... (Semua fungsi helper dari script sebelumnya, seperti extract_product_overview_from_html,
#      extract_ingredients_from_html, extract_brand_from_html, extract_product_data_from_json_ld,
#      extract_rating_and_reviews, dan extract_product_id) harus ada di sini.
#      Saya hanya menyertakan beberapa sebagai placeholder, tetapi semua harus disalin.

def extract_product_overview_from_html(soup: BeautifulSoup) -> Optional[str]:
    target_div = soup.find('div', {'id': 'product-description-0'})
    if not target_div:
        target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
    if target_div:
        return target_div.get_text(separator='\n', strip=True)
    return None

def extract_ingredients_from_html(soup: BeautifulSoup) -> Optional[str]:
    target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    if target_div:
        return target_div.get_text(separator='\n', strip=True)
    return None

def extract_brand_from_html(soup: BeautifulSoup) -> Optional[str]:
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
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    for script in json_ld_scripts:
        if script.string:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = next((item for item in data if item.get("@type") == "Product"), None)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    product_data = {
                        'name': data.get('name'), 'sku': data.get('sku'), 'description': data.get('description'),
                        'image': data.get('image'), 'brand': data.get('brand', {}).get('name'),
                        'offer': data.get('offers')[0] if data.get('offers') else None
                    }
                    return product_data
            except (json.JSONDecodeError, TypeError, IndexError):
                continue
    return None

def extract_rating_and_reviews(soup: BeautifulSoup) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
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
                    return rating_data, review_list # Hanya mengambil rating/review pertama
            except json.JSONDecodeError:
                continue
    return rating_data, review_list

def extract_product_id(url: str) -> str:
    match = re.search(r'/(\d{8})/?$', url)
    if match:
        return match.group(1)
    return 'ID_TIDAK_DITEMUKAN'
# ------------------------------------------------------------------------------


# ==============================================================================
# III. FUNGSI UTAMA SCRAPER (scrape_dermstore_data) - (Tetap Sama)
# ==============================================================================

def scrape_dermstore_data(url: str, output_filename: str, first_run: bool):
    """Mengambil semua data produk dan memprosesnya menjadi daftar varian/SKU."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    # print(f"Sedang mengambil data dari: **{url}** ...") # Dihapus agar output loop lebih rapi
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  [ERROR] Gagal membuka URL produk. Status code: {response.status_code}. URL: {url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        product_id_val = extract_product_id(url)
        # ... (Logika Ekstraksi Data Produk dari script sebelumnya) ...
        variation_data = None
        ingredients_content = None
        brand_name = None 
        overview_content = None
        rating_data, review_list = extract_rating_and_reviews(soup)
        product_name = 'NAMA PRODUK INDUK TIDAK DITEMUKAN (FALLBACK HTML)'
        
        h1_tag = soup.find('h1', class_=lambda c: c and 'product-title' in c)
        if h1_tag:
            product_name = h1_tag.get_text(strip=True)
        
        if 'TIDAK DITEMUKAN' in product_name:
            title_tag = soup.find('title')
            if title_tag:
                full_title = title_tag.get_text(strip=True)
                product_name = full_title.split('-')[0].strip() if '-' in full_title else full_title
                
        for script in scripts:
            if script.string and "const variationData =" in script.string:
                match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if match:
                    try:
                        variation_data = json.loads(match.group(1))
                        break
                    except json.JSONDecodeError:
                        pass
        
        if variation_data and 'title' in variation_data[0] and '-' in variation_data[0]['title']:
            product_name = variation_data[0]['title'].split(' - ')[0].strip()

        if variation_data:
            first_variation = variation_data[0] 
            content_list = first_variation.get('content', [])
            # (Potongan kode untuk mengisi overview_content, ingredients_content, brand_name dari variation_data)
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

        if not variation_data:
            json_ld_product_data = extract_product_data_from_json_ld(soup)
            if json_ld_product_data:
                if not overview_content and json_ld_product_data.get('description'):
                    overview_content = json_ld_product_data['description']
                if not brand_name and json_ld_product_data.get('brand'):
                    brand_name = json_ld_product_data['brand']
                if 'TIDAK DITEMUKAN' in product_name and json_ld_product_data.get('name'):
                    product_name = json_ld_product_data['name']
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

        if not overview_content:
            overview_content = extract_product_overview_from_html(soup)
        if not ingredients_content:
            ingredients_content = extract_ingredients_from_html(soup)
        if not brand_name:
            brand_name = extract_brand_from_html(soup)
        
        # --- LOGIKA PEMROSESAN VARIAN ---

        final_product_list = []
        brand_val = brand_name if brand_name else 'N/A'
        overview_val = overview_content.replace('\n', ' ').replace('\r', '') if overview_content else 'N/A'
        ingredients_val = ingredients_content.replace('\n', ' ').replace('\r', '') if ingredients_content else 'N/A'
        
        rating_val = 'N/A'
        if rating_data and rating_data.get('value') is not None:
            try:
                raw_rating = float(rating_data['value'])
                rating_val = f"{raw_rating:.1f}"
            except (ValueError, TypeError):
                rating_val = 'N/A'
        
        reviews_val = f"{rating_data['count']}" if rating_data else '0'
        
        
        data_to_add = []
        if variation_data:
            for item in variation_data:
                variant_title_full = item.get('title', product_name)
                full_name = variant_title_full.strip()
                sku_val = item.get('sku', 'N/A')
                price_val = item['price']['price']['displayValue'] if 'price' in item and 'price' in item['price'] else 'N/A'
                image_url_val = item['images'][0]['original'] if item.get('images') and len(item['images']) > 0 else 'N/A'
                
                data_to_add.append({
                    'product_id': product_id_val, 'name': full_name, 'sku varian': sku_val,
                    'Harga': price_val, 'image url': image_url_val, 'url varian': url,
                    'Ingredients': ingredients_val, 'Brand': brand_val,
                    'Product Overview': overview_val, 'Rating': rating_val, 'reviews': reviews_val
                })
        else:
            data_to_add.append({
                'product_id': product_id_val, 'name': product_name, 'sku varian': 'N/A', 
                'Harga': 'N/A', 'image url': 'N/A', 'url varian': url, 'Ingredients': ingredients_val,
                'Brand': brand_val, 'Product Overview': overview_val, 'Rating': rating_val,
                'reviews': reviews_val
            })
        
        final_product_list.extend(data_to_add)

        if final_product_list:
            # Tidak menampilkan detail di console untuk setiap produk agar output tidak terlalu panjang
            export_to_csv(final_product_list, output_filename, first_run)
            return len(final_product_list)
        return 0
        
    except Exception as e:
        print(f"\n  [ERROR] Terjadi kesalahan saat scraping data produk {url}: {e}")
        return 0


# ==============================================================================
# IV. FUNGSI EKSPOR CSV DIREVISI (Untuk mode append/tambah)
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
            
        # Pesan sukses di handle di fungsi utama perulangan
        
    except Exception as e:
        print(f"\n[ERROR] Gagal mengekspor data ke CSV: {filename}: {e}")


# ==============================================================================
# V. EKSEKUSI UTAMA (Menggunakan search_products_in_category)
# ==============================================================================
if __name__ == "__main__":
    
    OUTPUT_FILE = "---------save-data-dermstore-final--1.csv"
    
    # URL Kategori yang akan di-scrape
    # category_urls = [
        
    # ]
    
    category_urls = [
            "https://www.dermstore.com/c/brands/philip-kingsley/",
            "https://www.dermstore.com/c/brands/phyto/",
            "https://www.dermstore.com/c/brands/plume-science/",
            "https://www.dermstore.com/c/brands/pmd/",
            "https://www.dermstore.com/c/brands/rco/",
            "https://www.dermstore.com/c/brands/rco-bleu/",
            "https://www.dermstore.com/c/brands/rahua/",
            "https://www.dermstore.com/c/brands/rapidlash/",
            "https://www.dermstore.com/c/brands/rejuvi/",
            "https://www.dermstore.com/c/brands/rene-furterer/",
            "https://www.dermstore.com/c/brands/replenix/",
            "https://www.dermstore.com/c/brands/rescuemd/",
            "https://www.dermstore.com/c/brands/revision-skincare/",
            "https://www.dermstore.com/c/brands/revitalash-cosmetics/",
            "https://www.dermstore.com/c/brands/rvive-skincare/",
            "https://www.dermstore.com/c/brands/rms-beauty/",
            "https://www.dermstore.com/c/brands/roen/",
            "https://www.dermstore.com/c/brands/sachajuan/",
            "https://www.dermstore.com/c/brands/sanitas-skincare/",
            "https://www.dermstore.com/c/brands/sarah-chapman/",
            "https://www.dermstore.com/c/brands/seen/",
            "https://www.dermstore.com/c/brands/sensica/",
            "https://www.dermstore.com/c/brands/sente/",
            "https://www.dermstore.com/c/brands/shark-beauty/",
            "https://www.dermstore.com/c/brands/sio-beauty/",
            "https://www.dermstore.com/c/brands/sisley-paris/",
            "https://www.dermstore.com/c/brands/sk-ii/",
            "https://www.dermstore.com/c/brands/skin-design-london/",
            "https://www.dermstore.com/c/brands/skin-gym/",
            "https://www.dermstore.com/c/brands/skinceuticals/",
            "https://www.dermstore.com/c/brands/skinmedica/",
            "https://www.dermstore.com/c/brands/skyn-iceland/",
            "https://www.dermstore.com/c/brands/slip/",
            "https://www.dermstore.com/c/brands/smile-makers/",
            "https://www.dermstore.com/c/brands/soleil-toujours/",
            "https://www.dermstore.com/c/brands/st-tropez/",
            "https://www.dermstore.com/c/brands/stila-cosmetics/",
            "https://www.dermstore.com/c/brands/strivectin/",
            "https://www.dermstore.com/c/brands/sunday-riley/",
            "https://www.dermstore.com/c/brands/suntegrity-skincare/",
            "https://www.dermstore.com/c/brands/supergoop/",
            "https://www.dermstore.com/c/brands/supersmile/",
            "https://www.dermstore.com/c/brands/susanne-kaufmann/",
            "https://www.dermstore.com/c/brands/symbiome/",
            "https://www.dermstore.com/c/brands/t3/",
            "https://www.dermstore.com/c/brands/tarte-cosmetics/",
            "https://www.dermstore.com/c/brands/the-light-salon/",
            "https://www.dermstore.com/c/brands/the-nue-co/",
            "https://www.dermstore.com/c/brands/therabody/",
            "https://www.dermstore.com/c/brands/this-works/",
            "https://www.dermstore.com/c/brands/tracie-martyn/",
            "https://www.dermstore.com/c/brands/trudon/",
            "https://www.dermstore.com/c/brands/u-beauty/",
            "https://www.dermstore.com/c/brands/unite-hair/",
            "https://www.dermstore.com/c/brands/ursa-major/",
            "https://www.dermstore.com/c/brands/vacation/",
            "https://www.dermstore.com/c/brands/valmont/",
            "https://www.dermstore.com/c/brands/veronique-gabai/",
            "https://www.dermstore.com/c/brands/verso/",
            "https://www.dermstore.com/c/brands/vi-derm/",
            "https://www.dermstore.com/c/brands/vichy/",
            "https://www.dermstore.com/c/brands/virtue/",
            "https://www.dermstore.com/c/brands/wander-beauty/",
            "https://www.dermstore.com/c/brands/weleda/",
            "https://www.dermstore.com/c/brands/wellbel/",
            "https://www.dermstore.com/c/brands/yon-ka/"
        ]
    # Hapus file lama jika ada
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"File lama '{OUTPUT_FILE}' dihapus untuk memulai pengujian baru.")

    print("\n" + "=" * 50 + " MEMULAI FULL SCRAPING KATEGORI DAN GABUNGAN CSV " + "=" * 50)
    
    # Inisialisasi status
    total_scraped_variants = 0
    total_products_scraped = 0
    is_first_run = True # Kontrol untuk menulis header CSV hanya sekali

    for category_url in category_urls:
        
        # 1. Dapatkan daftar produk dari kategori (termasuk pagination)
        product_list = search_products_in_category(category_url)
        
        if not product_list:
            print(f"  [WARNING] Tidak ada produk yang ditemukan di {category_url}. Melanjutkan ke kategori berikutnya.")
            continue

        print(f"\n--- Memulai scraping {len(product_list)} produk dari kategori ke-CSV ---")
        
        # 2. Loop melalui setiap produk dan scrape data detailnya
        for i, product in enumerate(product_list):
            url = product['product_url']
            
            print(f"  [{i+1}/{len(product_list)}] Mengambil data: {url}...")
            
            # Panggil fungsi detail scraper
            num_variants = scrape_dermstore_data(url, OUTPUT_FILE, first_run=is_first_run)
            
            if num_variants > 0:
                # Setelah berhasil scraping produk pertama/kategori pertama, set is_first_run menjadi False
                # agar header tidak ditulis lagi
                is_first_run = False
                total_scraped_variants += num_variants
                total_products_scraped += 1
            
            time.sleep(1) # Jeda antar permintaan produk detail (Ethical Scraping)

    print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)
    print(f"**Ringkasan Akhir:**")
    print(f"* Total {total_products_scraped} produk unik telah di-scrape.")
    print(f"* Total {total_scraped_variants} baris varian/SKU telah disimpan.")
    print(f"Silakan periksa file **{OUTPUT_FILE}** yang berisi gabungan data dari semua URL produk yang ditemukan.")