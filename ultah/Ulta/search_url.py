import requests
import json
import math
import urllib.parse
import time 
from queri import cari


# Helper untuk Ekstraksi URL
def extract_urls(data_content):
    """
    Ekstrak URL produk dari dictionary konten Ulta (data.Page.content).
    """
    urls_on_page = set()
    
    if not isinstance(data_content, dict):
        return []
    
    # 1. Cek langsung di data.Page.content.items
    if "items" in data_content:
        for item in data_content["items"]:
            try:
                u = item.get("action", {}).get("url") 
                if u:
                    final_url = u
                    urls_on_page.add(final_url)
            except:
                continue
    
    # 2. Cek di dalam 'modules'
    if "modules" in data_content:
        for mod in data_content["modules"]:
            urls_on_page.update(extract_urls(mod))
            
    return list(urls_on_page)

def get_all_urls():
    
    # --- Parameter yang Anda Identifikasi Sukses ---
    SEARCH_TERM = cari()
    BASE_PATH = f"/shop/{SEARCH_TERM}"
    STATIC_PARAMS = "&gti=eb9ae70c-311f-41dd-be0b-149654cd6d19&loginStatus=anonymous&retailerVisitorId=20d40221-124b-4304-a433-c63d766b8479&breakpoint=XL"
    CONTENT_ID = "cb7c0efb-8772-4abc-9be0-4dfaf1b625ee" 
    
    # 432 + 72
    # Template Headers
    headers_template = {
        'User-Agent': 'Mozilla/5.0',
        'content-type': 'application/json',
        'apollographql-client-name': 'ulta-graph',
        'x-ulta-dxl-query-id': 'NonCachedPage',
        'x-ulta-graph-type': 'query',
        'x-ulta-graph-sub-type': 'noncachedpage',
        'x-ulta-graph-module-name': 'ProductListingResults',
        'x-ulta-client-locale': 'en-US',
        'x-ulta-client-country': 'US',
        'x-ulta-client-channel': 'web',
    }
    
    page = 0
    all_urls = []
    
    print("Memulai proses pagination...")
    
    while True:
        # PENTING: Batasan page > 50 telah DIHAPUS. Skrip akan berhenti secara alami.

        # 1. Bangun Path URL LENGKAP DENGAN PAGE DINAMIS
        path_query = f"{BASE_PATH}?page={page}&loadPreviousIndex=1{STATIC_PARAMS}"
        full_url_for_encoding = "https://www.ulta.com" + path_query
        encoded_path_in_query = urllib.parse.quote(full_url_for_encoding, safe='')

        # 2. Bangun URL GraphQL
        graphql_query_template = (
            "query%20NonCachedPage(%24stagingHost%3A%20String%2C%20%24previewOptions%3A%20JSON%2C%20%24moduleParams%3A%20JSON)%20%7B"
            "%20%20Page%3A%20NonCachedPage(stagingHost%3A%20%24stagingHost%2C%20previewOptions%3A%20%24previewOptions%2C%20moduleParams%3A%20%24moduleParams%2C%20url%3A%20%7Bpath%3A%20%22"
            f"{encoded_path_in_query}"
            f"%22%7D%2C%20contentId%3A%20%22{CONTENT_ID}%22)%20%7Bcontent%20customResponseAttributes%20meta%20__typename%7D%7D"
            "&operationName=NonCachedPage"
            "&variables=%7B%22moduleParams%22%3A%7B%22gti%22%3A%22eb9ae70c-311f-41dd-be0b-149654cd6d19%22%2C%22loginStatus%22%3A%22anonymous%22"
            "%2C%22retailerVisitorId%22%3A%2220d40221-124b-4304-a433-c63d766b8479%22%2C%22breakpoint%22%3A%22XL%22%7D%7D"
        )
        
        graphql_url = "https://www.ulta.com/dxl/graphql?ultasite=en-us&user-agent=gomez&query=" + graphql_query_template


        headers = headers_template.copy()
        # 3. SET Header Wajib
        headers["x-ulta-graph-page-url"] = full_url_for_encoding

        # 4. Lakukan Permintaan
        try:
            print(f"Mengambil halaman {page}...")
            r = requests.get(graphql_url, headers=headers, timeout=20) 
            r.raise_for_status() 
            data = r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error saat mengambil halaman {page}: {e}. Menghentikan.")
            break 
            
        # 5. Dapatkan dan Validasi Konten
        content = data.get("data", {}).get("Page", {}).get("content")
        
        if not isinstance(content, dict):
            print(f"Halaman {page} tidak memiliki konten yang valid. Menghentikan pagination.")
            break 

        # 6. Ekstrak URL Produk
        urls_on_page = extract_urls(content)

        # 7. Cek Kondisi Berhenti Alami
        if not urls_on_page:
            print(f"Halaman {page} tidak memiliki URL produk baru. Pagination Selesai.")
            break
            
        new_urls_count = 0
        for url in urls_on_page:
            # Menggunakan setidaknya satu pengecekan (query string) untuk mencegah duplikasi yang tidak perlu
            url_no_sku = url.split('?')[0] # Ambil base URL produk tanpa skuId
            is_new = True
            for existing_url in all_urls:
                if existing_url.split('?')[0] == url_no_sku:
                    is_new = False
                    break
            
            if is_new:
                 # Tambahkan URL lengkap (termasuk ?sku=...)
                all_urls.append(url)
                new_urls_count += 1
                
        print(f"PAGE {page}: Ditemukan {len(urls_on_page)} URL (Baru: {new_urls_count}). Total URL unik saat ini: {len(all_urls)}")
        
        # --- BLOK KODE UNTUK MENAMPILKAN URL (hanya 10 pertama) ---
        print(f"--- DAFTAR URL HALAMAN {page} (10 URL pertama) ---")
        for i, url in enumerate(urls_on_page):
            print(f"  {i+1}. {url}")
        # if len(urls_on_page) > 10:
        #     print("  ... dan seterusnya.")
        print("----------------------------------------------------\n")
        # ----------------------------------------------------

        # INCREMENT PAGE
        page += 1
        time.sleep(1) 
        # break

    return all_urls