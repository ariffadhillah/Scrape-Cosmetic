import requests
import json
from bs4 import BeautifulSoup
import os

def ekstrak_json_next_data(url):
    """
    Mengambil konten HTML dari URL, mencari tag <script id="__NEXT_DATA__">,
    dan mengembalikan konten JSON di dalamnya.
    """
    try:
        print(f"Mengambil data dari: {url}")
        
        # Header untuk mengatasi masalah deteksi anti-bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari tag <script> berdasarkan ID
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if script_tag and script_tag.string:
            json_text = script_tag.string
            data_dict = json.loads(json_text)
            
            print("✅ Data JSON berhasil diekstrak.")
            return data_dict
        else:
            print("❌ Tag <script id='__NEXT_DATA__'> tidak ditemukan.")
            return None

    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
        return None

def simpan_data_ke_json(data, nama_file="upc-new.json"):
    """
    Menyimpan dictionary Python ke dalam file JSON.
    """
    try:
        with open(nama_file, 'w', encoding='utf-8') as f:
            # Menggunakan indent=4 agar file JSON mudah dibaca (pretty print)
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ Data berhasil disimpan ke file: {os.path.abspath(nama_file)}")
        print(f"Ukuran file yang disimpan: {os.path.getsize(nama_file) / 1024:.2f} KB")
    except Exception as e:
        print(f"❌ Gagal menyimpan data ke file JSON: {e}")

# --- Proses Utama ---

# target_url = "https://www.walmart.com/ip/Rimmel-Just-Let-it-Go-Gentle-Eye-Makeup-Remover-3-4-fl-oz/43286061"
target_url = "https://www.walmart.com/ip/3-pack-Pedigree-Chopped-Ground-Dinner-Chicken-Rice-Dinner-Adult-Soft-Wet-Dog-Food-13-2-Oz-Single-Can/5724279326"

# 1. Ekstrak data JSON dari URL
data = ekstrak_json_next_data(target_url)

if data:
    # 2. Simpan data yang diekstrak ke file JSON
    # simpan_data_ke_json(data)
    
    # Menampilkan contoh data setelah disimpan
    print("\n" + "="*50)
    print("Contoh Data Kunci untuk Verifikasi:")
    print("="*50)
    try:
        # Menarik Nama Produk
        product_name = data['props']['pageProps']['initialData']['data']['idml']['productHighlights']
        print(f"Nama Produk: {product_name}")
    except KeyError:
        print("Gagal menampilkan nama produk.")
    print("="*50)