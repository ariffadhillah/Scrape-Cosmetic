# walmart_category_scraper.py

import requests
import json
from bs4 import BeautifulSoup
import time
import csv



HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/143.0.0.0 Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;'
        'q=0.9,image/webp,image/apng,*/*;q=0.8'
    ),
    'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
}


def ambil_semua_url_produk_kategori(category_url):
    """
    Mengambil daftar URL produk dari JSON-LD (ItemList) di halaman kategori Walmart
    """
    print(f"\n🔎 Memindai halaman kategori:")
    print(category_url)

    try:
        response = requests.get(category_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        product_urls = set()

        # Cari semua JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)

                # Kadang berupa list
                if isinstance(data, list):
                    for item in data:
                        _extract_itemlist(item, product_urls)
                else:
                    _extract_itemlist(data, product_urls)

            except (json.JSONDecodeError, TypeError):
                continue

        print(f"\n✅ Total URL produk ditemukan: {len(product_urls)}")
        return list(product_urls)

    except Exception as e:
        print(f"❌ Error saat scanning kategori: {e}")
        return []


def _extract_itemlist(data, product_urls):
    """
    Helper internal untuk ekstrak ItemList
    """
    if not isinstance(data, dict):
        return

    # Format umum Walmart
    main_entity = data.get('mainEntity')
    if not isinstance(main_entity, dict):
        return

    item_list = main_entity.get('itemListElement')
    if not isinstance(item_list, list):
        return

    for item in item_list:
        url = item.get('url')
        if url:
            clean_url = url.split('?')[0]
            # print(clean_url)
            product_urls.add(clean_url)

save_file = 'Url-Cologne for Men.csv'

if __name__ == "__main__":
    # URL Dasar (Base URL) tanpa parameter page
    BASE_URL = "https://www.walmart.com/browse/beauty/cologne-for-men/1085666_133225_6873232"
    # https://www.walmart.com/browse/beauty/cologne-for-men/1085666_133225_6873232?povid=Beauty_NUPs_mensFragranceByBrand_Shopallfragrance&seo=beauty&seo=cologne-for-men&seo=1085666_133225_6873232&page=2&affinityOverride=default
    PARAMS = "povid=Beauty_NUPs_mensFragranceByBrand_Shopallfragrance&seo=beauty&seo=cologne-for-men&seo=1085666_133225_6873232"
    
    semua_produk = set()
    MAX_PAGES = 25

    for page_num in range(1, MAX_PAGES + 1):
        # Membuat URL dinamis untuk setiap halaman
        # Halaman 1 biasanya bisa diakses dengan page=1
        page_url = f"{BASE_URL}?{PARAMS}&page={page_num}"
        
        print(f"\n🚀 MEMPROSES HALAMAN {page_num} DARI {MAX_PAGES}")
        
        # Panggil fungsi scraper yang sudah Anda buat berhasil tadi
        urls = ambil_semua_url_produk_kategori(page_url)

        if not urls:
            print(f"⚠️ Peringatan: Tidak ditemukan produk di halaman {page_num}. Berhenti atau lanjut?")
            # Jika ingin berhenti saat halaman kosong, aktifkan 'break'
            # break 
        
        semua_produk.update(urls)

        # Jeda waktu agar tidak diblokir (Sangat disarankan minimal 5-10 detik)
        print(f"⏳ Jeda keamanan... (Total terkumpul: {len(semua_produk)} URL)")
        time.sleep(10)

    print(f"\n🏁 SELESAI!")
    print(f"TOTAL SELURUH PRODUK UNIK DARI {MAX_PAGES} HALAMAN: {len(semua_produk)}")

    # Simpan hasil ke file teks agar tidak hilang
    with open(save_file, "w") as f:
        for url in semua_produk:
            f.write(url + "\n")
    print(f"💾 Semua URL telah disimpan ke '{save_file}'")