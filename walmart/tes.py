import requests
import json
from bs4 import BeautifulSoup

def ekstrak_json_next_data(url):
    """
    Mengambil konten HTML dari URL, mencari tag <script id="__NEXT_DATA__">,
    dan mengembalikan konten JSON di dalamnya.
    
    Catatan: Header telah diperkuat untuk mengatasi masalah deteksi anti-bot.
    """
    try:
        print(f"Mengambil data dari: {url}")
        
        # Menggunakan header yang sangat menyerupai browser Chrome asli
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        
        # Mem-parsing HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari tag <script> hanya berdasarkan ID (metode yang paling umum)
        # BeautifulSoup akan menemukan tag tersebut baik dengan atau tanpa atribut type="application/json"
        script_tag = soup.find('script', id='__NEXT_DATA__')
        print(script_tag)
        
        if script_tag and script_tag.string:
            # Mengekstrak teks dan mem-parsing JSON
            json_text = script_tag.string
            data_dict = json.loads(json_text)
            
            print("\n✅ Data JSON berhasil diekstrak dan diproses menjadi dictionary Python.")
            return data_dict
        else:
            print(f"\n❌ Tag <script id='__NEXT_DATA__'> tidak ditemukan di halaman.")
            print("Periksa kembali apakah situs tersebut menampilkan konten JSON ini kepada skrip.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Terjadi kesalahan saat mengambil URL (Periksa koneksi atau pemblokiran IP): {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"\n❌ Terjadi kesalahan saat mem-parsing JSON (Konten mungkin tidak valid JSON): {e}")
        return None

# URL produk yang Anda berikan
target_url = "https://www.walmart.com/ip/DUAIU-Makeup-Brushes-Set-18pcs-Professional-Makeup-Brushes-2-Powder-Puff-Travel-Bag-Premium-Synthetic-Foundation-Powder-Blush-Blending-Face-Brush-Kit/5043608455"

# Jalankan fungsi
data = ekstrak_json_next_data(target_url)

# Menampilkan informasi kunci
if data:
    print("\n" + "="*50)
    print("Contoh Data Kunci yang Diekstrak:")
    print("="*50)
    
    try:
        # Menarik informasi Nama Produk
        product_name = data['props']['pageProps']['initialData']['data']['product']['displayName']
        print(f"Nama Produk: {product_name}")
    except KeyError as e:
        print(f"Gagal menemukan kunci data: {e}. Struktur JSON mungkin berubah.")
        
    print("="*50)