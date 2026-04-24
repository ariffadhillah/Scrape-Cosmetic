
# import requests
# import json
# import re
# import os
# import csv
# import time
# import random  # Tambahkan ini untuk jeda acak
# from bs4 import BeautifulSoup

# # --- KONFIGURASI KATEGORI ---
# Major_Category = "Bath & Body"
# Category = "Luxury Bath & Body Collection"

# # --- KONFIGURASI FILE ---
# INPUT_FILENAME = "url.csv"
# OUTPUT_FILENAME = f"{Major_Category.replace(' ', '_')}_{Category.replace(' ', '_')}.csv"
# URL_COLUMN_NAME = "Product Url"

# fields = [
#     "Product ID", "SKU ID", "Product Name", "Product Maker", 
#     "Varian/color", "Product Url", "Major Category", 
#     "Category", "Ingredients", "Product Image URL", "Price"
# ]

# # --- FUNGSI HELPER ---

# PROXY_LIST = [
#     "46.203.210.142:5589",
#     "92.113.231.248:7333",
#     "104.239.33.248:6603",
#     "136.0.189.3:6730",
#     "31.57.82.64:6645",
#     "82.21.244.76:5399"
# ]

# PROXY_USER = "arssrhsq"
# PROXY_PASS = "x1vpi09f4v1g"


# def get_random_proxy():
#     proxy = random.choice(PROXY_LIST)
#     proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{proxy}"
#     return {
#         "http": proxy_url,
#         "https": proxy_url
#     }


# def load_datadome_cookie(path="datadome.txt"):
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             return f.read().strip()
#     except FileNotFoundError:
#         print("⚠️ File datadome.txt tidak ditemukan!")
#         return ""

# def extract_brand(product_data):
#     attributes = product_data.get('attributesMap', {})
#     if attributes and attributes.get('brandName'):
#         return attributes['brandName'][0]
#     for key in ['skus', 'childProducts']:
#         for item in product_data.get(key, []):
#             attrs = item.get('attributesMap', {})
#             if attrs and attrs.get('brandName'):
#                 return attrs['brandName'][0]
#     return "N/A"

# def build_price_sources(product_data):
#     price_map = {}
#     for child in product_data.get("childProducts", []):
#         pid = child.get("id")
#         price = child.get("price", {})
#         if pid and price.get("retailPrice"):
#             price_map[pid] = price.get("retailPrice")
#     root_price = product_data.get("price", {}).get("retailPrice")
#     range_price = product_data.get("priceRange", {}).get("lowPrice")
#     return price_map, root_price, range_price

# def extract_ingredients_from_longdesc(long_desc):
#     if not long_desc: return "N/A"
#     soup = BeautifulSoup(long_desc, "html.parser")
#     text = re.sub(r"\u00a0", " ", soup.get_text(separator="\n"))
#     text = re.sub(r"\n+", "\n", text).strip()

#     patterns = [
#         r"Ingredients\*:\s*(.+?)(?:\n\*Please Note|\nPlease|\Z)",
#         r"Ingredients Listing\s*(.+?)(?:\n[A-Z][a-z ]+:|\n\d+(\.\d+)?\s*oz|\Z)",
#         r"Ingredients\s*\*?\s*:?\s*\n(.+)",
#     ]
#     for pattern in patterns:
#         match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
#         if match:
#             ingredients = match.group(1).strip()
#             ingredients = re.split(r"\n(?:How To Use|Shade Descriptions|Pairs Well With|Clinical Results)", ingredients, flags=re.IGNORECASE)[0].strip()
#             return ingredients
#     return "N/A"

# # --- FUNGSI UTAMA SCRAPER ---

# def scrape_neiman_marcus(url, datadome_val):

#     # headers = {
#     #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
#     #     "Accept": "application/json, text/plain, */*",
#     #     "x-datadome-clientid": datadome_val,
#     #     "Referer": "https://www.neimanmarcus.com/",
#     # }
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
#         "Accept": "application/json, text/plain, */*",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip, deflate, br, zstd",
#         "Referer": url,
#         "Origin": "https://www.neimanmarcus.com",
#         "x-datadome-clientid": datadome_val,
#         "X-Feature-Toggles": '{ "USE_PH": false, "USE_CM4": false,"PDP_MASTERSTYLE_GROUP_PRODUCTS": true,"USE_PRIVATE_LAUNCH": true,"USE_DISPLAYABLE_BETA": false, "USE_CM4_DBU": false, "PH_BACKORDER_FLAG": true, "USE_SELLABLE_STORE": false}',
#         "Sec-Fetch-Dest": "empty",
#         "Sec-Fetch-Mode": "cors",
#         "Sec-Fetch-Site": "same-origin",
#         "Connection": "keep-alive",
#     }

