import requests
import json

# url = "https://pdp-api.public.prd.beautybay.com/product/beauty-bay-high-key-volume-mascara"
url = "https://pdp-api.public.prd.beautybay.com/product/medicube-collagen-night-wrapping-mask"
# url = "https://pdp-api.public.prd.beautybay.com/product/numbuzin-no1-centella-re-leaf-green-toner-pad"
# url = "https://pdp-api.public.prd.beautybay.com/product/niod-fractionated-eye-contour-concentrate"
# url = "https://pdp-api.public.prd.beautybay.com/product/beauty-bay-powder-bronzer"
# url = "https://pdp-api.public.prd.beautybay.com/product/danessa-myricks-beauty-yummy-skin-blurring-balm-powder"
# url = "https://pdp-api.public.prd.beautybay.com/product/medicube-collagen-night-wrapping-mask"
# url = "https://pdp-api.public.prd.beautybay.com/product/beauty-of-joseon-revive-serum-ginseng-snail-mucin"

# response = requests.get(url)

# # kalau mau tampilkan JSON rapi
# json_detail = response.json()
# print(json.dumps(json_detail, indent=4, ensure_ascii=False))

# product_id = json_detail.get("sku","")
# product_name = json_detail.get("name","")
# brand_raw = json_detail.get("brand", {}).get("name","")
# # brand = brand_raw.get("", {})

# if "variants" in json_detail:
#     inStock = json_detail.get("variants",{})
#     for data_instock in inStock['inStock']:
#         name_inStock = data_instock.get("name")
#         sku_id = data_instock.get("sku")
#         imageUrl = data_instock.get("imageUrl")
#         product_desc = product_name +" "+ name_inStock    
#         print(f"Brand: {brand_raw}")
#         print(f"Product Desc: {product_desc}")
#         print("SKU Id:",sku_id)
#         print("Image Url :",imageUrl)
#         print()
    
# else:    
#     print("Brand:",brand_raw)
#     print("Product Id:",product_id)


import requests
import json

def parse_product_detail(json_detail):
    """
    Parse detail produk BeautyBay dari JSON API.
    Mengembalikan list dict dengan format konsisten.
    """

    results = []

    # --- data umum ---
    product_id = json_detail.get("sku", "")
    product_name = json_detail.get("name", "")
    brand = json_detail.get("brand", {}).get("name", "")
    measurement = json_detail.get("measurement", "")
    url_product_canonical = json_detail.get("seoData", {}).get("canonical","")
    ingredients = json_detail.get("ingredients", "")
    reviewSummary = json_detail.get("reviewSummary", {})
    reviewcount = reviewSummary.get("count", "")
    overallRating = reviewSummary.get("overallRating", "")

    # --- cek apakah ada variants ---
    variants = json_detail.get("variants")

    if isinstance(variants, dict) and ("inStock" in variants or "outOfStock" in variants):
        # Loop keduanya
        for stock_key in ["inStock", "outOfStock"]:
            if stock_key in variants:
                for data_variant in variants[stock_key]:
                    name_variant = data_variant.get("name", "")
                    measurement_variant = data_variant.get("measurement", "")
                    product_id = data_variant.get("sku")
                    url_variants = data_variant.get("url", "")
                    imageUrl = data_variant.get("imageUrl", "")

                    # --- susun product_desc ---
                    base_name = product_name
                    parts = [base_name]

                    if measurement_variant:
                        parts.append(measurement_variant)
                    if name_variant:
                        parts.append(name_variant)

                    # Gabungkan
                    product_desc = " ".join(parts)

                    # Hilangkan duplikat kata (misal "60ml 60ml")
                    tokens = product_desc.split()
                    seen = []
                    clean_tokens = []
                    for t in tokens:
                        if t not in seen:
                            clean_tokens.append(t)
                            seen.append(t)
                    product_desc = " ".join(clean_tokens)

                    results.append({
                        "brand": brand,
                        "product_id": product_id,
                        "product_desc": product_desc,
                        "image_url": imageUrl,
                        "url product canonical": f"{url_product_canonical}{url_variants}",
                        "stock_status": stock_key,  # inStock / outOfStock
                        "ingredients": ingredients,
                        "review": reviewcount,
                        "overallRating": overallRating
                    })
    else:
        # Produk tanpa variasi        
        image_list = json_detail.get("media", {}).get("images", [])
        first_image = image_list[0] if image_list else ""

        results.append({
            "brand": brand,
            "product_id": product_id,
            "product_desc": f"{product_name} {measurement}".strip(),
            "url_variants": "",
            "image_url": first_image,
            "url product canonical": url_product_canonical,
            "ingredients": ingredients,
            "review": reviewcount,
            "overallRating": overallRating,
            "stock_status": "unknown"
        })

    return results


