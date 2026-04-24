import requests
import json
import re
from bs4 import BeautifulSoup
import math
import time
import sys
import csv
import os

# Batas rekursi default Python mungkin terlalu rendah untuk beberapa operasi BeautifulSoup/JSON dalam loop besar
sys.setrecursionlimit(3000)

# --- KONSTANTA GLOBAL ---
BASE_URL = "https://www.dermstore.com"
BRAND_PAGE_URL = "https://www.dermstore.com/c/brands/" 
PRODUCTS_PER_PAGE = 36 # Jumlah produk per halaman kategori
OUTPUT_CSV_FILE = "dermstore_scraped_data_per_sku.csv" # Nama file CSV output

# ==============================================================================
# I. FUNGSI HELPER (DIPINDAHKAN DARI page_product.py)
# ==============================================================================

def extract_product_overview_from_html(soup):
    """Fallback: Mencari Product Overview dari tab HTML."""
    target_div = soup.find('div', {'id': 'product-description-0'})
    if not target_div:
        target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return 'N/A'

def extract_ingredients_from_html(soup):
    """Fallback: Mencari Ingredients dari tab HTML."""
    target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return 'N/A'

def extract_brand_from_html(soup):
    """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
    # 1. Dari Breadcrumbs
    breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
    if breadcrumb:
        brand_link = breadcrumb.find_all('li')
        if len(brand_link) > 1:
            brand_name = brand_link[-2].get_text(strip=True)
            if brand_name and brand_name.lower() != 'all brands':
                return brand_name
    
    # 2. Dari Link Brand
    brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
    if brand_link:
        return brand_link.get_text(strip=True)
    
    return 'N/A'

def extract_rating_and_reviews(soup):
    """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
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
                        rating_data = {
                            'value': aggregate_rating.get('ratingValue', 'N/A'), 
                            'count': aggregate_rating.get('reviewCount', 'N/A')
                        }
                    
                    reviews = data.get("review")
                    if reviews:
                        # Gabungkan review menjadi satu string per SKU
                        for review in reviews[:3]: 
                             review_list.append(f"Rating {review['reviewRating'].get('ratingValue', 'N/A')} by {review['author'].get('name', 'Anonymous')} on {review.get('datePublished', 'N/A')}: {review.get('reviewBody', 'No body text')[:100]}...")
                    
                    return rating_data, " | ".join(review_list)
            
            except json.JSONDecodeError:
                continue
                
    return rating_data, 'N/A'

# ==============================================================================
# II. FUNGSI PENCARIAN & CRAWLING (DIPINDAHKAN DARI master_scraper)
# ==============================================================================

def get_total_products(soup):
    """Mencari total jumlah produk di halaman kategori."""
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
    """Mengambil nama brand dan URL kategori dari halaman Brands Dermstore."""
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
    except Exception as e:
        print(f"[ERROR] Gagal mencari kategori: {e}")
        return brand_list

