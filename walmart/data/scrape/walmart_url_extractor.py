# # # walmart_url_extractor.py

# # import requests
# # from bs4 import BeautifulSoup
# # from urllib.parse import urljoin
# # import time

# # def ekstrak_dan_filter_urls_walmart(base_url, target_id, target_class):
# #     """
# #     Mengambil konten HTML dari URL utama, mencari tautan varian, 
# #     dan mengembalikan daftar URL unik.
# #     """
# #     try:
# #         print(f"Mencoba mengambil dan menganalisis: {base_url}")
        
# #         # Header yang diperkuat
# #         headers = {
# #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
# #             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
# #             'Accept-Encoding': 'gzip, deflate, br',
# #             'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
# #         }
        
# #         # Tingkatkan timeout karena sering terjadi masalah koneksi
# #         response = requests.get(base_url, headers=headers, timeout=20) 
# #         response.raise_for_status() 
        
# #         soup = BeautifulSoup(response.text, 'html.parser')
# #         main_div = soup.find('div', id=target_id)
        
# #         if not main_div:
# #             print(f"❌ Elemen Div ID '{target_id}' TIDAK ditemukan.")
# #             return []

# #         target_div = main_div.find('div', class_=target_class)
        
# #         if not target_div:
# #             print(f"❌ Elemen Div Class '{target_class}' TIDAK ditemukan.")
# #             return []
        
# #         all_links = target_div.find_all('a', href=True)
# #         extracted_urls = set()
        
# #         for link in all_links:
# #             href = link.get('href')
# #             absolute_url = urljoin(base_url, href)
# #             extracted_urls.add(absolute_url)

# #         return list(extracted_urls)

# #     except requests.exceptions.RequestException as e:
# #         print(f"\n❌ Terjadi kesalahan saat mengambil URL utama: {e}")
# #     except Exception as e:
# #         print(f"\n❌ Terjadi kesalahan tak terduga: {e}")
        
# #     return []

# # if __name__ == '__main__':
# #     # Ini hanya akan berjalan jika file ini dieksekusi langsung
# #     base_url = "https://www.walmart.com/ip/e-l-f-Contour-Palette-Light-Medium/49952141?classType=REGULAR"
# #     target_id = "item-page-variant-group-bg-div"
# #     target_class = "dn" 

# #     urls = ekstrak_dan_filter_urls_walmart(base_url, target_id, target_class)
    
# #     if urls:
# #         print(f"\n✅ Total URL unik berhasil diekstrak: {len(urls)}")
# #         print("\nSilakan jalankan walmart_main.py untuk memproses JSON.")



# # walmart_url_extractor.py

# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import time

# # --- KONFIGURASI URL (Dipindahkan dari walmart_main.py) ---
# # Anda hanya perlu mengubah URL di sini.
# BASE_URL = "https://www.walmart.com/ip/NYX-Professional-Makeup-Buttermelt-Powder-Blush-Getting-Butta/5189630976"
# # BASE_URL = "https://www.walmart.com/ip/Dove-Body-Wash-for-Women-Nourishing-Deep-Moisture-Cleanser-All-Skin-11-oz/895057"
# # BASE_URL = "https://www.walmart.com/ip/Dove-Body-Wash-for-Women-Nourishing-Deep-Moisture-Cleanser-All-Skin-11-oz/895057?classType=VARIANT&athbdg=L1102&from=/search"
# URL_TARGET_ID = "item-page-variant-group-bg-div"
# URL_TARGET_CLASS = "dn"

# def get_config():
#     """Mengembalikan konfigurasi URL dan target element."""
#     return BASE_URL, URL_TARGET_ID, URL_TARGET_CLASS

# def ekstrak_dan_filter_urls_walmart(base_url, target_id, target_class):
#     """
#     Mengambil konten HTML dari URL utama, mencari tautan varian, 
#     dan mengembalikan daftar URL unik.
#     """
#     try:
#         print(f"Mencoba mengambil dan menganalisis: {base_url}")
        
