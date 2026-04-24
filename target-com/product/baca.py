# # # # import requests

# # # # url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?category=5xszd&count=24&default_purchasability_filter=true&include_sponsored=true&include_review_summarization=true&offset=24&page=%2Fc%2F5xszd&platform=desktop&pricing_store_id=1874&spellcheck=true&store_ids=1874%2C1009%2C2272%2C1046%2C1137&visitor_id=019CFCCE4CC50200A497F1A4D4A5DE12&zip=20131&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB&include_dmc_dmr=true&useragent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F146.0.0.0+Safari%2F537.36"

# # # # payload = {}
# # # # headers = {
# # # #   'accept': 'application/json',
# # # #   'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
# # # #   'dnt': '1',
# # # #   'origin': 'https://www.target.com',
# # # #   'priority': 'u=1, i',
# # # #   'referer': 'https://www.target.com/c/frozen-foods-grocery/-/N-5xszd',
# # # #   'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
# # # #   'sec-ch-ua-mobile': '?0',
# # # #   'sec-ch-ua-platform': '"Windows"',
# # # #   'sec-fetch-dest': 'empty',
# # # #   'sec-fetch-mode': 'cors',
# # # #   'sec-fetch-site': 'same-site',
# # # #   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
# # # #   'Cookie': 'refreshToken=bTaX_mJr__A9S2-_j3_E9yLk6uRxTErbeO6Bfvrte3bJRy8Bz-kdmkl_uC1l67rGOWAEE9W_qTyEw13z-jpziQ; adScriptData=SU; visitorId=019CFCCE4CC50200A497F1A4D4A5DE12; TealeafAkaSid=kMNS-C46sB-SYxrX31-lnmmcvKRUAESh; onboardingGuest=timestamp=1773767905154; sapphire=1; idToken=eyJhbGciOiJub25lIn0.eyJzdWIiOiI5NGJiMzQxMC05YTk2LTRiMDItOGVmMC1hMTM3M2ViN2Y5MjMiLCJpc3MiOiJNSTYiLCJleHAiOjE3NzM4NTQzMDQsImlhdCI6MTc3Mzc2NzkwNCwiYXNzIjoiTCIsInN1dCI6IkciLCJjbGkiOiJlY29tLXdlYi0xLjAuMCIsInBybyI6eyJmbiI6bnVsbCwiZm51IjpudWxsLCJlbSI6bnVsbCwicGgiOmZhbHNlLCJsZWQiOm51bGwsImx0eSI6ZmFsc2UsInN0IjoiU1UiLCJzbiI6bnVsbH19.; accessToken=eyJraWQiOiJlYXMyIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI5NGJiMzQxMC05YTk2LTRiMDItOGVmMC1hMTM3M2ViN2Y5MjMiLCJpc3MiOiJNSTYiLCJleHAiOjE3NzM4NTQzMDQsImlhdCI6MTc3Mzc2NzkwNCwianRpIjoiVEdULmIxM2I1ZDRhYmY1ZDRlODY4NmM2ZDczZDJiOTRhNTA4LWwiLCJza3kiOiJlYXMyIiwic3V0IjoiRyIsImRpZCI6IjM0NTM2OGI4M2NhZjE3YjA5OTc2YWQ3ZmM4NmFhZmVjYmQ2MTBjYmU4MGU2ODNkMmIzNDFhNTg3NzQxMjMzZmUiLCJzY28iOiJlY29tLm5vbmUsb3BlbmlkIiwiY2xpIjoiZWNvbS13ZWItMS4wLjAiLCJhc2wiOiJMIn0.FQY1wAkXBbVA7tvtr5-W4WXwgUadMFi9kMKDkTl9L2T23eRhR3uXAUyrRxBjM8H4KgrTlfp8rvOGsy6RMv4zNEVzAFRRUOv96JKm52ezjLudZgDcX7HDM4ExuZZrKXrNwyTSeE1Hn54RGEcaj0OPFR1JWK0SZnjOxk2f4DzzaEtbp96qxkJSWy44uqOTpD75_Jltre0MqVmnX7sXULCj2ixdXnYWQ--OTRC9a3l8Ye0sbXAi82XDiE4Sy81QLyPgh8pVMHT7_5G7fw--7m3s2rLYjA9Ei4rCsnmVYHKf1GlbxUR223UyhfDve4i6qm3NCmcENILZoPwFAIAM1EM71g; egsSessionId=e1eae579-452a-4ed2-bd95-ebad8434a765; _pxvid=4f587a4f-2225-11f1-8f90-aacb78c386dd; pxcts=4f5890b1-2225-11f1-8f93-6081a290ebfb; UserLocation=20131|3.540|98.650|SU|ID; ffsession={%22sessionHash%22:%229b032861948751773767905197%22}; AMCVS_99DD1CFE5329660B0A490D45%40AdobeOrg=1; BVBRANDID=d292357c-8080-434d-bc20-9a8910a31d4b; BVBRANDSID=a6d70243-17e6-4d4a-b34a-3780ff36f5fe; fiatsCookie=DSI_1874|DSN_Leesburg|DSZ_20176; hideglobalbanner=true; AMCV_99DD1CFE5329660B0A490D45%40AdobeOrg=179643557%7CMCIDTS%7C20530%7CMCMID%7C58798565123627039105302998966176410069%7CMCOPTOUT-1773775525s%7CNONE%7CvVersion%7C5.5.0; _px3=7a1189aa31cc684568dcb3298c7260f08a1d5d4486c4e8dfe82c840714a7ec99:fS/X1kxxwQ6jU1jaJlZ64AzE8hoeW27OuZI3fxLW8AqhXfHt6qCXeEgwcRGoAfFU3YFcqj2lh5Djcp+1XcqtAA==:1000:PKPf0Y+JBV/cbbf1lrszFySx0Q+qK345Emin8zLZUV8IQ83iNHzEpAAK/8/X21Y8/hh8JCcsSrfuBkVG8DZ8P9tOVAVZnyApSPne17NuCm1S5AEmYwANS4KK4e6IenqAO53DU2BnPjdObSNb9d6k/oZxeO6ZSAvEIjK0/YE14uwt96q5uyXhz59ra5dt1rfgKQ8YS4vjt0y7wQADAUIsji/FtVGyQu3u30wS6/oyXHc3pn8NAIEnDjH5pQIy/O7HcaoaVOu8jUbUKgbrwkRp0BIA9SlOWv/S1sBAD3N3tZtzZ0Bs4o+D3UqMv0coNhh24ejsX6Ge5GdljvxLScnCaaUD1o3w1Pxa+0klBOpOOueC1/4bAc4pksEu7ezCv7skQ7g8IYNBfH5Iwz0ok5H8akwx7J7CD1MzjzTAW2s0mBoepLrfakZenNn+rCiWPtPcSW+VC2qgPInVd1QymkPg2PqaSeTN6xgpGQOPSvjxqCo=; _tgt_session=ce781b22e0344e6e8f98bc80534b5f14.6ca11cf6361f58e4019e4975720f18810f55fdfebe2305aa23fd70c1e57842130339b347c5445706ec1a09d839109e9147e30703a0680653fe913be51d115e0331d9b0c2faf6b05a80d7dab1f8bab27dc95c26f21f88f98fdf9d136c6eccb263dedec5a02de2d191e97e6da78109f2d10e1606ddc3c07c7d9c66177aa03c7054d4edc2775885f942e04d2907073c9262e1cb7f0fb87cc59bd6a39e4c025669a0d78d55488eb5ac570c022eb1a4732b3a0a37bfaabb864fa9ce82fe0ce9874ffa8338485762eeb1b05f619ceb81e4ee23c647febbcb7ee8591e13206e98fd0adcd9.0x981c247c4b6482ebbc132bfeb1552288668ce94723b29233f60635f6727d4764; __gads=ID=b64d50eee79603b6:T=1773723595:RT=1773768330:S=ALNI_MbPceUBnQph9zrGSv0BM3zFKCX9yA; __gpi=UID=00001220e873415b:T=1773723595:RT=1773768330:S=ALNI_MbXcZ0ABZsEAVmwsfdnDNhI8E2yag; __eoi=ID=ad458edf26fa3b5a:T=1773723595:RT=1773768330:S=AA-AfjazWcT19eb0oRqSa0GXflSq; _tgt_session=53c5d9d2aab74e869d055a31e6fac600.ee65b869bea270b78aa77b2f2460e71b8b0639860cf00e59cde689e6cbf346cb01f67ce33fd0b5121e0a5c5c608fb474ad9d8c9942485fa9b39dee4c3ed4def91cf77b39ec1e97086ccd16516413eb2510a141960093a78d31e74b4fe4661cfad0eefbdcaba9f53ff4a0e70230da8b193c9761805e59952b965678b148db47c87857c0dc14981f81280143f3322de6501039f4514af585ffb05d6c17346c929b500f57d8d73da891aa5fe1e57c7d608b11a18f95821e5a33706190435a004718c7561f76cd99380729daaab62d99ab87f1be8618993b1eb397c15741b191819b80.0x7b458c34039d88620fbd5c58a5d778cdf768d8625526fc5827549d81fce1498a'
# # # # }

