import requests
import json

def ambil_data_dari_api_nordstrom(product_id):
    """
    Mengambil data produk langsung dari endpoint API Nordstrom.
    """
    # Endpoint API yang paling mungkin untuk detail produk
    api_url = f"https://apigateway.nordstrom.com/product/api/v1/products/{product_id}?format=json&market=US&channel=WEB"
    
    # Headers yang wajib ada
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }
    
    print(f"-> Mengakses API endpoint: {api_url}")
    
    try:
        # 1. Mengirim permintaan GET ke API
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status() # Cek error HTTP
        
        # 2. Parsing respons JSON
        data = response.json()
        
        # Cek apakah data utama produk ada
        if data and 'id' in data and data['id'] == product_id:
            print("-> BERHASIL! Data produk JSON berhasil diambil dari API.")
            return data
        else:
            print("-> GAGAL! Respons API valid, tetapi tidak mengandung data produk yang diharapkan.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"-> Error saat mengakses API: {e}")
        return None
    except json.JSONDecodeError:
        print("-> Error: Respons API bukan format JSON yang valid.")
        return None

def tampilkan_info_produk_api(data):
    """
    Mencetak data kunci dari respons API produk.
    """
    if not data:
        return

    # Ekstraksi data dari struktur API yang kompleks
    name = data.get('productTitle', 'N/A')
    brand_name = data.get('brand', {}).get('name', 'N/A')
    description = data.get('productDescription', 'N/A')
    
    # Mencari harga dari daftar harga yang tersedia
    price_info = 'N/A'
    for price_obj in data.get('prices', []):
        if price_obj.get('type') == 'CURRENT':
            price_info = f"{price_obj.get('currencyCode', 'USD')} {price_obj.get('price', 'N/A')}"
            break

    # Mencari URL gambar utama
    image_url = 'N/A'
    for image_obj in data.get('media', []):
        if image_obj.get('type') == 'PRIMARY':
            image_url = image_obj.get('url', 'N/A')
            break
            
    # Asumsi ketersediaan (Stok tersedia)
    availability = 'Stok Tersedia (Asumsi)'

    print("\n" + "="*50)
    print("DETAIL DATA PRODUK (EKSTRAKSI API)")
    print("="*50)
    print(f"Nama Produk: {name}")
    print(f"Merek (Brand): {brand_name}")
    print(f"Harga: {price_info}")
    print(f"Ketersediaan: {availability}")
    print("-" * 50)
    print(f"Deskripsi:\n{description[:500]}...")
    print("-" * 50)
    print(f"URL Gambar Utama: {image_url}")
    print("="*50)

# --- Eksekusi Utama ---
PRODUCT_ID = "8173197"

data_produk_api = ambil_data_dari_api_nordstrom(PRODUCT_ID)

if data_produk_api:
    tampilkan_info_produk_api(data_produk_api)
else:
    print("\nOperasi pengambilan data gagal. Coba pastikan ID produk sudah benar.")