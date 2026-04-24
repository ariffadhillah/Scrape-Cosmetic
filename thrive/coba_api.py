# import requests
# import json
# import urllib3
# from datetime import datetime

# # Menghilangkan peringatan SSL
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# # 1. Konfigurasi Proxy
# proxy_host = "191.96.254.80"
# proxy_port = "6127"
# proxy_user = "arssrhsq"
# proxy_pass = "x1vpi09f4v1g"

# proxies = {
#     "http": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
#     "https": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
# }

# # 2. URL & Parameter
# url = "https://thrivemarket.com/api/v1/products"
# params = {
#     "filter[categories]": "41640",
#     "filter[category_url_key]": "poultry",
#     "cur_page": "1",
#     "page_size": "60",
#     "multifilter": "1",
#     "display_mode": "grid",
#     "page_view_id": "7b9ed97f-e72c-44fc-a334-28e6de78320e",
#     "page_type": "category"
# }

# # 3. Headers (Gunakan token terbaru Anda)
# headers = {
#     'accept': 'application/json, text/plain, */*',
#     'accept-language': 'en-US,en;q=0.9',
#     'referer': 'https://thrivemarket.com/c/poultry',
#     'reqsource': 'web',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'x-aws-waf-token': '938569a1-bc70-42b7-9fd6-8e8ef4d7c36e:EwoA7qF6EulQAAAA:B2sQjIgTWDUUa/MJRAz7VhTPZdvJCXhwzD1lkeXdfwHKNqiAdS3ncmyN3tQBQcf9Ycu4cofPitvVSNhBVySsJJ9UYx04DRXjZmwfgJDXWFDAi1aC2AEGBscVADKAi7MU+zV7T94nApQzTa/+2eRGj8DLdcYMG9jjvUFjP0gPIW+Zm0xRWIWhK4i1GqxKPGXx778cjmP+KfcsyFZhFVNNZ2CYZLYI0D5jUJd1f9xeEcLjiakWJjQTtCO0zLtTTDF/apwsJPikwQ==',
#     'cookie': 'frontend=b8eded958d95116b62670e5f9f588488; aws-waf-token=938569a1-bc70-42b7-9fd6-8e8ef4d7c36e:EwoA7qF6EulQAAAA:B2sQjIgTWDUUa/MJRAz7VhTPZdvJCXhwzD1lkeXdfwHKNqiAdS3ncmyN3tQBQcf9Ycu4cofPitvVSNhBVySsJJ9UYx04DRXjZmwfgJDXWFDAi1aC2AEGBscVADKAi7MU+zV7T94nApQzTa/+2eRGj8DLdcYMG9jjvUFjP0gPIW+Zm0xRWIWhK4i1GqxKPGXx778cjmP+KfcsyFZhFVNNZ2CYZLYI0D5jUJd1f9xeEcLjiakWJjQTtCO0zLtTTDF/apwsJPikwQ=='
# }

# try:
#     print("Sedang mengambil data...")
#     response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=30, verify=False)
    
#     if response.status_code == 200:
#         data = response.json()
        
#         # Nama file dengan timestamp agar tidak tertukar
#         filename = f"thrive_beef_data.json"
        
#         # Menyimpan ke file
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)
            
#         print(f"--- BERHASIL ---")
#         print(f"Data disimpan ke: {filename}")
        
#         # Cek jumlah produk di dalam JSON (berdasarkan struktur umum Thrive)
#         products = data.get('data', {}).get('products', [])
#         print(f"Jumlah produk ditemukan: {len(products)}")
        
#     else:
#         print(f"Gagal! Status Code: {response.status_code}")
#         print(response.text)

# except Exception as e:
#     print(f"Error: {e}")


import requests
import json
import urllib3

# Menghilangkan peringatan SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KONFIGURASI PROXY ---
proxy_host = "191.96.254.80"
proxy_port = "6127"
proxy_user = "arssrhsq"
proxy_pass = "x1vpi09f4v1g"

proxies = {
    "http": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
    "https": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
}

# --- KONFIGURASI API (POULTRY) ---
url = "https://thrivemarket.com/api/v1/products"

# Menggunakan parameter dari URL poultry yang Anda berikan
params = {
    "filter[categories]": "41638", # ID untuk Poultry
    "filter[category_url_key]": "poultry",
    "cur_page": "1",
    "page_size": "60",
    "multifilter": "1",
    "display_mode": "grid",
    "page_view_id": "7b9ed97f-e72c-44fc-a334-28e6de78320e",
    "page_type": "category"
}

# --- HEADERS ---
# Pastikan aws-waf-token masih fresh (diambil dari browser jika perlu)
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://thrivemarket.com/c/poultry',
    'reqsource': 'web',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'x-aws-waf-token': '938569a1-bc70-42b7-9fd6-8e8ef4d7c36e:EwoA7qF6EulQAAAA:B2sQjIgTWDUUa/MJRAz7VhTPZdvJCXhwzD1lkeXdfwHKNqiAdS3ncmyN3tQBQcf9Ycu4cofPitvVSNhBVySsJJ9UYx04DRXjZmwfgJDXWFDAi1aC2AEGBscVADKAi7MU+zV7T94nApQzTa/+2eRGj8DLdcYMG9jjvUFjP0gPIW+Zm0xRWIWhK4i1GqxKPGXx778cjmP+KfcsyFZhFVNNZ2CYZLYI0D5jUJd1f9xeEcLjiakWJjQTtCO0zLtTTDF/apwsJPikwQ==',
    'cookie': 'frontend=b8eded958d95116b62670e5f9f588488; aws-waf-token=938569a1-bc70-42b7-9fd6-8e8ef4d7c36e:EwoA7qF6EulQAAAA:B2sQjIgTWDUUa/MJRAz7VhTPZdvJCXhwzD1lkeXdfwHKNqiAdS3ncmyN3tQBQcf9Ycu4cofPitvVSNhBVySsJJ9UYx04DRXjZmwfgJDXWFDAi1aC2AEGBscVADKAi7MU+zV7T94nApQzTa/+2eRGj8DLdcYMG9jjvUFjP0gPIW+Zm0xRWIWhK4i1GqxKPGXx778cjmP+KfcsyFZhFVNNZ2CYZLYI0D5jUJd1f9xeEcLjiakWJjQTtCO0zLtTTDF/apwsJPikwQ=='
}

try:
    print(f"Mengambil data untuk kategori: {params['filter[category_url_key]']}...")
    response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=30, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        
        # Simpan dengan nama file yang sesuai kategori
        filename = f"thrive_{params['filter[category_url_key]']}_page1.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"--- BERHASIL ---")
        print(f"File disimpan: {filename}")
        
        # Verifikasi jumlah produk
        products = data.get('data', {}).get('products', [])
        print(f"Jumlah produk ditemukan: {len(products)}")
        
    else:
        print(f"Gagal! Status Code: {response.status_code}")
        print("Pesan Error:", response.text[:200]) # Print sedikit pesan error jika ada

except Exception as e:
    print(f"Terjadi error: {e}")