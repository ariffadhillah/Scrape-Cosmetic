from bs4 import BeautifulSoup
import requests
import json
import re
import os
import csv

walmart_data = []

major_Category = "Skincare"
category_name = 'Face Masks'

filename = f"{major_Category}-{category_name}.csv"
fields = ["Product ID", "SKU ID","Product Name","Product Maker","Varian/color","Product Url","Major Category","Category","Ingredients", "Product Image URL", "Price"]




# url = "https://www.neimanmarcus.com/p/maison-francis-kurkdjian-baccarat-rouge-540-extrait-de-parfum-2-4-oz-prod203310173?childItemId=NMC4LTY_&msid=4186589&navpath=cat000000_cat000285&page=0&position=0"
# url = "https://www.neimanmarcus.com/p/dior-dior-addict-lip-maximizer-gloss-prod259640088"
# url = "https://www.neimanmarcus.com/p/bvlgari-eau-parfumee-the-blanc-body-shower-gel-10-1-oz-prod282740027?childItemId=NMC6CFD_&msid=5065063&navpath=cat000000_cat000285&page=1&position=104"

# url = "https://www.neimanmarcus.com/p/dior-dior-addict-lip-maximizer-gloss-prod259640088"
# url = 'https://www.neimanmarcus.com/p/dior-dior-forever-matte-foundation-spf-15-1-oz-prod248300029'
# url = 'https://www.neimanmarcus.com/p/bvlgari-eau-parfumee-the-blanc-body-shower-gel-10-1-oz-prod282740027'
# url = 'https://www.neimanmarcus.com/p/bvlgari-eau-parfumee-the-blanc-body-shower-gel-10-1-oz-prod282740027'
url ='https://www.neimanmarcus.com/p/dior-sauvage-eau-de-parfum-3-4-oz-prod208780232?childItemId=NMC4QNM_&msid=4418049&navpath=cat000000_cat000285_cat10470744&page=0&position=3'
# url = 'https://www.neimanmarcus.com/p/creed-aventus-3-4-oz-prod222150059?childItemId=NMC5AMY_&msid=2220365&navpath=cat000000_cat000285_cat10470744&page=0&position=5'
# url = 'https://www.neimanmarcus.com/p/sisley-paris-hair-rituel-gentle-purifying-shampoo-prod254650167?childItemId=NMC5S2N_&msid=4392260&navpath=cat000000_cat000285_cat55180733_cat51180746&page=0&position=11'

# datadome = "4jQ5WyQjhoFX26LieZUgMUbUfvPrhgCXJE3afl6PKdXQ_Gr_KhB~ivI07IgNhl75~N7LiK5UQ62GhVk3_ox9mJhlqWZrH0edZ7nzqkCRhCaAWQqjOqz3SqdCb4lfwXoT; Max-Age=31536000; Domain=.neimanmarcus.com; Path=/; Secure; SameSite=Lax"

def load_datadome_cookie(path="datadome.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
datadome = load_datadome_cookie()


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


response = requests.get(
    url,
    headers=headers,
    cookies=cookies,
    timeout=20
)

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)


html = response.text

pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
match = re.search(pattern, html, re.DOTALL)

if not match:
    raise Exception("❌ __NEXT_DATA__ tidak ditemukan di response")

next_data_raw = match.group(1)

# parse ke dict Python
next_data = json.loads(next_data_raw)


def extract_active_price(product_data):
    for child in product_data.get("childProducts", []):
        price = child.get("price")
        if price:
            return {
                "retail": price.get("retailPrice"),
                "currency": price.get("currencyCode")
            }
    return None