# # # # response = requests.request("GET", url, headers=headers, data=payload)

# # # # print(response.text)




# # # import requests
# # # import json

# # # url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?category=5xszd&count=24&default_purchasability_filter=true&include_sponsored=true&include_review_summarization=true&offset=24&page=%2Fc%2F5xszd&platform=desktop&pricing_store_id=1874&spellcheck=true&store_ids=1874%2C1009%2C2272%2C1046%2C1137&visitor_id=019CFCCE4CC50200A497F1A4D4A5DE12&zip=20131&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB&include_dmc_dmr=true&useragent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F146.0.0.0+Safari%2F537.36"

# # # payload = {}
# # # headers = {
# # #   'accept': 'application/json',
# # #   'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
# # #   'origin': 'https://www.target.com',
# # #   'referer': 'https://www.target.com/',
# # #   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
# # #   'Cookie': 'YOUR_COOKIE_HERE' # Pastikan cookie masih valid
# # # }

# # # response = requests.request("GET", url, headers=headers, data=payload)

# # # # --- PERBAIKAN DI SINI ---
# # # if response.status_code == 200:
# # #     data = response.json() # Mengubah string JSON menjadi dictionary
    
# # #     # Mengakses list produk
# # #     products = data.get('data', {}).get('search', {}).get('products', [])