# ==== Contoh penggunaan ====

response = requests.get(url)
data = response.json()
parsed = parse_product_detail(data)

for item in parsed:
    print(f"product_desc: {item['product_desc']}")
    print(f"Product Id: {item['product_id']}")
    print(f"Url Product: {item['url product canonical']}")
    print(f"Url Image: {item['image_url']}")
    print(f"Ingredients: {item['ingredients']}")
    print(f"Review: {item['review']}")
    print(f"Overall Rating: {item['overallRating']}")
    print(f"Stock Status: {item['stock_status']}")
    print("="*80)


# def parse_product_detail(json_detail):
#     # print(json.dumps(json_detail, indent=4, ensure_ascii=False))
#     """
#     Parse detail produk BeautyBay dari JSON API.
#     Mengembalikan list dict dengan format konsisten.
#     """

#     results = []

#     # --- data umum ---
#     product_id = json_detail.get("sku", "")
#     product_name = json_detail.get("name", "")
#     brand = json_detail.get("brand", {}).get("name", "")
#     measurement = json_detail.get("measurement", "")
#     url = json_detail.get("measurement", "")
#     url_product_canonical = json_detail.get("seoData", {}).get("canonical","")
#     ingredients = json_detail.get("ingredients", "")
#     reviewSummary = json_detail.get("reviewSummary", {})
#     reviewcount = reviewSummary.get("count", "")
#     overallRating = reviewSummary.get("overallRating", "")
#     # reviewcount = json_detail.get("reviewSummary", {}).get("count","")
#     # overallRating = json_detail.get("reviewSummary", {}).get("overallRating","")

#     # --- cek apakah ada variants ---
#     # variants = json_detail.get("variants")

#     # if variants and "inStock" in variants:  
#     #     # Produk punya variasi (loop setiap variant)
#     #     for data_instock in variants["inStock"]:
#     #         name_inStock = data_instock.get("name")
#     #         product_id = data_instock.get("sku")
#     #         url_variants = data_instock.get("url")
#     #         imageUrl = data_instock.get("imageUrl")
#     #         product_desc = f"{product_name} {name_inStock}" if name_inStock else product_name

#     #         results.append({
#     #             "brand": brand,
#     #             "product_id": product_id,
#     #             # "measuremen":"",
#     #             # "sku_id": sku_id,
#     #             "product_desc":f"{product_desc}",
#     #             # "url_variants": url_variants,
#     #             "image_url": imageUrl,
#     #             "url product canonical": f"{url_product_canonical}{url_variants}"
#     #         })
#     # else:
#     #     # Produk tanpa variasi
#     #     image_list = json_detail.get("media", {}).get("images", [])
#     #     first_image = image_list[0] if image_list else ""
        

#     #     results.append({
#     #         "brand": brand,
#     #         "product_id": product_id,
#     #         # "measuremen": "",
#     #         # "sku_id": product_id,   
#     #         "product_desc":f"{product_name}{measurement}",
#     #          "url_variants": "",
#     #         "image_url": first_image,
#     #         "url product canonical": url_product_canonical
#     #     })





#     # --- cek apakah ada variants ---
#     variants = json_detail.get("variants")

#     if isinstance(variants, dict) and ("inStock" in variants or "outOfStock" in variants):
#         # Loop keduanya
#         for stock_key in ["inStock", "outOfStock"]:
#             if stock_key in variants:
#                 for data_variant in variants[stock_key]:
#                     name_variant = data_variant.get("name")
#                     measurement_ = data_variant.get("measurement", "")
#                     product_id = data_variant.get("sku")
#                     url_variants = data_variant.get("url")
#                     imageUrl = data_variant.get("imageUrl")
#                     product_desc = f"{product_name} {measurement_} {name_variant}" if name_variant else product_name

