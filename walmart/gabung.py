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
        
        # Header yang diperkuat
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        
        # Menggunakan timeout 15 detik (waspadai masalah timeout yang mungkin muncul lagi)
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

# --- Proses Utama ---

# URL produk baru Anda
target_url = "https://www.walmart.com/ip/Karseell-Collagen-Hair-Treatment-Deep-Repair-Conditioning-Argan-Oil-Collagen-Hair-Mask-Essence-for-Dry-Damaged-Hair-All-Hair-Types-3-38floz-100ml/14345268626?classType=REGULAR&athbdg=L1800&adsRedirect=true"

# 1. Ekstrak data JSON dari URL
data = ekstrak_json_next_data(target_url)

if data:
    print("\n" + "="*50)
    print("Contoh Data Kunci untuk Verifikasi:")
    print("="*50)
    try:
        # Menarik Nama Produk dari jalur yang paling umum: 
        # data['props']['pageProps']['initialData']['data']['product']['displayName']
        
        # Coba ambil nama produk dari jalur umum
        product_name = data['props']['pageProps']['initialData']['data']['product']['displayName']
        print(f"Nama Produk: {product_name}")
        
    except KeyError:
        # Jika jalur umum gagal, coba jalur lain yang mungkin ada (misalnya untuk produk tertentu)
        print("Gagal menemukan 'displayName' di jalur umum. Mencoba jalur alternatif...")
        try:
             # Coba jalur yang mungkin berisi data terstruktur lain, misalnya melalui item ID
            item_id = data['query']['itemid']
            # Data di __NEXT_DATA__ biasanya terstruktur, dan product data seharusnya ada
            print(f"Item ID yang terdeteksi: {item_id}")

            # Mencoba mendapatkan harga
            price = data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice']['price']
            print(f"Harga Produk: ${price}")

        except KeyError as e:
            print(f"Gagal menampilkan data kunci (displayName atau itemID). Kunci hilang: {e}")
            
    print("="*50)

# Jika Anda ingin menyimpan file JSON untuk analisis lebih lanjut, gunakan kode ini:
"""
def simpan_data_ke_json(data, nama_file="walmart_new_data.json"):
     try:
         with open(nama_file, 'w', encoding='utf-8') as f:
             json.dump(data, f, ensure_ascii=False, indent=4)
         print(f"\n✅ Data berhasil disimpan ke file: {os.path.abspath(nama_file)}")
     except Exception as e:
         print(f"\n❌ Gagal menyimpan data ke file JSON: {e}")
         
if data:
    simpan_data_ke_json(data)
"""