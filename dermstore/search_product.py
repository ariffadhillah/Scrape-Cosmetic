import requests
from bs4 import BeautifulSoup
import re
import math
import time
# from search_product import search_brand_categories

# Base URL untuk Dermstore (digunakan untuk membuat URL absolut)
BASE_URL = "https://www.dermstore.com"
# Asumsi: Jumlah produk per halaman adalah 36 (standar PLP Dermstore)
PRODUCTS_PER_PAGE = 36 

def get_total_products(soup):
    """
    Mencari total jumlah produk di halaman kategori untuk menghitung total halaman
    berdasarkan struktur HTML yang ditemukan.
    """
    # 1. Cari elemen <span> yang spesifik: <span class="total-products">
    total_products_span = soup.find('span', class_='total-products') 
    
    if total_products_span:
        try:
            # Ekstrak teks (angka) dari span tersebut dan konversi ke integer
            total = int(total_products_span.get_text(strip=True))
            return total
        except ValueError:
            print("[INFO] Ditemukan tag 'total-products', tetapi nilainya bukan angka valid.")
    
    # 2. Fallback (Jika struktur berubah atau tidak ditemukan)
    # Mencoba mencari elemen yang mengandung teks 'results' dan angka besar di dekatnya.
    try:
        # Perbaikan: Menggunakan 'string' alih-alih 'text'
        text_match = soup.find(string=re.compile(r'\d+ results'))
        if text_match:
             match = re.search(r'of\s*(\d+)\s*results', text_match.strip())
             if match:
                 return int(match.group(1))
    except Exception:
         pass

    print("[INFO] Tidak dapat menemukan total jumlah produk. Mengasumsikan 1 halaman penuh.")
    return PRODUCTS_PER_PAGE # Mengasumsikan setidaknya satu halaman penuh.


def search_products_in_category(category_url):
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
        
        # Hitung total produk dan halaman
        total_products = get_total_products(soup)
        total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
        
        if total_pages == 0:
            total_pages = 1 # Minimal 1 halaman
            
        print(f"[INFO] Ditemukan {total_products} produk total. Akan discrape {total_pages} halaman.")
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Terjadi kesalahan koneksi saat mengambil halaman pertama: {e}")
        return product_list
    
    # --- 2. Loop Semua Halaman ---
    for page in range(1, total_pages + 1):
        # Buat URL dengan parameter pageNumber
        if page == 1:
            current_url = category_url
        else:
            # Menangani penambahan parameter pada URL yang mungkin sudah memiliki parameter
            separator = '&' if '?' in category_url else '?'
            current_url = f"{category_url}{separator}pageNumber={page}"
                
        print(f"  > Scraping Halaman {page}/{total_pages} dari: {current_url}")
        
        try:
            # Untuk halaman 2 dan seterusnya, lakukan request baru
            if page > 1:
                response = requests.get(current_url, headers=headers, timeout=20)
                if response.status_code != 200:
                    print(f"    [WARNING] Gagal mengambil Halaman {page}. Status code: {response.status_code}. Melanjutkan ke halaman berikutnya.")
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                time.sleep(1) # Jeda untuk menghindari blokir IP (Ethical Scraping)
            
            # Ekstraksi produk dari halaman saat ini (soup sudah terisi)
            product_list_container = soup.find('div', id='product-list')
            
            if product_list_container:
                # Class link produk yang benar adalah 'product-item'
                product_links = product_list_container.find_all('a', class_='product-item')

                for anchor in product_links:
                    href = anchor.get('href')
                    title = anchor.get('data-title') 

                    if href and title:
                        if not href.startswith('http'):
                            full_url = BASE_URL + href
                        else:
                            full_url = href
                            
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

if __name__ == "__main__":
    
    # URL UJI COBA (Augustinus Bader)
    category_test_url = "https://www.dermstore.com/c/brands/augustinus-bader/"
    
    products = search_products_in_category(category_test_url)
    
    print("\n" + "="*80)
    print(f"## 📦 Hasil Ekstraksi Produk dari Kategori (Termasuk Pagination)")
    print("="*80)
    
    if products:
        print(f"Total {len(products)} produk unik ditemukan.")
        print("-" * 80)
        print(f"{'No.':<5} | {'Product Name':<50} | {'Product URL'}")
        print("-" * 80)
        
        # Tampilkan 5 produk pertama dan 5 produk terakhir
        display_products = products[:5]
        if len(products) > 10:
             display_products.extend(products[-5:])
        
        for i, product in enumerate(display_products):
            # Cek apakah kita sudah menampilkan 5 produk pertama dan akan melompat
            if i == 5 and len(products) > 10:
                print("... (Produk di tengah dihilangkan)")
            
            # Jika nama terlalu panjang, potong
            display_name = (product['product_name'][:47] + '...') if len(product['product_name']) > 50 else product['product_name']
            
            # Mencari indeks produk dari daftar asli
            original_index = products.index(product) + 1
            
            print(f"{original_index:<5} | {display_name:<50} | {product['product_url']}")
        
    else:
        print("Tidak ada produk yang berhasil diekstrak.")
    
    print("="*80)