# # #     for product in products:
# # #         item = product.get('item', {})
# # #         description = item.get('product_description', {})
# # #         price = product.get('price', {})
        
# # #         title = description.get('title')
# # #         current_price = price.get('formatted_current_price')
# # #         tcin = item.get('tcin')
        
# # #         print(f"ID: {tcin} | Harga: {current_price} | Nama: {title}")
# # # else:
# # #     print(f"Error: {response.status_code}")
# # #     print(response.text)



# # import requests
# # import time

# # # Base URL tanpa offset (kita akan tambahkan nanti)
# # base_url = "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?category=5xszd&count=24&default_purchasability_filter=true&include_sponsored=true&include_review_summarization=true&page=%2Fc%2F5xszd&platform=desktop&pricing_store_id=1874&spellcheck=true&store_ids=1874%2C1009%2C2272%2C1046%2C1137&visitor_id=019CFCCE4CC50200A497F1A4D4A5DE12&zip=20131&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB&include_dmc_dmr=true"

# # headers = {
# #     'accept': 'application/json',
# #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
# #     'Cookie': 'YOUR_COOKIE_HERE'
# # }

# # all_products = []
# # total_results = 1778
# # step = 24

# # for offset in range(0, total_results, step):
# #     print(f"Mengambil data dari offset: {offset}...")
    
