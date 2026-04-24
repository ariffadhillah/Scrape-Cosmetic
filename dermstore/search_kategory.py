import requests
from bs4 import BeautifulSoup
import re

# URL Halaman Brands Dermstore (asumsi: ini adalah halaman yang mengandung daftar lengkap merek)
BRAND_PAGE_URL = "https://www.dermstore.com/c/brands/" 
# Catatan: Sesuaikan URL di atas jika halaman Brands Anda berbeda.

# Base URL untuk Dermstore
BASE_URL = "https://www.dermstore.com"

def search_brand_categories(url):
    """
    Mengambil nama brand dan URL kategori dari halaman Brands Dermstore.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"Sedang mengambil daftar kategori dari: {url} ...")
    
    brand_list = []

    try:
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"Gagal membuka halaman. Status code: {response.status_code}")
            return brand_list

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Cari container utama
        # Class yang Anda sebutkan 'mx-auto px-5 mt-12 container' 
        # Coba cari juga kelas lain yang lebih spesifik jika ada (seperti 'widgets' yang Anda sebutkan)
        main_container = soup.find('div', class_='widgets mb-6 md:mb-12 customWidgetMargin')
        
        # Fallback ke container umum jika yang spesifik tidak ditemukan
        if not main_container:
            main_container = soup.find('div', class_='mx-auto px-5 mt-12 container')

        if not main_container:
            print("[ERROR] Container utama daftar merek tidak ditemukan.")
            return brand_list
        
        # 2. Cari semua daftar (<ul>) di dalam container utama
        # Kita perlu mencari <a> di dalam <li>, yang berada di dalam <ul>
        # Struktur yang kita cari: <ul> <li class="..."> <a href="..."> Brand Name </a> </li> </ul>
        
        # Mencari semua <li> yang berisi link brand
        list_items = main_container.find_all('li', class_=lambda c: c and 'w-1/2' in c)
        
        if not list_items:
            # Coba pencarian yang lebih umum di dalam container
            list_items = main_container.find_all('li')

        if not list_items:
            print("[INFO] Tidak ditemukan elemen daftar merek (<li> atau <a>) di halaman.")
            return brand_list

        # 3. Iterasi dan Ekstraksi Link
        for li in list_items:
            anchor = li.find('a')
            if anchor:
                href = anchor.get('href')
                name = anchor.get_text(strip=True)
                
                if href and name:
                    # Pastikan URL adalah URL absolut (lengkap)
                    if not href.startswith('http'):
                        full_url = BASE_URL + href
                    else:
                        full_url = href
                        
                    brand_list.append({
                        'brand_name': name,
                        'category_url': full_url
                    })

        return brand_list

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Terjadi kesalahan koneksi saat scraping: {e}")
        return brand_list
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan tak terduga: {e}")
        return brand_list

if __name__ == "__main__":
    
    brands = search_brand_categories(BRAND_PAGE_URL)
    
    print("\n" + "="*80)
    print("## 🛍️ Hasil Ekstraksi Kategori Merek (Brands)")
    print("="*80)
    
    if brands:
        print(f"Total {len(brands)} merek ditemukan.")
        print("-" * 80)
        print(f"{'No.':<5} | {'Brand Name':<25} | {'Category URL'}")
        print("-" * 80)
        
        for i, brand in enumerate(brands): # Tampilkan 10 merek pertama sebagai contoh
            print(f"{i+1:<5} | {brand['brand_name']:<25} | {brand['category_url']}")
        
        # if len(brands) > 10:
        #     print(f"\n... dan {len(brands) - 10} merek lainnya.")

    else:
        print("Tidak ada merek yang berhasil diekstrak.")
    
    print("="*80)