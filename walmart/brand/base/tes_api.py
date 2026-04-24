import requests
import json
from bs4 import BeautifulSoup
import os

# --- DEFINISI FUNGSI (Harus di atas) ---

def ekstrak_json_next_data(url):
    """Mengambil data JSON dari tag __NEXT_DATA__"""
    try:
        print(f"Mengambil data dari: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if script_tag and script_tag.string:
            return json.loads(script_tag.string)
        else:
            print("❌ Tag <script id='__NEXT_DATA__'> tidak ditemukan.")
            return None
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat ekstraksi: {e}")
        return None


# --- EKSEKUSI UTAMA ---

if __name__ == "__main__":
    target_url = "https://www.walmart.com/ip/Pasta-Roni-Angel-Hair-Pasta-with-Herbs-4-8oz-Box/10318341"

    # Panggil fungsi yang sudah didefinisikan di atas
    data_hasil = ekstrak_json_next_data(target_url)

    if data_hasil:
        
        # Verifikasi struktur (Walmart sering meletakkan nama produk di sini)
        try:
            # Gunakan .get() untuk menghindari KeyError jika struktur berubah
            nama_produk = data_hasil.get('props', {}).get('pageProps', {}).get('initialData', {}).get('data', {}).get('product', {}).get('name', 'Tidak diketahui')
            print(f"Hasil Verifikasi: {nama_produk}")
        except:
            print("Data berhasil disimpan, tapi gagal menampilkan preview nama produk.")