def search_products_in_category(category_url, brand_name):
    """Mengambil daftar Product URL dan Nama Produk dari halaman kategori (termasuk pagination)."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    product_list = []
    try:
        response = requests.get(category_url, headers=headers, timeout=20)
        if response.status_code != 200: return product_list
        soup = BeautifulSoup(response.text, 'html.parser')
        total_products = get_total_products(soup)
        total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
        if total_pages == 0: total_pages = 1
        
        # Batasi hanya 1 halaman untuk uji coba cepat
        pages_to_scrape = min(total_pages, 1) 
        
        for page in range(1, pages_to_scrape + 1):
            current_url = category_url
            if page > 1:
                separator = '&' if '?' in category_url else '?'
                current_url = f"{category_url}{separator}pageNumber={page}"
                response = requests.get(current_url, headers=headers, timeout=20)
                if response.status_code != 200: continue
                soup = BeautifulSoup(response.text, 'html.parser')
                time.sleep(1) # Jeda antar halaman
            
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
    except Exception as e:
        print(f"[ERROR] Gagal mencari produk di kategori {brand_name}: {e}")
        pass
    return product_list

# ==============================================================================
# III. FUNGSI UTAMA SCRAPER PER PRODUK (DIPINDAHKAN DARI page_product.py)
# Mengembalikan list of dictionaries (SATU BARIS PER SKU)
# ==============================================================================

def scrape_dermstore_data(product_url, brand_name_from_category):
    """
    Mengambil detail data produk, memecahnya menjadi BARIS PER SKU/VARIAN,
    dan mengembalikan list of dictionaries (satu dict per SKU).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    # Data statis per halaman
    base_data = {
        'URL_Product_Page': product_url,
        'Name_Product_Main': 'N/A', # Nama produk utama
        'Brand_from_Page': 'N/A',   # Brand dari halaman produk (Fallback/Verifikasi)
        'RatingValue': 'N/A',
        'Reviews': 'N/A',
        'Overview': 'N/A',
        'Ingredients': 'N/A',
    }

    scraped_skus = []

    try:
        response = requests.get(product_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"  [ERROR] Gagal membuka halaman. Code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        # 1. Ekstraksi Data Statis (Rating, Overview, Ingredients, Brand)
        rating_data, reviews_string = extract_rating_and_reviews(soup)
        base_data['RatingValue'] = rating_data['value']
        base_data['Reviews'] = reviews_string # String gabungan ulasan
        base_data['Overview'] = extract_product_overview_from_html(soup)
        base_data['Ingredients'] = extract_ingredients_from_html(soup)
        base_data['Brand_from_Page'] = extract_brand_from_html(soup)
        
        name_tag = soup.find('h1', class_='product-title')
        base_data['Name_Product_Main'] = name_tag.get_text(strip=True) if name_tag else 'N/A'
        
        price_tag = soup.find('p', class_='product-price') 
        if not price_tag: price_tag = soup.find('span', {'data-component': 'Price'})
        price_main = price_tag.get_text(strip=True) if price_tag else 'N/A'


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
                sku_entry['Name_Product_SKU'] = item.get('name', base_data['Name_Product_Main']) # Nama produk per SKU
                sku_entry['Status'] = "Ready" if item.get('inStock') else "Kosong"

                try:
                    sku_entry['Price_SKU'] = item['price']['price']['displayValue']
                except (KeyError, TypeError):
                    sku_entry['Price_SKU'] = price_main # Fallback ke harga utama
                
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
                
                # Hapus kolom yang tidak relevan (jika ada)
                del sku_entry['Name_Product_Main']
                
                scraped_skus.append(sku_entry)
        
        # Jika tidak ada variationData (produk tanpa varian)
        if not scraped_skus:
             sku_entry = base_data.copy()
             sku_entry['SKU'] = 'N/A (No Varian)'
             sku_entry['Name_Product_SKU'] = base_data['Name_Product_Main']
             sku_entry['Status'] = 'N/A'
             sku_entry['Price_SKU'] = price_main
             sku_entry['Varian/Warna'] = 'N/A'
             sku_entry['ImageURL'] = 'N/A'
             del sku_entry['Name_Product_Main']
             scraped_skus.append(sku_entry)


        return scraped_skus

    except Exception as e:
        # print(f"\n[ERROR] Terjadi kesalahan saat scraping {product_url}: {e}")
        return []

# ==============================================================================
# IV. FUNGSI KOORDINATOR UTAMA (master_scraper)
# ==============================================================================

def master_scraper(limit_brands=3, limit_products_per_brand=3):
    """
    Mengkoordinasikan proses crawling & scraping, membatasi, dan menyimpan hasilnya ke CSV.
    Menggabungkan semua SKU dari semua produk ke dalam satu list.
    """
    brands = search_brand_categories(BRAND_PAGE_URL)
    
    if not brands:
        print("[FATAL] Tidak ada kategori merek yang ditemukan. Proses dihentikan.")
        return

    print("\n" + "="*80)
    print(f"## 2. 🚀 Memulai Crawling Produk ({len(brands)} Merek ditemukan)")
    print(f"   (Batasan: {limit_brands} Merek Pertama, {limit_products_per_brand} Produk per Merek untuk Uji Coba)")
    print("="*80)
    
    brands_to_process = brands[:limit_brands] 
    final_scraped_data = [] # LIST FINAL SEMUA SKU
    
    for i, brand in enumerate(brands_to_process):
        print(f"\n--- Memproses Brand {i+1}/{len(brands_to_process)}: {brand['brand_name']} ---")
        
        products_urls = search_products_in_category(brand['category_url'], brand['brand_name'])
        
        products_to_scrape = products_urls[:limit_products_per_brand]
        
        print(f"  [INFO] Ditemukan total {len(products_urls)} produk. Melanjutkan scrape detail untuk {len(products_to_scrape)} produk...")
        
        for j, product_item in enumerate(products_to_scrape):
            print(f"    > Mengambil detail {j+1}/{len(products_to_scrape)}: {product_item['product_name'][:40]}...")
            
            # Panggil scraper yang mengembalikan LIST SKU
            # brand_name_from_category diberikan sebagai parameter kedua
            list_of_skus = scrape_dermstore_data(product_item['product_url'], product_item['brand_name'])
            
            # Gabungkan list SKU ke list final
            if list_of_skus:
                final_scraped_data.extend(list_of_skus)
                
            time.sleep(0.5) # Jeda antar permintaan produk

        time.sleep(2) # Jeda antar merek

    # Panggil fungsi penyimpanan CSV
    save_to_csv(final_scraped_data, OUTPUT_CSV_FILE)
    
    print("\n" + "="*100)
    print(f"## 3. ✅ RINGKASAN AKHIR: {len(final_scraped_data)} Baris SKU Detail Berhasil Disimpan")
    print("="*100)
    print(f"File CSV: {OUTPUT_CSV_FILE}")


# ==============================================================================
# V. FUNGSI PENYIMPANAN CSV
# ==============================================================================

def save_to_csv(data_list, filename):
    """
    Menyimpan list of dictionaries (satu baris per SKU) ke dalam file CSV.
    """
    if not data_list:
        print("[CSV] Tidak ada data untuk disimpan.")
        return

    # Urutan kolom yang disepakati (diperbarui sedikit untuk Price_SKU dan Brand_from_Page)
    fieldnames = ['SKU', 'Name_Product_SKU', 'Status', 'Price_SKU', 'Varian/Warna', 
                  'ImageURL', 'URL_Product_Page', 'Brand_from_Page', 
                  'RatingValue', 'Reviews', 'Ingredients', 'Overview']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            writer.writeheader()
            writer.writerows(data_list)
        
        print(f"\n[SUCCESS] Data berhasil disimpan ke: {os.path.abspath(filename)}")
        print(f"Total {len(data_list)} baris data SKU ditulis.")
        
    except Exception as e:
        print(f"\n[ERROR] Gagal menyimpan data ke CSV: {e}")


if __name__ == "__main__":
    
    # PERHATIAN: Atur limit_brands dan limit_products_per_brand untuk uji coba.
    # Ubah menjadi master_scraper(limit_brands=len(brands), limit_products_per_brand=len(products_urls)) 
    # saat Anda ingin menjalankan scraping skala penuh.
    
    print("--- MEMULAI MASTER SCRAPER: PENGUJIAN KE CSV PER SKU ---")
    master_scraper(limit_brands=3, limit_products_per_brand=3)
    
    print("\n" + "=" * 50 + " MASTER SCRAPER SELESAI " + "=" * 50)