# #     # Gabungkan base_url dengan offset yang dinamis
# #     current_url = f"{base_url}&offset={offset}"
    
# #     try:
# #         response = requests.get(current_url, headers=headers)
        
# #         if response.status_code == 200:
# #             data = response.json()
# #             products = data.get('data', {}).get('search', {}).get('products', [])
            
# #             if not products:
# #                 break # Berhenti jika tidak ada produk lagi
                
# #             all_products.extend(products)
# #             print(f"Berhasil mengambil {len(products)} produk.")
            
# #         else:
# #             print(f"Gagal di offset {offset}. Status code: {response.status_code}")
# #             break
            
# #         # Jeda sejenak agar tidak terkena ban (anti-bot protection)
# #         time.sleep(2) 
        
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         break

# # print(f"Total produk yang berhasil dikumpulkan: {len(all_products)}")

# import requests
# import time
# import json
# import random

# # Daftar Proxy Anda (IP:PORT:USER:PASS)
# proxies_list = [
#     "191.96.254.80:6127:arssrhsq:x1vpi09f4v1g",
#     "45.61.122.149:6441:arssrhsq:x1vpi09f4v1g",
#     "45.61.124.153:6482:arssrhsq:x1vpi09f4v1g",
#     "64.64.110.63:6586:arssrhsq:x1vpi09f4v1g",
#     "145.223.58.21:6290:arssrhsq:x1vpi09f4v1g",
#     "82.23.206.96:5902:arssrhsq:x1vpi09f4v1g",
#     "38.154.233.46:5456:arssrhsq:x1vpi09f4v1g",
#     "45.61.118.128:5825:arssrhsq:x1vpi09f4v1g",
#     "191.96.202.229:6275:arssrhsq:x1vpi09f4v1g"
#     "23.27.196.145:6514:arssrhsq:x1vpi09f4v1g",
#     "154.6.126.37:6008:arssrhsq:x1vpi09f4v1g",
#     "89.249.195.211:6966:arssrhsq:x1vpi09f4v1g",
#     "147.124.198.69:5928:arssrhsq:x1vpi09f4v1g",
#     "82.24.238.65:6872:arssrhsq:x1vpi09f4v1g",
#     "38.154.217.34:7225:arssrhsq:x1vpi09f4v1g",
#     "174.140.200.142:6422:arssrhsq:x1vpi09f4v1g",
#     "46.202.224.238:5790:arssrhsq:x1vpi09f4v1g",
#     "31.57.87.145:5830:arssrhsq:x1vpi09f4v1g",
#     "38.154.233.181:5591:arssrhsq:x1vpi09f4v1g",
#     "198.46.241.143:6678:arssrhsq:x1vpi09f4v1g",
#     "23.27.203.134:6869:arssrhsq:x1vpi09f4v1g",
#     "104.168.118.219:6175:arssrhsq:x1vpi09f4v1g",
#     "152.232.14.43:7174:arssrhsq:x1vpi09f4v1g",
#     "82.26.238.68:6375:arssrhsq:x1vpi09f4v1g",
#     "89.249.194.231:6630:arssrhsq:x1vpi09f4v1g",
#     "104.232.211.0:5613:arssrhsq:x1vpi09f4v1g",
#     "38.154.217.123:7314:arssrhsq:x1vpi09f4v1g",
#     "67.227.14.204:6796:arssrhsq:x1vpi09f4v1g"




#     # Tambahkan semua proxy lainnya di sini...
# ]

# def get_proxy_dict(proxy_str):
#     ip, port, user, pw = proxy_str.split(':')
#     proxy_url = f"http://{user}:{pw}@{ip}:{port}"
#     return {
#         "http": proxy_url,
#         "https": proxy_url
#     }

# visitor_id = "019CFCE885520200B468E5FA8AE98CF7"
# api_key = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