#     cookies = {
#         "df_cid": "df1cf8f7-36dc-4a9f-a180-306edb4ececc",
#         "m_bid": "fb.2.1764318285.6060987951717347",
#         "_cplid": "1764317770718313",
#         "_optuid": "1764317770718271",
#         "datadome": datadome_val,
#         "optimizelyEndUserId": "oeu1764317779405r0.24951854071271473",
#         "_ga": "GA1.1.800365987.1764318331",
#         "_ga_1B8WTDSBDF": "GS2.1.s1766484035$o10$g0$t1766484035$j60$l0$h0",
#         "QuantumMetricUserID": "4e472d2a930234efd19657ea5b7f4e10",
#         "__attentive_id": "6458f8efd4154904bf8081a8da091cda",
#         "OptanonAlertBoxClosed": "2025-12-23T10:00:59.401Z",
#         "OptanonConsent": "isGpcEnabled=0&datestamp=Tue+Dec+23+2025+17:01:00+GMT+0700&version=202507.1.0",
#         "utag_main": "v_id:019ac98b968800128060aea2312e05050008100d0086e",
#         "s_cc": "true",
#         "s_ppv": url,
#         "nm_throttling": "DT3",
#         "pdp_mfa": "true",
#     }

#     try:
#         # response = requests.get(url, headers=headers, cookies=cookies, timeout=25)

#         proxies = get_random_proxy()

#         response = requests.get(
#             url,
#             headers=headers,
#             cookies=cookies,
#             proxies=proxies,
#             timeout=25
#         )


#         if response.status_code == 403:
#             print(f"🚫 Akses Ditolak (403) pada {url}. Cookie mungkin kadaluarsa.")
#             return []
#         if response.status_code != 200:
#             print(f"❌ Error {response.status_code} pada {url}")
#             return []








#         match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text, re.DOTALL)
#         if not match:
#             return []

#         next_data = json.loads(match.group(1))
#         product_data = next_data['props']['pageProps']['productData']
        
#         product_name = product_data.get('name')
#         brand = extract_brand(product_data)
#         price_map, root_price, range_price = build_price_sources(product_data)
#         ingredients = extract_ingredients_from_longdesc(product_data.get('details', {}).get('longDesc'))
        
#         scraped_items = []
#         for sku in product_data.get("skus", []):
#             sku_id = sku.get("id")
#             product_id = sku.get("productId")
#             varian = sku.get("color", {}).get("name") or sku.get("size", {}).get("name") or "Standard"
#             img_url = sku.get("media", {}).get("main", {}).get("dynamic", {}).get("url")
#             final_price = price_map.get(product_id) or root_price or range_price

#             scraped_items.append({
#                 "Product ID": product_id,
#                 "SKU ID": sku_id,
#                 "Product Name": product_name,
#                 "Product Maker": brand,
#                 "Varian/color": varian,
#                 "Product Url": url,
#                 "Major Category": Major_Category, 
#                 "Category": Category,
#                 "Ingredients": ingredients,
#                 "Product Image URL": img_url,
#                 "Price": final_price
#             })
#         return scraped_items
#     except Exception as e:
#         print(f"⚠️ Request Error: {e}")
#         return []

# # --- EKSEKUSI UTAMA ---

# def main():
#     datadome = load_datadome_cookie()
#     file_exists = os.path.isfile(OUTPUT_FILENAME)
    
#     if not os.path.exists(INPUT_FILENAME):
#         print(f"❌ File input {INPUT_FILENAME} tidak ditemukan!")
#         return

#     with open(INPUT_FILENAME, mode='r', encoding='utf-8') as infile:
#         reader = list(csv.DictReader(infile))
#         total_urls = len(reader)
#         print(f"🚀 Memulai scraping {total_urls} produk...")

#         with open(OUTPUT_FILENAME, mode='a', newline='', encoding='utf-8') as outfile:
#             writer = csv.DictWriter(outfile, fieldnames=fields)
#             if not file_exists:
#                 writer.writeheader()

#             for index, row in enumerate(reader, 1):
#                 target_url = row.get(URL_COLUMN_NAME)
#                 if not target_url: continue

#                 print(f"[{index}/{total_urls}] 🔍 Scraping: {target_url}")
                
#                 results = scrape_neiman_marcus(target_url, datadome)
#                 if results:
#                     for item in results:
#                         writer.writerow(item)
#                     print(f"   ✅ Berhasil mengambil {len(results)} varian.")
#                 else:
#                     print(f"   ⚠️ Data tidak ditemukan atau diblokir.")

#                 # --- LOGIKA JEDA ANTI-BLOCK ---
#                 if index < total_urls:
#                     # 1. Jeda acak antar produk (3 sampai 7 detik)
#                     sleep_time = random.uniform(3, 7)
                    
#                     # 2. Jeda lebih panjang setiap 10 produk (Batch Break)
#                     if index % 10 == 0:
#                         batch_delay = random.randint(30, 60)
#                         print(f"☕ Istirahat sejenak... (Batch Break {batch_delay} detik)")
#                         time.sleep(batch_delay)
#                     else:
#                         time.sleep(sleep_time)

