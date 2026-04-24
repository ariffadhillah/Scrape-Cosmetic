import requests
from bs4 import BeautifulSoup
import re
import math
import time
import sys

# Tingkatkan limit rekursi untuk proses scraping yang dalam
sys.setrecursionlimit(3000)

# --- KONSTANTA GLOBAL ---
BASE_URL = "https://www.dermstore.com"
BRAND_PAGE_URL = "https://www.dermstore.com/c/brands/" 
PRODUCTS_PER_PAGE = 36 

# --- FUNGSI SEARCH KATEGORI (Dari search_kategory.py) ---

def search_brand_categories(url):
    """
    Mengambil nama brand dan URL kategori dari halaman Brands Dermstore.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"## 1. 🔍 Sedang mengambil daftar kategori dari: {url}")
    
    brand_list = []

    try:
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"[ERROR] Gagal membuka halaman Brands. Status code: {response.status_code}")
            return brand_list

        soup = BeautifulSoup(response.text, 'html.parser')
        
        main_container = soup.find('div', class_='widgets mb-6 md:mb-12 customWidgetMargin')
        if not main_container:
            main_container = soup.find('div', class_='mx-auto px-5 mt-12 container')

        if not main_container:
            print("[ERROR] Container utama daftar merek tidak ditemukan.")
            return brand_list
        
        list_items = main_container.find_all('li', class_=lambda c: c and 'w-1/2' in c)
        
        if not list_items:
            list_items = main_container.find_all('li')

        for li in list_items:
            anchor = li.find('a')
            if anchor:
                href = anchor.get('href')
                name = anchor.get_text(strip=True)
                
                if href and name:
                    full_url = BASE_URL + href if not href.startswith('http') else href
                    brand_list.append({
                        'brand_name': name,
                        'category_url': full_url
                    })

        print(f"[SUCCESS] Total {len(brand_list)} merek berhasil ditemukan.")
        return brand_list

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Terjadi kesalahan koneksi saat scraping kategori: {e}")
        return brand_list
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan tak terduga saat scraping kategori: {e}")
        return brand_list

# --- FUNGSI SEARCH PRODUK (Dari search_product.py) ---

def get_total_products(soup):
    """Mencari total jumlah produk di halaman kategori."""
    total_products_span = soup.find('span', class_='total-products') 
    
    if total_products_span:
        try:
            total = int(total_products_span.get_text(strip=True))
            return total
        except ValueError:
            pass
    
    # Fallback (perbaikan DeprecationWarning)
    try:
        text_match = soup.find(string=re.compile(r'\d+ results'))
        if text_match:
             match = re.search(r'of\s*(\d+)\s*results', text_match.strip())
             if match:
                 return int(match.group(1))
    except Exception:
         pass

    return PRODUCTS_PER_PAGE


def search_products_in_category(category_url, brand_name):
    """
    Mengambil daftar Product URL dan Nama Produk dari halaman kategori (termasuk pagination).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    product_list = []
    
    # --- 1. Ambil Halaman Pertama untuk Menghitung Total Halaman ---
    try:
        response = requests.get(category_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"  [ERROR] Gagal membuka Halaman 1 kategori '{brand_name}'. Code: {response.status_code}")
            return product_list
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        total_products = get_total_products(soup)
        total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
        
        if total_pages == 0: total_pages = 1
        
        print(f"  [INFO] Brand '{brand_name}' memiliki {total_products} produk ({total_pages} halaman).")
        
    except requests.exceptions.RequestException:
        print(f"  [ERROR] Kesalahan koneksi saat mengambil Halaman 1 '{brand_name}'.")
        return product_list
    
    # --- 2. Loop Semua Halaman ---
    for page in range(1, total_pages + 1):
        if page == 1:
            current_url = category_url
        else:
            separator = '&' if '?' in category_url else '?'
            current_url = f"{category_url}{separator}pageNumber={page}"
                
        # print(f"    > Scraping Halaman {page}/{total_pages}...") # Terlalu verbose, dinonaktifkan

        try:
            # Re-request untuk halaman > 1
            if page > 1:
                response = requests.get(current_url, headers=headers, timeout=20)
                if response.status_code != 200:
                    continue
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
                                'brand_name': brand_name, # Tambahkan nama brand di sini
                                'product_name': title,
                                'product_url': full_url
                            })
        
        except requests.exceptions.RequestException:
             # Biarkan loop terus berjalan jika ada error koneksi per halaman
             continue 
            
    return product_list

# --- FUNGSI UTAMA KOORDINATOR ---

def master_scraper():
    """
    Mengkoordinasikan proses scraping: Kategori -> Produk -> Daftar Gabungan.
    """
    all_brands_products = []
    
    # 1. Ambil semua URL Kategori Merek
    brands = search_brand_categories(BRAND_PAGE_URL)
    
    if not brands:
        print("[FATAL] Tidak ada kategori merek yang ditemukan. Proses dihentikan.")
        return

    print("\n" + "="*80)
    print("## 2. 🚀 Memulai Scraping Produk per Kategori")
    print("="*80)
    
    # Uji coba hanya pada 5 merek pertama dan 1 merek terakhir (untuk melihat pagination)
    brands_to_process = brands[:5] 
    if len(brands) > 5:
        # Tambahkan Augustinus Bader (index 7 pada run sebelumnya) atau yang banyak produk
        # Mencari brand dengan nama 'Augustinus Bader' untuk contoh pagination
        augustinus = next((b for b in brands if b['brand_name'] == 'Augustinus Bader'), None)
        if augustinus and augustinus not in brands_to_process:
             brands_to_process.append(augustinus)
        
        # Tambahkan merek terakhir
        if brands[-1] not in brands_to_process:
             brands_to_process.append(brands[-1])

    total_brands_processed = 0
    total_products_scraped = 0
    
    for i, brand in enumerate(brands_to_process):
        print(f"\n--- Memproses {i+1}/{len(brands_to_process)}: {brand['brand_name']} ({brand['category_url']}) ---")
        
        # 2. Ambil semua Produk dalam Kategori ini (dengan pagination)
        products = search_products_in_category(brand['category_url'], brand['brand_name'])
        
        # 3. Gabungkan hasil
        all_brands_products.extend(products)
        total_brands_processed += 1
        total_products_scraped += len(products)
        
        # Jeda antar kategori (penting)
        time.sleep(2) 

    # 4. Tampilkan Hasil Akhir
    print("\n" + "="*100)
    print("## 3. ✅ RINGKASAN AKHIR SCRAPING")
    print("="*100)
    print(f"Total Merek yang Diproses: {total_brands_processed}")
    print(f"Total Produk Unik yang Ditemukan: {total_products_scraped}")
    
    if all_brands_products:
        print("\n" + f"{'Brand':<25} | {'Product Name':<45} | {'Product URL'}")
        print("-" * 100)
        
        # Tampilkan 15 item pertama
        for i, item in enumerate(all_brands_products[:15]): 
            display_name = (item['product_name'][:42] + '...') if len(item['product_name']) > 45 else item['product_name']
            print(f"{item['brand_name']:<25} | {display_name:<45} | {item['product_url']}")
        
        if len(all_brands_products) > 15:
            print(f"\n... (Total {total_products_scraped} produk ditemukan).")

    print("="*100)

if __name__ == "__main__":
    master_scraper()