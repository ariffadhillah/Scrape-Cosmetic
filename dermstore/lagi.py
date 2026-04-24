import requests
from bs4 import BeautifulSoup
import re
import math
import time
import sys
import json
import csv
import os

sys.setrecursionlimit(3000)

# --- KONSTANTA GLOBAL ---
BASE_URL = "https://www.dermstore.com"
BRAND_PAGE_URL = "https://www.dermstore.com/c/brands/" 
PRODUCTS_PER_PAGE = 36 
OUTPUT_CSV_FILE = "dermstore_scraped_data_per_sku.csv" # <--- NAMA FILE BARU

# ==============================================================================
# I. FUNGSI HELPER (Ekstraksi dari HTML Langsung)
# ==============================================================================
# (Fungsi Helper: extract_product_overview_from_html, extract_ingredients_from_html, 
#  extract_brand_from_html, extract_rating_and_reviews, get_total_products, 
#  search_brand_categories, dan search_products_in_category TIDAK BERUBAH dari 
#  versi sebelumnya, namun harus disertakan di kode akhir Anda.)
# Disederhanakan untuk melihat perubahan inti:

def extract_product_overview_from_html(soup):
    target_div = soup.find('div', {'id': 'product-description-0'})
    if not target_div:
        target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
    return target_div.get_text(separator='\n', strip=True) if target_div else 'N/A'

def extract_ingredients_from_html(soup):
    target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    return target_div.get_text(separator='\n', strip=True) if target_div else 'N/A'

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
    return 'N/A'

def extract_rating_and_reviews(soup):
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    rating_data = {'value': 'N/A', 'count': 'N/A'}
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
                        rating_data = {'value': aggregate_rating.get('ratingValue', 'N/A'), 
                                       'count': aggregate_rating.get('reviewCount', 'N/A')}
                    reviews = data.get("review")
                    if reviews:
                        for review in reviews[:3]: 
                            review_list.append(f"{review['reviewRating'].get('ratingValue', 'N/A')} by {review['author'].get('name', 'Anonymous')}: {review.get('reviewBody', 'No body text')[:50]}...")
                    return rating_data, review_list
            except json.JSONDecodeError:
                continue
    return rating_data, review_list

def get_total_products(soup):
    total_products_span = soup.find('span', class_='total-products') 
    if total_products_span:
        try: return int(total_products_span.get_text(strip=True))
        except ValueError: pass
    try:
        text_match = soup.find(string=re.compile(r'\d+ results'))
        if text_match:
             match = re.search(r'of\s*(\d+)\s*results', text_match.strip())
             if match: return int(match.group(1))
    except Exception: pass
    return PRODUCTS_PER_PAGE

