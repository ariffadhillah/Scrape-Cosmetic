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

file_input= 'url_cleaned.csv'

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