#         # Header yang diperkuat
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
#         }
        
#         # Tingkatkan timeout karena sering terjadi masalah koneksi
#         response = requests.get(base_url, headers=headers, timeout=50) 
#         response.raise_for_status() 
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         main_div = soup.find('div', id=target_id)
        
#         if not main_div:
#             print(f"❌ Elemen Div ID '{target_id}' TIDAK ditemukan.")
#             return []

#         target_div = main_div.find('div', class_=target_class)
        
#         if not target_div:
#             print(f"❌ Elemen Div Class '{target_class}' TIDAK ditemukan.")
#             return []
        
#         all_links = target_div.find_all('a', href=True)
#         extracted_urls = set()
        
#         for link in all_links:
#             href = link.get('href')
#             absolute_url = urljoin(base_url, href)
#             extracted_urls.add(absolute_url)

#         return list(extracted_urls)

#     except requests.exceptions.RequestException as e:
#         print(f"\n❌ Terjadi kesalahan saat mengambil URL utama: {e}")
#     except Exception as e:
#         print(f"\n❌ Terjadi kesalahan tak terduga: {e}")
        
#     return []

# if __name__ == '__main__':
#     # Contoh penggunaan saat file ini dieksekusi langsung
#     base, id_target, class_target = get_config()
#     urls = ekstrak_dan_filter_urls_walmart(base, id_target, class_target)
    
#     if urls:
#         print(f"\n✅ Total URL unik berhasil diekstrak: {len(urls)}")
#         print("\nSilakan jalankan walmart_main.py untuk memproses JSON.")




# walmart_url_extractor.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import time

# --- KONFIGURASI TARGET DOM ---
URL_TARGET_ID = "item-page-variant-group-bg-div"
URL_TARGET_CLASS = "dn"

file_input="Url-Perfume for Women.csv"

def ambil_daftar_url_dari_csv(file_input):
    """Membaca daftar URL dari file CSV (kolom 'url')"""
    urls = []
    if not os.path.exists(file_input):
        print(f"❌ File {file_input} tidak ditemukan!")
        return urls

    try:
        with open(file_input, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'url' in row:
                    urls.append(row['url'])
                elif 'URL' in row: # Backup jika header huruf besar
                    urls.append(row['URL'])
    except Exception as e:
        print(f"❌ Error saat membaca CSV: {e}")
    
    return urls

def ekstrak_dan_filter_urls_walmart(base_url, target_id=URL_TARGET_ID, target_class=URL_TARGET_CLASS):
    """
    Mengambil konten HTML dari URL utama, mencari tautan varian (swatches), 
    dan mengembalikan daftar URL unik termasuk URL utama itu sendiri.
    """
    # Masukkan URL utama ke set sebagai default (agar jika tidak ada varian, produk utama tetap diproses)
    extracted_urls = {base_url} 
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        
        response = requests.get(base_url, headers=headers, timeout=30) 
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari kontainer varian
        main_div = soup.find('div', id=target_id)
        if main_div:
            target_div = main_div.find('div', class_=target_class)
            if target_div:
                all_links = target_div.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    # Bersihkan URL varian dari parameter query agar bersih
                    absolute_url = urljoin(base_url, href).split('?')[0]
                    extracted_urls.add(absolute_url)

        return list(extracted_urls)

    except Exception as e:
        print(f"   ⚠️ Gagal mengekstrak varian dari {base_url[:50]}... : {e}")
        return [base_url] # Kembalikan URL asli jika gagal cari varian

# if __name__ == '__main__':
#     # Test sederhana
#     urls_dari_csv = ambil_daftar_url_dari_csv("Lip-Makeup.csv")
#     if urls_dari_csv:
#         print(f"📂 Berhasil memuat {len(urls_dari_csv)} URL dari CSV.")
#         # Test satu URL pertama
#         test_url = urls_dari_csv[0]
#         hasil = ekstrak_dan_filter_urls_walmart(test_url)
#         print(f"✅ Varian ditemukan untuk URL pertama: {len(hasil)}")