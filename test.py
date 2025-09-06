# import requests
# import re
# import json
# import time
# import csv
# from bs4 import BeautifulSoup




# # URL target
# url = 'https://ohmycream.co.uk/collections/skincare'

# # # Kirim permintaan HTTP
# headers = {
#     "User-Agent": "Mozilla/5.0"
# }
# response = requests.get(url, headers=headers)
# soup = BeautifulSoup(response.text, "html.parser")





# # # --- 1. Ambil JSON dari "variationData" dalam script biasa ---
# # variation_json = None

# script_tags = soup.find_all("script")[37]
# print(script_tags)
# # for tag in script_tags:
# #     if "data-events" in tag.text:
# #         match = re.search(r'data-events\s*=\s*(\[\{.*?\}\]);', tag.text, re.DOTALL)
# #         if match:
# #             json_str = match.group(1)
# #             try:
# #                 variation_json = json.loads(json_str)
# #             except json.JSONDecodeError as e:
# #                 print("Gagal parse variationData:", e)
# #             break

# # # --- 2. Ambil JSON dari <script type="application/ld+json" id="bv-jsonld-bvloader-summary"> ---
# # rating_json = None

# # script_rating = soup.find("script", {"type": "application/ld+json"})
# # # print(script_rating)
# # if script_rating:
# #     try:
# #         rating_json = json.loads(script_rating.string)
# #     except json.JSONDecodeError as e:
# #         print("Gagal parse bvloader summary:", e)

# # # --- Tampilkan hasil ---
# # print("\n--- variationData ---")
# # print(json.dumps(variation_json))

# # print("\n--- bvloader-summary ---")
# # print(json.dumps(rating_json, indent=2))




import requests
from bs4 import BeautifulSoup
import json

url = "https://ohmycream.co.uk/collections/make-up/products/ilia-multi-stick"  # ganti dengan URL halaman produk
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

rating = None
review_count = None

# Cari semua script dengan type application/ld+json
for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.string)

        # Cek apakah ini dictionary dan punya 'aggregateRating'
        if isinstance(data, dict) and "aggregateRating" in data:
            agg = data["aggregateRating"]
            rating = agg.get("ratingValue")
            review_count = agg.get("reviewCount")
            break

        # Kadang data bisa berupa list
        if isinstance(data, list):
            for item in data:
                if "aggregateRating" in item:
                    agg = item["aggregateRating"]
                    rating = agg.get("ratingValue")
                    review_count = agg.get("reviewCount")
                    break

    except Exception:
        continue

print("Rating:", rating)
print("Review Count:", review_count)
