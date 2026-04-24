import json
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://www.superdrug.com/make-up/face/highlighter/liquid-highlighter/rimmel-better-than-filters-003-light-30ml/p/837530?varSel=837528"
# URL = 'https://www.superdrug.com/fragrance/perfume-for-women/womens-perfume/calvin-klein-eternity-moment-eau-de-parfum-100ml/p/923459'


def find_codes_with_image(node, results):
    """Cari semua pasangan code + thumbnailImage.url"""
    if isinstance(node, dict):
        code = node.get("code")
        if code and "thumbnailImage" in node and isinstance(node["thumbnailImage"], dict):
            img_url = node["thumbnailImage"].get("url")
            if img_url:
                results[code] = "https://www.superdrug.com" + img_url
        for v in node.values():
            find_codes_with_image(v, results)
    elif isinstance(node, list):
        for item in node:
            find_codes_with_image(item, results)



def find_codes_with_gallery_images(node, results):
    """Cari semua pasangan code + galleryImages.url (600x600)"""
    if isinstance(node, dict):
        code = node.get("code")
        if code and "galleryImages" in node and isinstance(node["galleryImages"], list):
            # ambil gambar dengan format 600x600 (atau fallback pertama)
            for img in node["galleryImages"]:
                url = img.get("url")
                meta = img.get("metaData", {})
                if url and meta.get("height") == "600" and meta.get("width") == "600":
                    results[code] = "https://www.superdrug.com" + url
                    break
            # fallback: kalau tidak ada yg 600x600, ambil gambar pertama
            if code not in results and node["galleryImages"]:
                results[code] = "https://www.superdrug.com" + node["galleryImages"][0].get("url")
        for v in node.values():
            find_codes_with_gallery_images(v, results)
    elif isinstance(node, list):
        for item in node:
            find_codes_with_gallery_images(item, results)



def find_ingredients(node, results):
    """Cari value dari code=ingredients di dalam JSON"""
    if isinstance(node, dict):
        if node.get("code") == "ingredients":
            results.append(node.get("value"))
        for v in node.values():
            find_ingredients(v, results)
    elif isinstance(node, list):
        for item in node:
            find_ingredients(item, results)


def find_key_values(node, key_name, results):
    """Cari semua value dari key tertentu di dalam JSON"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key_name:
                results.append(v)
            else:
                find_key_values(v, key_name, results)
    elif isinstance(node, list):
        for item in node:
            find_key_values(item, key_name, results)


def find_variants(node, results):
    """Cari semua key 'variants' dalam JSON hasil script_tag"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "variants" and isinstance(v, dict):
                options = (
                    v.get("value", {})
                     .get("baseOptions", [{}])[0]
                     .get("options", [])
                )
                if options:
                    results.extend(options)
            else:
                find_variants(v, results)
    elif isinstance(node, list):
        for item in node:
            find_variants(item, results)