def search_brand_categories(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    brand_list = []
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200: return brand_list
        soup = BeautifulSoup(response.text, 'html.parser')
        main_container = soup.find('div', class_='widgets mb-6 md:mb-12 customWidgetMargin')
        if not main_container: main_container = soup.find('div', class_='mx-auto px-5 mt-12 container')
        if not main_container: return brand_list
        list_items = main_container.find_all('li', class_=lambda c: c and 'w-1/2' in c)
        if not list_items: list_items = main_container.find_all('li')
        for li in list_items:
            anchor = li.find('a')
            if anchor:
                href = anchor.get('href')
                name = anchor.get_text(strip=True)
                if href and name:
                    full_url = BASE_URL + href if not href.startswith('http') else href
                    brand_list.append({'brand_name': name, 'category_url': full_url})
        return brand_list
    except Exception: return brand_list

def search_products_in_category(category_url, brand_name):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    product_list = []
    try:
        response = requests.get(category_url, headers=headers, timeout=20)
        if response.status_code != 200: return product_list
        soup = BeautifulSoup(response.text, 'html.parser')
        total_products = get_total_products(soup)
        total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
        if total_pages == 0: total_pages = 1
        
        for page in range(1, total_pages + 1):
            if page > 1:
                separator = '&' if '?' in category_url else '?'
                current_url = f"{category_url}{separator}pageNumber={page}"
                response = requests.get(current_url, headers=headers, timeout=20)
                if response.status_code != 200: continue
                soup = BeautifulSoup(response.text, 'html.parser')
                time.sleep(1) 
            
            product_list_container = soup.find('div', id='product-list')
            if product_list_container:
                product_links = product_list_container.find_all('a', class_='product-item')
                for anchor in product_links:
                    href = anchor.get('href')
                    title = anchor.get('data-title') 
                    if href and title:
                        full_url = BASE_URL + href if not href.startswith('http') else href
                        if full_url not in [p['product_url'] for p in product_list]:
                            product_list.append({
                                'brand_name': brand_name, 
                                'product_name': title,
                                'product_url': full_url
                            })
    except Exception: pass
    return product_list


# ==============================================================================
# II. FUNGSI UTAMA SCRAPER (Diubah)
# ==============================================================================

def scrape_dermstore_data(product_url, brand_name_from_category):
    """
    Mengambil semua data produk, memecahnya menjadi BARIS PER SKU/VARIAN,
    dan mengembalikan list of dictionaries (satu dict per SKU).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    # Inisialisasi data utama (data statis per halaman)
    base_data = {
        'URL_Product_Page': product_url,
        'Brand_from_Category': brand_name_from_category, # Brand yang didapat dari halaman kategori
        'Name': 'N/A',
        'Price_Main': 'N/A',
        'RatingValue': 'N/A',
        'ReviewCount': 'N/A',
        'Overview': 'N/A',
        'Ingredients': 'N/A',
        'Brand_from_Page': 'N/A', # Brand yang didapat dari halaman produk
    }

    scraped_skus = [] # List untuk menyimpan semua dictionary SKU

    try:
        response = requests.get(product_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"  [ERROR] Gagal membuka halaman. Code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        # 1. Ekstraksi Data Statis (Rating, Overview, Ingredients, Brand)
        base_data['RatingValue'], base_data['ReviewCount'] = extract_rating_and_reviews(soup)
        base_data['Overview'] = extract_product_overview_from_html(soup)
        base_data['Ingredients'] = extract_ingredients_from_html(soup)
        base_data['Brand_from_Page'] = extract_brand_from_html(soup)
        
        name_tag = soup.find('h1', class_='product-title')
        base_data['Name'] = name_tag.get_text(strip=True) if name_tag else 'N/A'
        
        price_tag = soup.find('p', class_='product-price') 
        if not price_tag:
             price_tag = soup.find('span', {'data-component': 'Price'})
        base_data['Price_Main'] = price_tag.get_text(strip=True) if price_tag else 'N/A'


        # 2. Cari Data Variasi (JSON)
        variation_data = None
        for script in scripts:
            if script.string and "const variationData =" in script.string:
                match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if match:
                    try:
                        variation_data = json.loads(match.group(1))
                        break
                    except json.JSONDecodeError:
                        pass
        
        
        # 3. Proses Variasi (Menciptakan BARIS PER SKU)
        if variation_data:
            for item in variation_data:
                sku_entry = base_data.copy() # Duplikasi data statis
                
                # Data SKU/Variasi
                sku_entry['SKU'] = item.get('sku', 'N/A')
                sku_entry['Product_Title_SKU'] = item.get('name', base_data['Name']) # Nama produk per SKU
                sku_entry['Status'] = "Ready" if item.get('inStock') else "Kosong"

                try:
                    sku_entry['Price_SKU'] = item['price']['price']['displayValue']
                except (KeyError, TypeError):
                    sku_entry['Price_SKU'] = 'N/A'
                
                try:
                    # Ambil title dari pilihan (choices) atau title utama item
                    color_name = item['choices'][0]['title']
                except (KeyError, IndexError, TypeError):
                    color_name = item.get('title', 'Unknown')
                
                # Info Subscription
                subscription_info = ""
                subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
                if subscription_contract:
                    initial_price = subscription_contract['initialPrice']['price']['displayValue']
                    freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
                    subscription_info = f" (Subs: {initial_price}/{freq})"

                sku_entry['Varian/Warna'] = color_name + subscription_info
                
                # Ekstraksi Image URL
                image_url = "N/A"
                try:
                    image_url = item['images'][0]['original']
                except (KeyError, IndexError, TypeError):
                    pass 
                sku_entry['ImageURL'] = image_url
                
                # Hapus kolom yang tidak relevan untuk output akhir
                del sku_entry['Brand_from_Category']
                del sku_entry['Price_Main']
                
                scraped_skus.append(sku_entry)
        
        # Jika tidak ada variationData (produk tanpa varian)
        if not scraped_skus:
             sku_entry = base_data.copy()
             sku_entry['SKU'] = 'N/A (No Varian)'
             sku_entry['Product_Title_SKU'] = base_data['Name']
             sku_entry['Status'] = 'N/A'
             sku_entry['Price_SKU'] = base_data['Price_Main']
             sku_entry['Varian/Warna'] = 'N/A'
             sku_entry['ImageURL'] = 'N/A'
             del sku_entry['Brand_from_Category']
             del sku_entry['Price_Main']
             scraped_skus.append(sku_entry)


        return scraped_skus

    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat scraping {product_url}: {e}")
        return []

# ==============================================================================
# III. FUNGSI KOORDINATOR UTAMA (Diubah untuk menangani List of SKUs)
# ==============================================================================

def master_scraper(limit_brands=3, limit_products_per_brand=3):
    """
    Mengkoordinasikan proses scraping, membatasi, dan menyimpan hasilnya ke CSV.
    Menggabungkan semua SKU dari semua produk ke dalam satu list.
    """
    brands = search_brand_categories(BRAND_PAGE_URL)
    
    if not brands:
        print("[FATAL] Tidak ada kategori merek yang ditemukan. Proses dihentikan.")
        return

    print("\n" + "="*80)
    print(f"## 2. 🚀 Memulai Scraping Produk ({limit_brands} Merek Pertama) & Detail")
    print("="*80)
    
    brands_to_process = brands[:limit_brands] 
    final_scraped_data = [] # LIST FINAL SEMUA SKU
    
    for i, brand in enumerate(brands_to_process):
        print(f"\n--- Memproses Brand {i+1}/{len(brands_to_process)}: {brand['brand_name']} ---")
        
        products_urls = search_products_in_category(brand['category_url'], brand['brand_name'])
        
        products_to_scrape = products_urls[:limit_products_per_brand]
        
        print(f"  [INFO] Melanjutkan scrape detail untuk {len(products_to_scrape)} dari {len(products_urls)} produk yang ditemukan...")
        
        for j, product_item in enumerate(products_to_scrape):
            print(f"    > Mengambil detail {j+1}/{len(products_to_scrape)}: {product_item['product_name'][:40]}...")
            
            # Panggil scraper yang mengembalikan LIST SKU
            list_of_skus = scrape_dermstore_data(product_item['product_url'], product_item['brand_name'])
            
            # Gabungkan list SKU ke list final
            if list_of_skus:
                final_scraped_data.extend(list_of_skus)
                
            time.sleep(0.5) 

        time.sleep(2)

    # Panggil fungsi penyimpanan CSV
    save_to_csv(final_scraped_data, OUTPUT_CSV_FILE)
    
    print("\n" + "="*100)
    print(f"## 3. ✅ RINGKASAN AKHIR: {len(final_scraped_data)} Baris SKU Detail Siap Diperiksa")
    print("="*100)


# ==============================================================================
# IV. FUNGSI PENYIMPANAN CSV (Diubah)
# ==============================================================================

def save_to_csv(data_list, filename):
    """
    Menyimpan list of dictionaries (satu baris per SKU) ke dalam file CSV.
    """
    if not data_list:
        print("[CSV] Tidak ada data untuk disimpan.")
        return

    # Urutan kolom yang sesuai dengan permintaan Anda
    fieldnames = ['SKU', 'Product_Title_SKU', 'Status', 'Price_SKU', 'Varian/Warna', 
                  'ImageURL', 'URL_Product_Page', 'Brand_from_Page', 
                  'RatingValue', 'ReviewCount', 'Ingredients', 'Overview']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Gunakan extrasaction='ignore' untuk mengabaikan kunci yang tidak ada di fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            writer.writeheader()
            writer.writerows(data_list)
        
        print(f"\n[SUCCESS] Data berhasil disimpan ke: {os.path.abspath(filename)}")
        print(f"Total {len(data_list)} baris data SKU ditulis.")
        
    except Exception as e:
        print(f"\n[ERROR] Gagal menyimpan data ke CSV: {e}")


if __name__ == "__main__":
    # Menguji dengan 3 brand pertama dan 3 produk per brand
    print("--- MEMULAI SCRAPING UJI COBA PER SKU KE CSV ---")
    master_scraper(limit_brands=3, limit_products_per_brand=3)