import requests
from bs4 import BeautifulSoup
import re
import math
import time
import sys
import json
import csv # <--- TAMBAHAN
import os # <--- TAMBAHAN

sys.setrecursionlimit(3000)

# --- KONSTANTA GLOBAL ---
BASE_URL = "https://www.dermstore.com"
BRAND_PAGE_URL = "https://www.dermstore.com/c/brands/" 
PRODUCTS_PER_PAGE = 36 
OUTPUT_CSV_FILE = "dermstore_scraped_data_sample.csv" # <--- NAMA FILE OUTPUT

# ==============================================================================
# I. FUNGSI HELPER (Ekstraksi Detail)
# ==============================================================================

# Helper functions for scraping product details (Simplified for Master Scraper)
def extract_product_overview_from_html(soup):
    target_div = soup.find('div', {'id': 'product-description-0'})
    if not target_div:
        target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
    return target_div.get_text(separator=' ', strip=True) if target_div else 'N/A'

def extract_ingredients_from_html(soup):
    target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    return target_div.get_text(separator=' ', strip=True) if target_div else 'N/A'

def extract_rating_and_reviews(soup):
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    rating_value = 'N/A'
    review_count = 'N/A'
    for script in json_ld_scripts:
        if script.string:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = next((item for item in data if item.get("@type") == "Product"), None)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    aggregate_rating = data.get("aggregateRating")
                    if aggregate_rating:
                        rating_value = aggregate_rating.get('ratingValue', 'N/A')
                        review_count = aggregate_rating.get('reviewCount', 'N/A')
                        return rating_value, review_count
            except json.JSONDecodeError:
                continue
    return rating_value, review_count


# ==============================================================================
# II. FUNGSI UTAMA (Crawl & Scraping)
# ==============================================================================

# ... (Fungsi search_brand_categories dan get_total_products dari master_scraper.py sebelumnya) ...

def get_total_products(soup):
    """Mencari total jumlah produk di halaman kategori."""
    total_products_span = soup.find('span', class_='total-products') 
    if total_products_span:
        try:
            return int(total_products_span.get_text(strip=True))
        except ValueError:
            pass
    try:
        text_match = soup.find(string=re.compile(r'\d+ results'))
        if text_match:
             match = re.search(r'of\s*(\d+)\s*results', text_match.strip())
             if match:
                 return int(match.group(1))
    except Exception:
         pass
    return PRODUCTS_PER_PAGE


def search_brand_categories(url):
    """Mengambil nama brand dan URL kategori dari halaman Brands Dermstore."""
    # (Kode di sini sama dengan bagian 1 master_scraper.py)
    # Dihilangkan untuk keringkasan
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
    except Exception:
        return brand_list

def search_products_in_category(category_url, brand_name):
    """Mengambil daftar Product URL dan Nama Produk dari halaman kategori (termasuk pagination)."""
    # (Kode di sini sama dengan bagian 2 master_scraper.py)
    # Dihilangkan untuk keringkasan
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
            if page == 1:
                current_url = category_url
            else:
                separator = '&' if '?' in category_url else '?'
                current_url = f"{category_url}{separator}pageNumber={page}"
                    
            if page > 1:
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
    except Exception:
        pass
    return product_list


