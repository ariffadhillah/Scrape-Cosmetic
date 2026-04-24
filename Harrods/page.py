import requests
import re
import json
from bs4 import BeautifulSoup
import time
import csv


# BASE_URL = "https://www.harrods.com/en-us/p/gucci-rouge-de-beaute-brillant-glow-and-care-lip-colour-000000000007837904"
# BASE_URL = "https://www.harrods.com/en-us/p/maison-crivelli-hibiscus-mahajad-perfume-extract-50ml-000000000007266634"
BASE_URL = "https://www.harrods.com/en-us/p/dolce-and-gabbana-everlast-concealer-000000000007871118"
CATEGORY_URL = BASE_URL + "/c/make-up/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Connection": "keep-alive"
}


res = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(res.text, "html.parser")

find_json_page = soup.find_all("script", {"type": "application/ld+json"})[2]
if find_json_page:
    try:
        data = json.loads(find_json_page.string)
        # tampilkan rapi dengan indent
        product_desc = data.get("name","")
        product_brand = data.get("brand",{}).get("name","")
        print(product_desc)
        print(product_brand)
        hasVariant = data.get("hasVariant",{})
        # print(hasVariant)

        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("⚠️ Error parse JSON reviews:", e)




# import requests
# import re
# import json
# from bs4 import BeautifulSoup
# import time
# import csv
# BASE_URL = "https://www.harrods.com/en-us/p/maison-crivelli-hibiscus-mahajad-perfume-extract-50ml-000000000007266634"
# BASE_URL = "https://www.harrods.com/en-us/p/dolce-and-gabbana-everlast-concealer-000000000007871118"
# CATEGORY_URL = BASE_URL + "/c/make-up/"
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Referer": BASE_URL,
#     "Origin": BASE_URL,
#     "Connection": "keep-alive"
# }


# res = requests.get(BASE_URL, headers=HEADERS)
# soup = BeautifulSoup(res.text, "html.parser")

# find_json_page = soup.find_all("script", {"type": "application/ld+json"})[2]
# if find_json_page:
#     try:
#         data = json.loads(find_json_page.string)

#         # ambil name utama
#         main_name = data.get("name", "")
#         print(f"Product Group: {main_name}\n")

#         # ambil varian
#         variants = data.get("hasVariant", [])
#         for variant in variants:
#             v_name = variant.get("name", "")
#             v_sku = variant.get("sku", "")
#             print(f"- {v_name} | SKU: {v_sku}")

#     except Exception as e:
#         print("⚠️ Error parse JSON reviews:", e)