#     print(f"🎉 Selesai! Data disimpan di {OUTPUT_FILENAME}")

# if __name__ == "__main__":
#     main()




# def scrape_neiman_marcus(url, datadome_val):
#     proxies = get_random_proxy()
#     print(f"🌐 Proxy digunakan: {proxies['http'].split('@')[-1]}")

#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
#         "Accept": "application/json, text/plain, */*",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip, deflate, br, zstd",
#         "Referer": url,
#         "Origin": "https://www.neimanmarcus.com",
#         "x-datadome-clientid": datadome_val,
#         "X-Feature-Toggles": '{ "USE_PH": false, "USE_CM4": false,"PDP_MASTERSTYLE_GROUP_PRODUCTS": true,"USE_PRIVATE_LAUNCH": true,"USE_DISPLAYABLE_BETA": false, "USE_CM4_DBU": false, "PH_BACKORDER_FLAG": true, "USE_SELLABLE_STORE": false}',
#         "Sec-Fetch-Dest": "empty",
#         "Sec-Fetch-Mode": "cors",
#         "Sec-Fetch-Site": "same-origin",
#         "Connection": "keep-alive",
#     }

#     cookies = {
#         "df_cid": "df1cf8f7-36dc-4a9f-a180-306edb4ececc",
#         "m_bid": "fb.2.1764318285.6060987951717347",
#         "_cplid": "1764317770718313",
#         "_optuid": "1764317770718271",
#         "datadome": datadome_val,
#         "optimizelyEndUserId": "oeu1764317779405r0.24951854071271473",
#         "_ga": "GA1.1.800365987.1764318331",
#         "_ga_1B8WTDSBDF": "GS2.1.s1766484035$o10$g0$t1766484035$j60$l0$h0",
#         "QuantumMetricUserID": "4e472d2a930234efd19657ea5b7f4e10",
#         "__attentive_id": "6458f8efd4154904bf8081a8da091cda",
#         "OptanonAlertBoxClosed": "2025-12-23T10:00:59.401Z",
#         "OptanonConsent": "isGpcEnabled=0&datestamp=Tue+Dec+23+2025+17:01:00+GMT+0700&version=202507.1.0",
#         "utag_main": "v_id:019ac98b968800128060aea2312e05050008100d0086e",
#         "s_cc": "true",
#         "s_ppv": url,
#         "nm_throttling": "DT3",
#         "pdp_mfa": "true",
#     }

#     try:
#         response = requests.get(
#             url,
#             headers=headers,
#             cookies=cookies,
#             proxies=proxies,
#             timeout=25
#         )

#         if response.status_code in (403, 429):
#             print("🚫 Proxy atau cookie diblokir")
#             return []

#         match = re.search(
#             r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
#             response.text,
#             re.DOTALL
#         )
#         if not match:
#             return []

#         next_data = json.loads(match.group(1))
#         product_data = next_data['props']['pageProps']['productData']

#         price_map, root_price, range_price = build_price_sources(product_data)
#         ingredients = extract_ingredients_from_longdesc(
#             product_data.get('details', {}).get('longDesc')
#         )

#         items = []
#         for sku in product_data.get("skus", []):
#             product_id = sku.get("productId")
#             items.append({
#                 "Product ID": product_id,
#                 "SKU ID": sku.get("id"),
#                 "Product Name": product_data.get("name"),
#                 "Product Maker": extract_brand(product_data),
#                 "Varian/color": sku.get("size", {}).get("name") or "Standard",
#                 "Product Url": url,
#                 "Major Category": Major_Category,
#                 "Category": Category,
#                 "Ingredients": ingredients,
#                 "Product Image URL": sku.get("media", {}).get("main", {}).get("dynamic", {}).get("url"),
#                 "Price": price_map.get(product_id) or root_price or range_price
#             })
#         return items

#     except Exception as e:
#         print(f"⚠️ Error: {e}")
#         return []



import requests

API_URL = "https://www.neimanmarcus.com/c/dt/api/productlisting"

params = {
    "categoryId": "cat10470738",
    "page": 1
}

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
    "Referer": API_URL,
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
    "s_ppv": API_URL,
    "nm_throttling": "DT3",
    "pdp_mfa": "true",
}

res = requests.get(API_URL, params=params, cookies=cookies, headers=headers)
# data = res.json()
# print(data)

# pastikan response valid
# res.raise_for_status()

data = res.json()
import json
# simpan ke file json
with open("neimanmarcus_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Data berhasil disimpan ke neimanmarcus_response.json")

# products = data.get("products", [])

# for p in products:
#     product_url = "https://www.neimanmarcus.com" + p.get("url", "")
#     print({
#         "id": p.get("id"),
#         "name": p.get("name"),
#         "brand": p.get("brandName"),
#         "price": p.get("price", {}).get("retailPrice"),
#         "image": p.get("media", {}).get("main", {}).get("dynamic", {}).get("url"),
#         "url": product_url
#     })
