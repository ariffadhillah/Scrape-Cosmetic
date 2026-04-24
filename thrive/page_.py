import requests
import json
from bs4 import BeautifulSoup

# --- KONFIGURASI ---
url = "https://thrivemarket.com/p/thrive-market-organic-93lean-7fat-ground-beef"

# Konfigurasi Proxy (Format: http://user:pass@host:port)
proxies = {
    'http': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
    'https': 'http://arssrhsq:x1vpi09f4v1g@191.96.254.80:6127',
}

# Headers sangat penting agar tidak terkena blokir (WAF)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

try:
    print(f"Mengakses: {url} (via Requests)...")
    
    # Melakukan request
    response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
    
    # Cek status code (200 berarti sukses)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Ambil JSON dari <script id="productSchema">
        data_schema = {}
        script_schema = soup.find('script', id='productSchema')
        if script_schema:
            data_schema = json.loads(script_schema.string)
            print("Berhasil mengambil Product Schema JSON.")

        # 2. Ambil JSON dari <script id="__NEXT_DATA__">
        data_next = {}
        script_next = soup.find('script', id='__NEXT_DATA__')
        if script_next:
            data_next = json.loads(script_next.string)
            print("Berhasil mengambil NEXT_DATA JSON.")

        # 3. Gabungkan hasil
        combined_data = {
            "source_url": url,
            "product_schema_data": data_schema,
            "next_js_internal_data": data_next
        }

        # 4. Simpan ke JSON
        filename = "gomacro_complete_requests.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=4, ensure_ascii=False)

        print(f"\n--- SELESAI ---")
        print(f"Data disimpan di: {filename}")
    else:
        print(f"Gagal mengakses halaman. Status code: {response.status_code}")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")