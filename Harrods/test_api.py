# # import requests
# # import json

# # url = "https://w3dhihsi98-1.algolianet.com/1/indexes/*/queries"

# # headers = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
# #     "Accept": "*/*",
# #     "Referer": "https://www.harrods.com/",
# #     "Origin": "https://www.harrods.com",
# #     "Content-Type": "application/json",
# #     "x-algolia-agent": "Algolia for JavaScript (4.24.0); Browser (lite)",
# #     "x-algolia-api-key": "86699d9befae1ab20f0f0138cd622e0e",
# #     "x-algolia-application-id": "W3DHIHSI98"
# # }

# # payload = {
# #     "requests": [
# #         {
# #             "indexName": "prod_harrods.com",
# #             "query": "",
# #             "params": "facets=%5B%22*%22%5D&clickAnalytics=true&ruleContexts=%5B%22USD%22%5D&maxValuesPerFacet=1000&facetFilters=%5B%5B%22categoryPageIdentifier%3AMake%20Up%3EFace%3EFoundations%22%5D%5D&offset=0&length=60"
# #         }
# #     ]
# # }

# # resp = requests.post(url, headers=headers, json=payload)
# # print(resp.status_code)
# # print(json.dumps(resp.json(), indent=2))



# import requests
# import json

# url = "https://w3dhihsi98-1.algolianet.com/1/indexes/*/queries"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
#     "Accept": "*/*",
#     "Referer": "https://www.harrods.com/",
#     "Origin": "https://www.harrods.com",
#     "Content-Type": "application/json",
#     "x-algolia-agent": "Algolia for JavaScript (4.24.0); Browser (lite)",
#     "x-algolia-api-key": "86699d9befae1ab20f0f0138cd622e0e",
#     "x-algolia-application-id": "W3DHIHSI98"
# }

# payload = {
#     "requests": [
#         {
#             "indexName": "prod_harrods.com",
#             "query": "",
#             "params": "facets=%5B%22*%22%5D&clickAnalytics=true&ruleContexts=%5B%22USD%22%5D&maxValuesPerFacet=1000&facetFilters=%5B%5B%22categoryPageIdentifier%3AMake%20Up%3EFace%3EFoundations%22%5D%5D&offset=0&length=60"
#         }
#     ]
# }

# resp = requests.post(url, headers=headers, json=payload)

# if resp.status_code == 200:
#     data = resp.json()
#     # Simpan ke file JSON
#     with open("---harrods_data.json", "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)
#     print("✅ Data berhasil disimpan ke harrods_data.json")
# else:
#     print(f"❌ Error {resp.status_code}: {resp.text}")



import requests
import json
import math

url = "https://w3dhihsi98-1.algolianet.com/1/indexes/*/queries"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "*/*",
    "Referer": "https://www.harrods.com/",
    "Origin": "https://www.harrods.com",
    "Content-Type": "application/json",
    "x-algolia-agent": "Algolia for JavaScript (4.24.0); Browser (lite)",
    "x-algolia-api-key": "86699d9befae1ab20f0f0138cd622e0e",
    "x-algolia-application-id": "W3DHIHSI98"
}

all_hits = []
hits_per_page = 60

# --- ambil total items dulu (nbHits) ---
payload = {
    "requests": [
        {
            "indexName": "prod_harrods.com",
            "query": "",
            "params": "facets=%5B%22*%22%5D&clickAnalytics=true&ruleContexts=%5B%22USD%22%5D&maxValuesPerFacet=1000&facetFilters=%5B%5B%22categoryPageIdentifier%3AMake%20Up%3EFace%3EFoundations%22%5D%5D&offset=0&length=60"
        }
    ]
}

resp = requests.post(url, headers=headers, json=payload)
data = resp.json()
# nb_hits = data["results"][0]["nbHits"]


hits = data["results"][0]["hits"]

for item in hits:
    product_id = item.get("product_id")
    referenceKey = item.get("referenceKey")
    name = item.get("name")
    brand = item.get("brand")

    print(f"ID: {product_id} | Ref: {referenceKey} | Name: {name} | Brand: {brand}")


# total_pages = math.ceil(nb_hits / hits_per_page)
# print(f"Total items: {nb_hits}, Total pages: {total_pages}")

# --- loop semua halaman ---
# for page in range(total_pages):
#     offset = page * hits_per_page
#     print(f"📥 Mengambil data offset {offset}")

#     payload["requests"][0]["params"] = (
#         f"facets=%5B%22*%22%5D&clickAnalytics=true&ruleContexts=%5B%22USD%22%5D"
#         f"&maxValuesPerFacet=1000&facetFilters=%5B%5B%22categoryPageIdentifier%3AMake%20Up%3EFace%3EFoundations%22%5D%5D"
#         f"&offset={offset}&length={hits_per_page}"
#     )

#     resp = requests.post(url, headers=headers, json=payload)
#     page_data = resp.json()

#     # simpan semua "hits" (produk)
#     all_hits.extend(page_data["results"][0]["hits"])
    


# --- simpan ke file JSON ---
# with open("harrods_all_products.json", "w", encoding="utf-8") as f:
#     json.dump(all_hits, f, indent=2, ensure_ascii=False)

# print(f"✅ Selesai! Total produk tersimpan: {len(all_hits)}")
