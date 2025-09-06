# import json

# def get_product_json(product_url):
#     print(f"Ambil JSON dari: {product_url}")
#     soup_product = get_soup(product_url)
#     if not soup_product:
#         print("Gagal ambil halaman produk")
#         return None

#     # Cari script dengan type application/ld+json
#     script_tag = soup_product.find("script", type="application/ld+json")
#     if not script_tag:
#         print("JSON tidak ditemukan di halaman produk")
#         return None

#     try:
#         data = json.loads(script_tag.string)
#         return data
#     except json.JSONDecodeError:
#         print("Gagal parse JSON")
#         return None


# # Cara pakai
# product_url = "https://www.contentbeautywellbeing.com/products/ere-perez-coco-crayon?variant=39763144048721"
# product_data = get_product_json(product_url)

# if product_data:
#     print("Nama produk:", product_data.get("name"))
#     print("Brand:", product_data.get("brand", {}).get("name"))
#     print("URL produk:", product_data.get("url"))
#     print("Jumlah variasi:", len(product_data.get("hasVariant", [])))