def build_price_sources(product_data):
    price_map = {}

    # 1️⃣ childProducts (harga spesifik SKU)
    for child in product_data.get("childProducts", []):
        pid = child.get("id")
        price = child.get("price", {})

        if pid and price.get("retailPrice"):
            price_map[pid] = price.get("retailPrice")

    # 2️⃣ root product price
    root_price = (
        product_data.get("price", {}).get("retailPrice")
    )

    # 3️⃣ price range fallback
    range_price = (
        product_data.get("priceRange", {}).get("lowPrice")
    )

    return price_map, root_price, range_price


def map_sku_to_price(product_data):
    result = {}

    for child in product_data.get("childProducts", []):
        price = child.get("price", {}).get("retailPrice")

        options = child.get("options", {}).get("productOptions", [])
        for opt in options:
            if opt.get("label") == "size":
                for val in opt.get("values", []):
                    sku_id = val.get("skuId")
                    result[sku_id] = price

    return result





def extract_brand(product_data):
    # 1️⃣ langsung di productData
    attributes = product_data.get('attributesMap')
    if attributes and attributes.get('brandName'):
        return attributes['brandName'][0]

    # 2️⃣ di skus
    for sku in product_data.get('skus', []):
        attrs = sku.get('attributesMap')
        if attrs and attrs.get('brandName'):
            return attrs['brandName'][0]

    # 3️⃣ di originalSkus
    for sku in product_data.get('childProducts', []):
        attrs = sku.get('attributesMap')
        if attrs and attrs.get('brandName'):
            return attrs['brandName'][0]

    return None



# def extract_ingredients_from_longdesc(long_desc: str) -> str | None:
#     if not long_desc:
#         return None

#     # 1. Parse HTML → text
#     soup = BeautifulSoup(long_desc, "html.parser")
#     text = soup.get_text(separator="\n")

#     # 2. Rapikan whitespace
#     text = re.sub(r"\n+", "\n", text).strip()

#     patterns = [
#         # CASE 1 — Ingredients*:
#         r"Ingredients\*:\s*(.+?)(?:\n\*Please Note|\nPlease|\Z)",

#         # CASE 2 — Ingredients Listing
#         r"Ingredients Listing\s*(.+?)(?:\n[A-Z][a-z ]+:|\n\d+(\.\d+)?\s*oz|\Z)",
#     ]

#     for pattern in patterns:
#         match = re.search(pattern, text, re.DOTALL)
#         if match:
#             ingredients = match.group(1).strip()

#             # 3. Hapus ukuran produk kalau masih nyempil
#             ingredients = re.sub(
#                 r"\s*\d+(\.\d+)?\s*oz\s*/\s*\d+\s*mL.*$",
#                 "",
#                 ingredients,
#                 flags=re.IGNORECASE
#             ).strip()

#             return ingredients

#     return None