#                     results.append({
#                         "brand": brand,
#                         "product_id": product_id,
#                         "product_desc": f"{product_desc}",
#                         "image_url": imageUrl,
#                         "url product canonical": f"{url_product_canonical}{url_variants}",
#                         "stock_status": stock_key,  # inStock / outOfStock
#                         "ingredients": ingredients,
#                         "review": reviewcount,
#                         "overallRating": overallRating
#                     })
#     else:
#         # Produk tanpa variasi        
#         image_list = json_detail.get("media", {}).get("images", [])
#         first_image = image_list[0] if image_list else ""

#         results.append({
#             "brand": brand,
#             "product_id": product_id,
#             "product_desc": f"{product_name}{measurement}",
#             "url_variants": "",
#             "image_url": first_image,
#             "url product canonical": url_product_canonical,
#             "ingredients": ingredients,
#             "review": reviewcount,
#             "overallRating": overallRating,
#             "stock_status": "unknown"
#         })



#     return results


# # response = requests.get(url)

# for url in [url]:
#     response = requests.get(url)
#     data = response.json()
#     parsed = parse_product_detail(data)

#     print(f"🔎 URL: {url}")
#     for item in parsed:
#         product_desc = item.get("product_desc", "")
#         product_id = item.get("product_id", "")
#         # sku_id = item.get("sku_id", "")
#         url_product = item.get( "url product canonical", "")
#         url_image = item.get( "image_url", "")
#         ingredients = item.get("ingredients", "")
#         rating = item.get("review", "")
#         user_reviews = item.get("overallRating", "")

#         print(f"product_desc: {product_desc}")
#         print(f"Product Id: {product_id}")
#         print(f"SKU Id: {product_id}")
#         print(f"Url Product: {url_product}")
#         print(f"Url Image: {url_image}")
#         print(f"Ingredients: {ingredients}")
#         print(f"Review: {rating}")
#         print(f"User Reviews: {user_reviews}")
#         print("="*80)
#         print()

        # print(json.dumps(item, indent=2, ensure_ascii=False))

# json_detail = response.json()
# print(json.dumps(json_detail, indent=4, ensure_ascii=False))
# # --- data umum ---
# product_id = json_detail.get("sku", "")
# product_name = json_detail.get("name", "")
# brand_raw = json_detail.get("brand", {}).get("name", "")

# print(f"Brand: {brand_raw}")
# print(f"Product Name: {product_name}")
# print(f"Product Id: {product_id}")

# # --- cek apakah ada variasi ---
# variants = json_detail.get("variants")

# if variants and "inStock" in variants:  
#     # Produk punya variasi
#     for data_instock in variants["inStock"]:
#         name_inStock = data_instock.get("name")
#         sku_id = data_instock.get("sku")
#         imageUrl = data_instock.get("imageUrl")
#         product_desc = f"{product_name} {name_inStock}" if name_inStock else product_name

#         print("---- VARIANT ----")
#         print(f"Variant: {name_inStock}")
#         print(f"SKU Id: {sku_id}")
#         print(f"Image Url: {imageUrl}")
#         print(f"Product Desc: {product_desc}")
#         print()
# else:
#     # Produk tanpa variasi
#     image_list = json_detail.get("media", {}).get("images", [])
#     first_image = image_list[0] if image_list else ""
    
#     print("---- SINGLE PRODUCT ----")
#     print(f"SKU Id: {product_id}")
#     print(f"Image Url: {first_image}")
#     print(f"Product Desc: {product_name}")

# for url in [url]:
#     response = requests.get(url)
#     data = response.json()
#     parsed = parse_product_detail(data)

#     print(f"🔎 URL: {url}")
#     for item in parsed:
#         product_id = item.get("product_id", "")
#         product_id = item.get("sku_id", "")
#         print(product_id)

#         # print(json.dumps(item, indent=2, ensure_ascii=False))
#     print("="*80)