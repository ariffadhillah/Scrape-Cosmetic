# # import requests
# # import json

# # url = (
# #     "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
# #     "?category=mpo32"
# #     "&count=24"
# #     "&default_purchasability_filter=false"
# #     "&include_sponsored=true"
# #     "&include_review_summarization=true"
# #     "&offset=24"
# #     "&page=%2Fc%2Fmpo32"
# #     "&platform=desktop"
# #     "&pricing_store_id=3991"
# #     "&spellcheck=true"
# #     "&visitor_id=019A5E13904B02019657CA5992C340A5"
# #     "&zip=23362"
# #     "&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
# #     "&channel=WEB"
# #     "&include_dmc_dmr=false"
# #     "&useragent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%3B+rv%3A144.0%29+Gecko/20100101+Firefox/144.0"
# # )

# # headers = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
# #     "Accept": "application/json",
# #     "Accept-Language": "en-US,en;q=0.5",
# #     "Referer": "https://www.target.com/c/makeup-deals/-/N-mpo32",
# #     "Origin": "https://www.target.com",
# #     "Connection": "keep-alive",

# #     # kamu TETAP bisa pakai cookie panjang di sini
# #     # tapi sudah ditata agar tidak bikin kepala muter
# #     "Cookie": (
# #         "TealeafAkaSid=YsVRkMzAPJiazPM5yMbIr8j0JQefm2iK; "
# #         "adScriptData=01; "
# #         "visitorId=019A5E13904B02019657CA5992C340A5; "
# #         "sapphire=1; "
# #         "_pxvid=f2e34917-bbcc-11f0-adc4-40395ab7d28f; "
# #         "_tgt_session=ff036d1c9d0144e38bab07486535dc65; "
# #         # sisanya sangat panjang, tapi kamu tetap bisa paste kalau mau
# #     ),

# #     "Sec-Fetch-Dest": "empty",
# #     "Sec-Fetch-Mode": "cors",
# #     "Sec-Fetch-Site": "same-site",
# #     "Priority": "u=4",
# #     "TE": "trailers"
# # }

# # response = requests.get(url, headers=headers)
# # # print(response.text)

# # data = response.json()
# # products = data["data"]["search"].get("products", [])

# # products = data["data"]["search"].get("products", [])

# # for i, p in enumerate(products):
# #     # 1. Coba ambil dari parent
# #     url = (
# #         p.get("parent", {})
# #          .get("item", {})
# #          .get("enrichment", {})
# #          .get("buy_url")
# #     )

# #     # 2. Kalau gagal → fallback ke item.enrichment
# #     if not url:
# #         url = (
# #             p.get("item", {})
# #              .get("enrichment", {})
# #              .get("buy_url")
# #         )

# #     # 3. Validasi URL asli Target
# #     if isinstance(url, str) and "/p/" in url and "/A-" in url:
# #         print(f"Produk #{i} → {url}")
# #     else:
# #         print(f"Produk #{i} → None")




# import requests
# import re
# import json

# def extract_tcin(url):
#     """Ambil TCIN dari buy_url"""
#     match = re.search(r'/A-(\d+)', url)
#     return match.group(1) if match else None


# # --- API dari PLP ---
# url = (
#     "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
#     "?category=mpo32&count=24&default_purchasability_filter=false"
#     "&include_sponsored=true&include_review_summarization=true"
#     "&offset=24&page=%2Fc%2Fmpo32&platform=desktop&pricing_store_id=3991"
#     "&spellcheck=true&visitor_id=019A5E13904B02019657CA5992C340A5&zip=23362"
#     "&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB"
#     "&include_dmc_dmr=false"
# )

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
#     "Accept": "application/json"
# }

# resp = requests.get(url, headers=headers).json()
# products = resp["data"]["search"].get("products", [])


# for i, p in enumerate(products):

#     # Ambil buy_url
#     buy_url = (
#         p.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url")
#         or p.get("item", {}).get("enrichment", {}).get("buy_url")
#     )

#     print("\n==============================")
#     print(f"Produk #{i}")
#     print("buy_url:", buy_url)

#     if not buy_url:
#         print("Tidak ada buy_url")
#         continue

#     # Ambil TCIN
#     tcin = extract_tcin(buy_url)
#     print("TCIN:", tcin)

#     if not tcin:
#         print("TCIN tidak ditemukan.")
#         continue

#     # Panggil API detail produk
#     detail_url = (
#         f"https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
#         f"?tcin={tcin}&pricing_store_id=3991"
#         f"&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
#     )

#     detail_resp = requests.get(detail_url, headers=headers)
#     data_detail = detail_resp.json()

#     # Tampilkan JSON mentah untuk cek dulu
#     print("Detail JSON:")
#     print(json.dumps(data_detail, indent=2))



import requests
import re

url = (
    "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
    "?category=mpo32&count=24&default_purchasability_filter=false"
    "&include_sponsored=true&include_review_summarization=true"
    "&offset=24&page=%2Fc%2Fmpo32&platform=desktop&pricing_store_id=3991"
    "&spellcheck=true&visitor_id=019A5E13904B02019657CA5992C340A5&zip=23362"
    "&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB"
    "&include_dmc_dmr=false"
)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

resp = requests.get(url, headers=headers).json()

# 1. Ambil total product count jika ada
search_data = resp.get("data", {}).get("search", {})

total_results = search_data.get("total_results")
product_count = search_data.get("product_count")

print("=== INFO JUMLAH DATA ===")
print("total_results :", total_results)
print("product_count :", product_count)

# 2. Ambil list products
products = search_data.get("products", [])
print("Jumlah item dalam products[] :", len(products))

# 3. Print semua TCIN
print("\n=== DAFTAR SEMUA TCIN ===")
def extract_tcin(buy_url):
    if not buy_url: return None
    m = re.search(r'/A-(\d+)', buy_url)
    return m.group(1) if m else None

for i, p in enumerate(products):
    buy_url = (
        p.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url")
        or p.get("item", {}).get("enrichment", {}).get("buy_url")
    )
    tcin = extract_tcin(buy_url)
    print(f"{i}. TCIN:", tcin)