# base_url = f"https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?category=5xszd&count=24&default_purchasability_filter=true&include_sponsored=true&include_review_summarization=true&page=%2Fc%2F5xszd&platform=desktop&pricing_store_id=1874&spellcheck=true&store_ids=1874%2C1009%2C2272%2C1046%2C1137&visitor_id={visitor_id}&zip=20131&key={api_key}&channel=WEB&include_dmc_dmr=true"

# headers = {
#     'accept': 'application/json',
#     'referer': 'https://www.target.com/c/frozen-foods-grocery/-/N-5xszd',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
# }

# all_products = []
# total_results = 1778
# step = 24

# for offset in range(0, total_results, step):
#     # Rotasi Proxy: Ambil satu secara acak atau berurutan
#     proxy_choice = proxies_list[offset // step % len(proxies_list)]
#     proxies = get_proxy_dict(proxy_choice)
    
#     print(f"Offset: {offset} | Menggunakan Proxy: {proxy_choice.split(':')[0]}")
    
#     current_url = f"{base_url}&offset={offset}"
    
#     try:
#         # Timeout ditambahkan agar jika proxy mati tidak menunggu selamanya
#         response = requests.get(current_url, headers=headers, proxies=proxies, timeout=15)
        
#         if response.status_code == 200:
#             data = response.json()
#             products = data.get('data', {}).get('search', {}).get('products', [])
            
#             if not products:
#                 print("Pencarian selesai (tidak ada produk).")
#                 break
                
#             all_products.extend(products)
#             print(f"Berhasil: {len(products)} produk. Total: {len(all_products)}")
            
#         elif response.status_code == 404:
#             print(f"Offset {offset} tetap 404. Limit Deep Paging terdeteksi.")
#             # Jika 404 tetap muncul meski sudah ganti IP, berarti Target membatasi jumlah offset 
#             # untuk kategori tersebut. Solusinya adalah segmentasi harga (price range).
#             break
#         else:
#             print(f"Gagal {offset}. Status: {response.status_code}")
            
#         time.sleep(1.5) # Jeda sedikit agar tetap aman
        
#     except Exception as e:
#         print(f"Error pada proxy {proxy_choice.split(':')[0]}: {e}")
#         # Jika error (proxy mati), kita bisa mengulangi offset ini di loop berikutnya
#         continue

# # Simpan data
# with open('target_data_proxy.json', 'w') as f:
#     json.dump(all_products, f)

# print(f"\nSelesai! Total terkumpul: {len(all_products)}")



import requests
import time
import json
import random

# Daftar Proxy Anda (IP:PORT:USER:PASS)
proxies_list = [
    "191.96.254.80:6127:arssrhsq:x1vpi09f4v1g",
    "45.61.122.149:6441:arssrhsq:x1vpi09f4v1g",
    "45.61.124.153:6482:arssrhsq:x1vpi09f4v1g",
    "64.64.110.63:6586:arssrhsq:x1vpi09f4v1g",
    "145.223.58.21:6290:arssrhsq:x1vpi09f4v1g",
    "82.23.206.96:5902:arssrhsq:x1vpi09f4v1g",
    "38.154.233.46:5456:arssrhsq:x1vpi09f4v1g",
    "45.61.118.128:5825:arssrhsq:x1vpi09f4v1g",
    "191.96.202.229:6275:arssrhsq:x1vpi09f4v1g",
    "23.27.196.145:6514:arssrhsq:x1vpi09f4v1g",
    "154.6.126.37:6008:arssrhsq:x1vpi09f4v1g",
    "89.249.195.211:6966:arssrhsq:x1vpi09f4v1g",
    "147.124.198.69:5928:arssrhsq:x1vpi09f4v1g",
    "82.24.238.65:6872:arssrhsq:x1vpi09f4v1g",
    "38.154.217.34:7225:arssrhsq:x1vpi09f4v1g",
    "174.140.200.142:6422:arssrhsq:x1vpi09f4v1g",
    "46.202.224.238:5790:arssrhsq:x1vpi09f4v1g",
    "31.57.87.145:5830:arssrhsq:x1vpi09f4v1g",
    "38.154.233.181:5591:arssrhsq:x1vpi09f4v1g",
    "198.46.241.143:6678:arssrhsq:x1vpi09f4v1g",
    "23.27.203.134:6869:arssrhsq:x1vpi09f4v1g",
    "104.168.118.219:6175:arssrhsq:x1vpi09f4v1g",
    "152.232.14.43:7174:arssrhsq:x1vpi09f4v1g",
    "82.26.238.68:6375:arssrhsq:x1vpi09f4v1g",
    "89.249.194.231:6630:arssrhsq:x1vpi09f4v1g",
    "104.232.211.0:5613:arssrhsq:x1vpi09f4v1g",
    "38.154.217.123:7314:arssrhsq:x1vpi09f4v1g",
    "67.227.14.204:6796:arssrhsq:x1vpi09f4v1g"
]

