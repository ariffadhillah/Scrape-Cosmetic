import requests
import json
import re
from bs4 import BeautifulSoup

def scrape_dermstore_variations(url):
    # 1. Setup Request Headers
    # Penting: Menggunakan User-Agent agar tidak dianggap bot jahat oleh server
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"Sedang mengambil data dari: {url} ...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Gagal membuka halaman. Status code: {response.status_code}")
            return

        # 2. Parsing HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Mencari data di dalam tag <script>
        # Kita mencari script yang mengandung teks "const variationData ="
        scripts = soup.find_all('script')
        json_data = None

        for script in scripts:
            if script.string and "const variationData =" in script.string:
                # Menggunakan Regex untuk mengambil teks di antara [ ... ]
                # Pattern ini mencari array JSON yang dimulai setelah "variationData ="
                match = re.search(r'const variationData = (\[.*?\]);', script.string, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        json_data = json.loads(json_str)
                        break
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
        
        # 4. Menampilkan Hasil
        if json_data:
            print("\nData Berhasil Ditemukan!\n")
            print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian'}")
            print("-" * 65)

            for item in json_data:
                # Ekstraksi field yang dibutuhkan
                sku = item.get('sku')
                title = item.get('title')
                in_stock = "Ready" if item.get('inStock') else "Kosong"
                
                # Mengambil harga (menangani kemungkinan struktur harga null)
                try:
                    price = item['price']['price']['displayValue']
                except (KeyError, TypeError):
                    price = "N/A"

                
                
                # Mengambil nama warna dari choices, fallback ke title jika tidak ada
                try:
                    color_name = item['choices'][0]['title']
                except (KeyError, IndexError, TypeError):
                    color_name = item.get('title', 'Unknown')

                print(f"{sku:<10} | {title} | {in_stock:<10} | {price:<8}")
        else:
            print("Tidak dapat menemukan variabel 'variationData' di halaman tersebut.")
            # Debugging: Kadang situs menggunakan nama variabel berbeda atau memblokir request
            
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

# --- Eksekusi Script ---
target_url = "https://www.dermstore.com/p/above-us-steorra-eau-de-parfum-50ml/16895897/"
scrape_dermstore_variations(target_url)