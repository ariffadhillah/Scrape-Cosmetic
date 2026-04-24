from bs4 import BeautifulSoup
import requests
import json
import re
import time

url = "https://www.neimanmarcus.com/c/beauty-hair-care-cat51180746?navpath=cat000000_cat000285_cat55180733_cat51180746&source=leftNav"

def load_datadome_cookie(path="datadome.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
datadome = load_datadome_cookie()

# datadome = "4QWBL~c2aAp9T0oPuMrgIBZ~LGCM6H7_yM7jaEZU4_W5bkDEOhIpvrrr8G3YYLNxJhkREBvcFXDzMiVdw_jd4C4cMEZ9gagJSIR4Ls80c1YsCXMmCMJsuCKcnNBVMC7S; Max-Age=31536000; Domain=.neimanmarcus.com; Path=/; Secure; SameSite=Lax"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": url,
    "Origin": "https://www.neimanmarcus.com",
    "x-datadome-clientid": datadome,
    "X-Feature-Toggles": '{ "USE_PH": false, "USE_CM4": false,"PDP_MASTERSTYLE_GROUP_PRODUCTS": true,"USE_PRIVATE_LAUNCH": true,"USE_DISPLAYABLE_BETA": false, "USE_CM4_DBU": false, "PH_BACKORDER_FLAG": true, "USE_SELLABLE_STORE": false}',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}

cookies = {
    "df_cid": "df1cf8f7-36dc-4a9f-a180-306edb4ececc",
    "m_bid": "fb.2.1764318285.6060987951717347",
    "_cplid": "1764317770718313",
    "_optuid": "1764317770718271",
    "datadome": datadome,
    "optimizelyEndUserId": "oeu1764317779405r0.24951854071271473",
    "_ga": "GA1.1.800365987.1764318331",
    "_ga_1B8WTDSBDF": "GS2.1.s1766484035$o10$g0$t1766484035$j60$l0$h0",
    "QuantumMetricUserID": "4e472d2a930234efd19657ea5b7f4e10",
    "__attentive_id": "6458f8efd4154904bf8081a8da091cda",
    "OptanonAlertBoxClosed": "2025-12-23T10:00:59.401Z",
    "OptanonConsent": "isGpcEnabled=0&datestamp=Tue+Dec+23+2025+17:01:00+GMT+0700&version=202507.1.0",
    "utag_main": "v_id:019ac98b968800128060aea2312e05050008100d0086e",
    "s_cc": "true",
    "s_ppv": url,
    "nm_throttling": "DT3",
    "pdp_mfa": "true",
}


# response = requests.get(
#     url,
#     headers=headers,
#     cookies=cookies,
#     timeout=20
# )
# print(response.text)



# response = requests.get(
#     url,
#     headers=headers,
#     cookies=cookies,
#     timeout=20
# )

# if response.status_code == 200:
#     try:
#         # 1. Parse string JSON menjadi dictionary Python
#         data = response.json()
        
#         # 2. Ambil list produk
#         products = data.get("products", [])
        
#         base_url = "https://www.neimanmarcus.com"
#         all_canonical_urls = []

#         print(f"Ditemukan {len(products)} produk di halaman ini.\n")

#         # 3. Loop untuk mengambil canonical URL
#         for product in products:
#             path = product.get("canonical")
#             if path:
#                 # Gabungkan base_url dengan path
#                 full_url = base_url + path
#                 all_canonical_urls.append(full_url)
#                 print(full_url)

#         # 4. Opsional: Simpan ke file teks
#         with open("product_urls.txt", "w") as f:
#             for link in all_canonical_urls:
#                 f.write(link + "\n")
        
#         print(f"\nBerhasil menyimpan {len(all_canonical_urls)} URL ke 'product_urls.txt'")

#     except json.JSONDecodeError:
#         print("Gagal membaca JSON. Respons mungkin bukan format JSON yang valid.")
# else:
#     print(f"Gagal! Status Code: {response.status_code}")


save_file = "Luxury Bath & Body Collection.csv"
# https://www.neimanmarcus.com/c/dt/api/productlisting?categoryId=cat51180746&page=2&parentCategoryId=cat55180733&siloCategoryId=cat000285&navPath=cat000000_cat000285_cat55180733_cat511807460431,prod254650167
base_api_url = "https://www.neimanmarcus.com/c/dt/api/productlisting?categoryId=cat10470806"
all_product_urls = []
base_domain = "https://www.neimanmarcus.com"

# Loop dari page 1 sampai 25
for page in range(1, 5):
    print(f"--- Mengambil Halaman {page} ---")
    
    # Masukkan parameter page ke dalam URL
    current_url = f"{base_api_url}&page={page}&parentCategoryId=cat55180733&siloCategoryId=cat000285&navPath=cat000000_cat000285_cat55180733_cat10470806"
    
    try:
        response = requests.get(current_url, headers=headers, cookies=cookies, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            
            if not products:
                print(f"Tidak ada produk lagi di halaman {page}. Berhenti.")
                break
                
            for prod in products:
                path = prod.get("canonical")
                if path:
                    full_link = base_domain + path
                    all_product_urls.append(full_link)
            
            print(f"Berhasil mengambil {len(products)} produk dari halaman {page}.")
            
        elif response.status_code == 403:
            print("ERROR 403: Sesi/Cookie DataDome sudah kedaluwarsa. Silakan ambil cookie baru!")
            break
        else:
            print(f"Error pada halaman {page}: Status {response.status_code}")

    except Exception as e:
        print(f"Terjadi error pada halaman {page}: {e}")
    
    # Delay 2-3 detik agar tidak terdeteksi bot yang sangat agresif
    time.sleep(2)


# Simpan semua hasil ke satu file
with open(save_file, "w") as f:
    for url in all_product_urls:
        f.write(url + "\n")

print(f"\nSelesai! Total {len(all_product_urls)} URL berhasil dikumpulkan.")