def find_codes_with_ean(node, results):
    """Cari semua pasangan code + ean di dalam JSON"""
    if isinstance(node, dict):
        code = node.get("code")
        ean = node.get("ean")
        if code and ean:
            results[code] = ean
        for v in node.values():
            find_codes_with_ean(v, results)
    elif isinstance(node, list):
        for item in node:
            find_codes_with_ean(item, results)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, timeout=95000)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    script_tag = soup.find("script", {"id": "spartacus-app-state", "type": "application/json"})
    if script_tag:
        raw_json = script_tag.string
        clean_json = raw_json.replace("&q;", '"')
        data = json.loads(clean_json)

        # === setelah data = json.loads(clean_json) ===
        # cari ingredients di seluruh JSON
        ingredients_list = []
        find_ingredients(data, ingredients_list)
        ingredients = ingredients_list[0] if ingredients_list else None


        # 1) Ambil semua variants
        variants = []
        find_variants(data, variants)

        # unique_variants = {}
        # for opt in variants:
        #     code = opt.get("code")
        #     price = opt.get("priceData", {}).get("formattedValue")
        #     stock = opt.get("stock", {}).get("stockLevelStatus")
        #     color = opt.get("variantOptionQualifiers", [{}])[0].get("value")
        #     url = opt.get("url")

        #     unique_variants[code] = {
        #         "code": code,
        #         "color": color,
        #         "price": price,
        #         "stock": stock,
        #         "url": f"https://www.superdrug.com{url}",
        #         "ean": None
        #     }

        # # unique_variants = {}
        # # for opt in variants:
        # #     code = opt.get("code")
        # #     price = opt.get("priceData", {}).get("formattedValue")
        # #     stock = opt.get("stock", {}).get("stockLevelStatus")
        # #     color = opt.get("variantOptionQualifiers", [{}])[0].get("value")
        # #     url = opt.get("url")

        # #     # # ambil url gambar
        # #     # image_url = None
        # #     # if "thumbnailImage" in opt and isinstance(opt["thumbnailImage"], dict):
        # #     #     image_url = opt["thumbnailImage"].get("url")

        # # # cari semua gambar
        # # image_map = {}
        # # find_codes_with_image(data, image_map)

        # # # gabungkan dengan unique_variants
        # # for code, img in image_map.items():
        # #     if code in unique_variants:
        # #         unique_variants[code]["image"] = img

        # #     unique_variants[code] = {
        # #         "code": code,
        # #         "color": color,
        # #         "price": price,
        # #         "stock": stock,
        # #         "url": f"https://www.superdrug.com{url}",
        # #         "ean": None,
        # #         "image": f"https://www.superdrug.com{image_url}"
        # #     }



        # # 2) Cari semua EAN
        # ean_map = {}
        # find_codes_with_ean(data, ean_map)

        # # 3) Gabungkan
        # for code, ean in ean_map.items():
        #     if code in unique_variants:
        #         unique_variants[code]["ean"] = ean



        # 1) Ambil semua variants
        unique_variants = {}
        for opt in variants:
            code = opt.get("code")
            price = opt.get("priceData", {}).get("formattedValue")
            stock = opt.get("stock", {}).get("stockLevelStatus")
            color = opt.get("variantOptionQualifiers", [{}])[0].get("value")
            url = opt.get("url")

            unique_variants[code] = {
                "code": code,
                "color": color,
                "price": price,
                "stock": stock,
                "url": f"https://www.superdrug.com{url}" if url else None,
                "ean": None,
                "image": None
            }

        # # 2) Cari semua gambar
        # image_map = {}
        # find_codes_with_image(data, image_map)
        # for code, img in image_map.items():
        #     if code in unique_variants:
        #         unique_variants[code]["image"] = img

        # # 2) Cari semua gambar besar (galleryImages 600x600)
        # gallery_map = {}
        # find_codes_with_gallery_images(data, gallery_map)
        # for code, img in gallery_map.items():
        #     if code in unique_variants:
        #         unique_variants[code]["image"] = img

        # 2) Cari semua gambar besar (galleryImages 600x600)
        gallery_map = {}
        find_codes_with_gallery_images(data, gallery_map)

        # 2b) Cari semua thumbnailImage (fallback)
        thumb_map = {}
        find_codes_with_image(data, thumb_map)

        # Gabungkan ke unique_variants
        for code in unique_variants:
            if code in gallery_map:
                unique_variants[code]["image"] = gallery_map[code]
            elif code in thumb_map:
                unique_variants[code]["image"] = thumb_map[code]



        # 3) Cari semua EAN
        ean_map = {}
        find_codes_with_ean(data, ean_map)
        for code, ean in ean_map.items():
            if code in unique_variants:
                unique_variants[code]["ean"] = ean



        ratings = []
        reviews = []
        find_key_values(data, "averageRating", ratings)
        find_key_values(data, "numberOfReviews", reviews)

        avg_rating = ratings[0] if ratings else None
        num_reviews = reviews[0] if reviews else None

        # print("⭐ Average Rating:", avg_rating)
        # print("📝 Number of Reviews:", num_reviews)

        # print(ingredients)
        # print("=== HASIL VARIANTS + EAN + IMAGE ===")
        # for v in unique_variants.values():
        #     print(f"{v['code']} | {v['ean']} | {v['color']} | {v['price']} | "
        #         f"{v['stock']} | {v['url']} | {v['image']} | "
        #         f"Rating: {avg_rating} | Reviews: {num_reviews} | Ingredients: {ingredients}")

        print("=== HASIL VARIANTS + EAN + IMAGE ===")
        for v in unique_variants.values():
            print(f"{v['code']} | {v['ean']} | {v['color']} | {v['price']} | "
                f"{v['stock']} | {v['url']} | {v['image']} | "
                f"Rating: {avg_rating} | Reviews: {num_reviews} | Ingredients: {ingredients}")


        # print("=== HASIL VARIANTS + EAN ===")
        # for v in unique_variants.values():
        #     print(f"{v['code']} | {v['ean']} | {v['color']} | {v['price']} | {v['stock']} | "
        #         f"{v['url']} | Rating: {avg_rating} | Reviews: {num_reviews} | Ingredients: {ingredients}")


        # # 4) Simpan ke CSV
        # with open("superdrug_variants.csv", "w", newline="", encoding="utf-8") as f:
        #     writer = csv.DictWriter(f, fieldnames=["code", "ean", "color", "price", "stock", "url"])
        #     writer.writeheader()
        #     writer.writerows(unique_variants.values())

        # print("✅ Data berhasil disimpan ke superdrug_variants.csv")
    else:
        print("❌ JSON state tidak ditemukan")

    browser.close()