def get_proxy_dict(proxy_str):
    """Mengonversi string IP:PORT:USER:PASS menjadi dictionary proxy requests."""
    try:
        ip, port, user, pw = proxy_str.split(':')
        proxy_url = f"http://{user}:{pw}@{ip}:{port}"
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    except Exception:
        return None

# Konfigurasi Target API
visitor_id = "019CFCE885520200B468E5FA8AE98CF7"
api_key = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

base_url = (
    f"https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?"
    f"category=5xszd&count=24&default_purchasability_filter=true&include_sponsored=true&"
    f"include_review_summarization=true&page=%2Fc%2F5xszd&platform=desktop&pricing_store_id=1874&"
    f"spellcheck=true&store_ids=1874%2C1009%2C2272%2C1046%2C1137&visitor_id={visitor_id}&"
    f"zip=20131&key={api_key}&channel=WEB&include_dmc_dmr=true"
)

headers = {
    'accept': 'application/json',
    'referer': 'https://www.target.com/c/frozen-foods-grocery/-/N-5xszd',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

all_tcin = []
total_results = 1778
step = 24

print("--- Memulai Scraping TCIN ---")

for offset in range(0, total_results, step):
    # Rotasi Proxy
    proxy_choice = proxies_list[offset // step % len(proxies_list)]
    proxies = get_proxy_dict(proxy_choice)
    
    if not proxies:
        continue

    print(f"Offset: {offset} | Proxy: {proxy_choice.split(':')[0]}", end=" -> ")
    
    current_url = f"{base_url}&offset={offset}"
    
    try:
        # Request dengan timeout 15 detik
        response = requests.get(current_url, headers=headers, proxies=proxies, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', {}).get('search', {}).get('products', [])
            
            if not products:
                print("Pencarian selesai (tidak ada produk).")
                break
            
            # Ekstrak TCIN dari setiap produk di halaman ini
            batch_tcin = [p.get('tcin') for p in products if p.get('tcin')]
            all_tcin.extend(batch_tcin)
            
            print(f"Sukses! Mendapat {len(batch_tcin)} TCIN. (Total: {len(all_tcin)})")
            
        elif response.status_code == 404:
            print("404 Terdeteksi (Deep Paging Limit). Berhenti.")
            break
        else:
            print(f"Gagal (Status: {response.status_code})")
            
        # Jeda antar request (opsional, disesuaikan agar tidak kena block)
        time.sleep(random.uniform(1.0, 2.0))
        
    except Exception as e:
        print(f"Error: {e}")
        continue

# --- Simpan Data ---
# 1. Simpan dalam bentuk list JSON
with open('target_tcin_list.json', 'w') as f:
    json.dump(all_tcin, f, indent=4)

# 2. Simpan dalam bentuk teks (satu TCIN per baris) agar mudah dibaca
with open('target_tcin_raw.txt', 'w') as f:
    for tcin in all_tcin:
        f.write(f"{tcin}\n")

print("-" * 30)
print(f"SELESAI! Total TCIN unik terkumpul: {len(set(all_tcin))}")
print("Data disimpan di 'target_tcin_list.json' dan 'target_tcin_raw.txt'")