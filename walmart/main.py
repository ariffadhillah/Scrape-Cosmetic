import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def ekstrak_dan_filter_urls_walmart(base_url, target_id, target_class):
    """
    Mengambil konten HTML, mencari div target, mengekstrak href dari 
    tag <a> di dalamnya, dan menghilangkan duplikat.
    """
    try:
        print(f"Mencoba mengambil dan menganalisis: {base_url}")
        
        # Header yang diperkuat
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')

        print("\n" + "="*70)
        print(f"Pencarian Element ID: '{target_id}' dan Class: '{target_class}'")
        print("="*70)
        
        # 1. Cari div utama berdasarkan ID
        main_div = soup.find('div', id=target_id)
        
        if not main_div:
            print(f"❌ Elemen Div ID '{target_id}' TIDAK ditemukan.")
            return []

        # 2. Cari div turunan berdasarkan class (class="dn") di dalam div utama
        target_div = main_div.find('div', class_=target_class)
        
        if not target_div:
            print(f"❌ Elemen Div Class '{target_class}' (di dalam '{target_id}') TIDAK ditemukan.")
            return []
        
        print(f"✅ Elemen Div Class '{target_class}' berhasil ditemukan.")
        
        # 3. Ekstrak semua href dari tag <a> di dalam div turunan
        all_links = target_div.find_all('a', href=True)
        
        extracted_urls = set() # Gunakan SET untuk secara otomatis menangani duplikat
        
        for link in all_links:
            href = link.get('href')
            
            # Ubah URL relatif menjadi URL absolut (misalnya: /ip/... menjadi https://www.walmart.com/ip/...)
            absolute_url = urljoin(base_url, href)
            
            # Tambahkan URL ke set. Jika sudah ada, set akan mengabaikannya (menghilangkan duplikat)
            extracted_urls.add(absolute_url)

        # 4. Tampilkan Hasil
        print(f"\n✅ Berhasil mengekstrak {len(all_links)} tautan total.")
        print(f"✅ Ditemukan {len(extracted_urls)} URL unik setelah menghilangkan duplikat.")
        print("="*70)
        
        return list(extracted_urls)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Terjadi kesalahan saat mengambil URL: {e}")
    except Exception as e:
        print(f"\n❌ Terjadi kesalahan tak terduga: {e}")
        
    return []

# URL dan target yang Anda berikan
base_url = "https://www.walmart.com/ip/NYX-Professional-Makeup-Buttermelt-Powder-Blush-Feeling-Butta/5191932158?classType=VARIANT"
target_id = "item-page-variant-group-bg-div"
target_class = "dn" # Class target adalah 'dn'

# Jalankan fungsi
unique_urls = ekstrak_dan_filter_urls_walmart(base_url, target_id, target_class)

if unique_urls:
    print("\n🔗 Daftar URL Varian Unik yang Ditemukan:")
    for i, url in enumerate(unique_urls, 1):
        print(f"{i}. {url}")