def scrape_dermstore_data(product_url, brand_name):
    """
    Mengambil detail data (Nama, Harga, Overview, Ingredients, Rating) dari satu halaman produk.
    Mengembalikan dictionary hasil scraping.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    # Inisialisasi dictionary hasil
    data = {
        'Brand': brand_name,
        'Name': 'N/A',
        'Price': 'N/A',
        'RatingValue': 'N/A',
        'ReviewCount': 'N/A',
        'Overview': 'N/A',
        'Ingredients': 'N/A',
        'URL': product_url
    }

    try:
        response = requests.get(product_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return data
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Ekstraksi Data dari HTML Biasa / JSON-LD
        name_tag = soup.find('h1', class_='product-title')
        data['Name'] = name_tag.get_text(strip=True) if name_tag else 'N/A'
        
        price_tag = soup.find('p', class_='product-price') 
        if not price_tag:
             price_tag = soup.find('span', {'data-component': 'Price'})
        data['Price'] = price_tag.get_text(strip=True) if price_tag else 'N/A'

        data['RatingValue'], data['ReviewCount'] = extract_rating_and_reviews(soup)
        data['Overview'] = extract_product_overview_from_html(soup)
        data['Ingredients'] = extract_ingredients_from_html(soup)


        # 2. Ekstraksi Detail Lanjut dari variationData (JSON)
        # Kami hanya akan mengambil data kunci (Price/Overview/Ingredients) yang mungkin 
        # terlewat oleh ekstraksi HTML sederhana, menggunakan struktur JSON yang Anda temukan.
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and "const variationData =" in script.string:
                match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if match:
                    try:
                        variation_data = json.loads(match.group(1))
                        # Jika ada data variasi, gunakan detail dari variasi pertama sebagai data utama
                        if variation_data:
                             first_variation = variation_data[0]
                             
                             # Mengambil harga utama dari JSON jika N/A dari HTML
                             if data['Price'] == 'N/A':
                                  data['Price'] = first_variation['price']['price']['displayValue']
                             
                             # Catatan: Untuk tugas CSV ini, kita hanya akan menyimpan SKU pertama dan image URL
                             data['SKU'] = first_variation.get('sku', 'N/A')
                             data['ImageURL'] = first_variation.get('images', [{}])[0].get('original', 'N/A')
                             
                        break
                    except:
                        pass
        
        return data

    except Exception:
        return data


# ==============================================================================
# III. FUNGSI KOORDINATOR UTAMA
# ==============================================================================

def master_scraper(limit_brands=3, limit_products_per_brand=3):
    """
    Mengkoordinasikan proses scraping, membatasi, dan menyimpan hasilnya ke CSV.
    """
    brands = search_brand_categories(BRAND_PAGE_URL)
    
    if not brands:
        print("[FATAL] Tidak ada kategori merek yang ditemukan. Proses dihentikan.")
        return

    print("\n" + "="*80)
    print(f"## 2. 🚀 Memulai Scraping Produk ({limit_brands} Merek Pertama) & Detail")
    print("="*80)
    
    brands_to_process = brands[:limit_brands] 
    final_scraped_data = []
    
    for i, brand in enumerate(brands_to_process):
        print(f"\n--- Memproses Brand {i+1}/{len(brands_to_process)}: {brand['brand_name']} ---")
        
        products_urls = search_products_in_category(brand['category_url'], brand['brand_name'])
        
        products_to_scrape = products_urls[:limit_products_per_brand]
        
        print(f"  [INFO] Melanjutkan scrape detail untuk {len(products_to_scrape)} dari {len(products_urls)} produk yang ditemukan...")
        
        for j, product_item in enumerate(products_to_scrape):
            print(f"    > Mengambil detail {j+1}/{len(products_to_scrape)}: {product_item['product_name'][:40]}...")
            
            detail = scrape_dermstore_data(product_item['product_url'], product_item['brand_name'])
            
            if detail:
                final_scraped_data.append(detail)
                
            time.sleep(0.5) 

        time.sleep(2)

    # Panggil fungsi penyimpanan CSV
    save_to_csv(final_scraped_data, OUTPUT_CSV_FILE)
    
    print("\n" + "="*100)
    print(f"## 3. ✅ RINGKASAN AKHIR: {len(final_scraped_data)} Detail Produk Siap Diperiksa")
    print("="*100)


# ==============================================================================
# IV. FUNGSI PENYIMPANAN CSV
# ==============================================================================

def save_to_csv(data_list, filename):
    """
    Menyimpan list of dictionaries ke dalam file CSV.
    """
    if not data_list:
        print("[CSV] Tidak ada data untuk disimpan.")
        return

    # Pastikan 'SKU' dan 'ImageURL' ada di header
    fieldnames = ['Brand', 'Name', 'SKU', 'Price', 'RatingValue', 'ReviewCount', 
                  'Overview', 'Ingredients', 'ImageURL', 'URL']
    
    try:
        # Gunakan 'w' (write) untuk membuat file baru
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            writer.writeheader()
            writer.writerows(data_list)
        
        print(f"\n[SUCCESS] Data berhasil disimpan ke: {os.path.abspath(filename)}")
        print(f"Total {len(data_list)} baris data ditulis.")
        
    except Exception as e:
        print(f"\n[ERROR] Gagal menyimpan data ke CSV: {e}")


if __name__ == "__main__":
    # Menguji dengan 3 brand pertama dan 3 produk per brand
    print("--- MEMULAI SCRAPING UJI COBA KE CSV ---")
    master_scraper(limit_brands=3, limit_products_per_brand=3)