def extract_ingredients_from_longdesc(long_desc: str) -> str | None:
    if not long_desc:
        return None

    soup = BeautifulSoup(long_desc, "html.parser")
    text = soup.get_text(separator="\n")

    # Rapikan whitespace
    text = re.sub(r"\u00a0", " ", text)   # NBSP
    text = re.sub(r"\n+", "\n", text).strip()

    patterns = [
        # CASE 1 — Ingredients*, Ingredients * , Ingredients :
        r"Ingredients\*:\s*(.+?)(?:\n\*Please Note|\nPlease|\Z)",

        # r"Ingredients\s*\*?\s*:?\s*\n(.+?)(?:\n\s*\*?Please Note|\n\s*Please Note|\Z)",

        # CASE 2 — Ingredients Listing
        r"Ingredients Listing\s*(.+?)(?:\n[A-Z][a-z ]+:|\n\d+(\.\d+)?\s*oz|\Z)",

        # CASE 3 — Ingredients tanpa marker Please Note
        r"Ingredients\s*\*?\s*:?\s*\n(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            ingredients = match.group(1).strip()

            # Stop kalau kepotong section lain
            ingredients = re.split(
                r"\n(?:How To Use|Shade Descriptions|Pairs Well With|Clinical Results)",
                ingredients,
                flags=re.IGNORECASE
            )[0].strip()

            # Hapus ukuran produk
            ingredients = re.sub(
                r"\s*\d+(\.\d+)?\s*oz\s*/\s*\d+\s*mL.*$",
                "",
                ingredients,
                flags=re.IGNORECASE
            ).strip()

            return ingredients


ingredients = extract_ingredients_from_longdesc(
    next_data['props']['pageProps']['productData']['details']['longDesc']
)
# print("ingredients =", ingredients)

# ingredients_raw = next_data['props']['pageProps']['productData']['details']['longDesc']


product_data = next_data['props']['pageProps']['productData']
price = extract_active_price(product_data)
productBrand = extract_brand(product_data)



# print("Price Data =", price_data)
price_map, root_price, range_price = build_price_sources(product_data)
productName = next_data['props']['pageProps']['productData']['name']
skus = next_data['props']['pageProps']['productData']['skus']

# for sku in skus:
# for sku in product_data.get("skus", []):
#     skuId = sku.get('id')
#     productId = sku.get('productId')
#     # price = sku.get('price')
#     # productName = sku.get('productName')

#     # ambil color atau size
#     name = (
#         sku.get('color', {}).get('name')
#         or sku.get('size', {}).get('name')
#     )

#     image_url = (
#         sku
#         .get('media', {})
#         .get('main', {})
#         .get('dynamic', {})
#         .get('url')
#     )

#     print("Sku ID =", skuId)
#     print("Product Name =", productName)
#     print("Product ID =", productId)
#     print("Product Maker =", productBrand)
#     print("Varian/color =", name)
#     print("Price Data =", price)
#     print("product Url =", url)
#     print("image_url =", image_url)
#     print("ingredients  =", ingredients)
#     print("=" * 40)

# for sku in skus:
#     skuId = sku.get('id')
#     productId = sku.get('productId')
#     # price = sku.get('price')
#     # productName = sku.get('productName')

#     # ambil color atau size
#     name = (
#         sku.get('color', {}).get('name')
#         or sku.get('size', {}).get('name')
#     )

#     image_url = (
#         sku
#         .get('media', {})
#         .get('main', {})
#         .get('dynamic', {})
#         .get('url')
#     )

#     print("Sku ID =", skuId)
#     print("Product Name =", productName)
#     print("Product ID =", productId)
#     print("Product Maker =", productBrand)
#     print("Varian/color =", name)
#     print("Price Data =", price)
#     print("product Url =", url)
#     print("image_url =", image_url)
#     print("ingredients  =", ingredients)
#     print("=" * 40)




for sku in product_data.get("skus", []):
    skuId = sku.get("id")
    productId = sku.get("productId")

    item_varian = (
        sku.get("color", {}).get("name")
        or sku.get("size", {}).get("name")
    )

    image_url = (
        sku.get("media", {})
        .get("main", {})
        .get("dynamic", {})
        .get("url")
    )

    # ✅ PRIORITAS HARGA YANG BENAR
    price = (
        price_map.get(productId)
        or root_price
        or range_price
    )

    print("Sku ID =", skuId)
    print("Product Name =", productName)
    print("Product ID =", productId)
    print("Product Maker =", productBrand)
    print("Varian/color =", item_varian)
    print("Price =", price)
    print("product Url =", url)
    print("image_url =", image_url)
    print("ingredients =", ingredients)
    # print("ingredients =", ingredients_raw)
    print("=" * 40)

    data_walmart = {
        "Product ID": productId,
        "SKU ID": skuId,
        "Product Name": productName,
        "Product Maker": productBrand,
        "Product Url":  url,
        "Major Category": major_Category,
        "Category": category_name,
        "Ingredients" : ingredients,
        "Product Image URL": image_url,
        "Price": price,
        "Varian/color": item_varian
    }
    walmart_data.append(data_walmart)
    print('Saving', data_walmart['Product Url'])
    
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_walmart)
