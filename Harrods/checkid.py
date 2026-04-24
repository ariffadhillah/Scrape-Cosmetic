# import requests
# import json
# from bs4 import BeautifulSoup

# BASE_URL = "https://www.harrods.com/en-us/p/dolce-and-gabbana-everlast-concealer-000000000007871118"
# # BASE_URL = "https://www.harrods.com/en-us/p/maison-crivelli-hibiscus-mahajad-perfume-extract-50ml-000000000007266634"

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
# }

# res = requests.get(BASE_URL, headers=HEADERS)
# soup = BeautifulSoup(res.text, "html.parser")

# # ambil script JSON-LD terakhir (biasanya yang berisi data produk)
# scripts = soup.find_all("script", {"type": "application/ld+json"})
# if not scripts:
#     print("❌ JSON-LD tidak ditemukan")
#     exit()

# # coba parse satu per satu
# for script in scripts:
#     try:
#         data = json.loads(script.string)

#         if data.get("@type") in ["Product", "ProductGroup"]:
#             product_name = data.get("name", "")
#             brand_name = data.get("brand", {}).get("name", "")

#             print(f"📌 Product: {product_name}")
#             print(f"🏷️ Brand: {brand_name}")

#             # jika ada varian
#             if "hasVariant" in data:
#                 for variant in data["hasVariant"]:
#                     sku = variant.get("sku", "")
#                     color = variant.get("color", "")
#                     # price = variant.get("offers", {}).get("price", "")
#                     # url = variant.get("url", "")

#                     print(f"   ➡️ SKU: {sku} | Color: {color}")

#             else:
#                 # single product
#                 sku = data.get("productID", "")
#                 color = data.get("color", "")
#                 # url = data.get("url", "")
#                 print(f"   ➡️ SKU: {sku} | Color: {color}")

#     except Exception as e:
#         continue



import requests
import json
from bs4 import BeautifulSoup
# BASE_URL = "https://www.harrods.com/en-us/p/dior-diorshow-5-couleurs-couture-eyeshadow-palette-000000000007796044"
BASE_URL = "https://www.harrods.com/en-us/p/kylie-cosmetics-skin-tint-blurring-elixir-foundation-000000000007647248"
# BASE_URL = "https://www.harrods.com/en-us/p/dior-backstage-face-glow-palette-000000000007827941"
# BASE_URL = "https://www.harrods.com/en-us/p/gucci-rouge-de-beaute-brillant-glow-and-care-lip-colour-000000000007837904"
# BASE_URL = "https://www.harrods.com/en-us/p/dolce-and-gabbana-everlast-concealer-000000000007871118"
# BASE_URL = "https://www.harrods.com/en-us/p/maison-crivelli-hibiscus-mahajad-perfume-extract-50ml-000000000007266634"
# BASE_URL = "https://www.harrods.com/en-us/p/maison-crivelli-hibiscus-mahajad-perfume-extract-50ml-000000000007266634"
# BASE_URL = "https://www.harrods.com/en-us/p/dior-rouge-dior-couture-colour-velvet-lipstick-000000000007827912"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
}

res = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(res.text, "html.parser")


# def get_section_text(soup, section_title: str) -> str:
#     """
#     Ambil teks dari section tertentu (misalnya 'Ingredients', 'How to use', dll.)
#     berdasarkan judul <h4>.
#     """
#     section = soup.find("h4", string=lambda t: t and section_title.lower() in t.lower())
#     if not section:
#         return ""

#     # Naik ke parent <button>
#     button = section.find_parent("button")
#     if not button:
#         return ""

#     # ambil id target dari aria-controls
#     target_id = button.get("aria-controls")
#     if not target_id:
#         return ""

#     # cari div dengan id tsb
#     target_div = soup.find("div", id=target_id)
#     if not target_div:
#         return ""

#     # gabungkan semua text di dalam <p>
#     paragraphs = target_div.find_all("p")
#     if not paragraphs:
#         return " ".join(target_div.stripped_strings)

#     return "\n".join(p.get_text(strip=True) for p in paragraphs)



# ingredients_text = get_section_text(soup, "Ingredients")


final_text = ""
ingredients_container = soup.find("div", id="benefits-dients-body")
if ingredients_container:
    ingredients_div = ingredients_container.find("div", class_="md:pl-[35px] pb-[30px]")
    if ingredients_div:
        paragraphs = ingredients_div.find_all("p")
        cleaned_texts = [p.get_text(strip=True) + "\n" for p in paragraphs]
        final_text = "\n".join(cleaned_texts).strip().title()


# ambil script JSON-LD terakhir (biasanya yang berisi data produk)
scripts = soup.find_all("script", {"type": "application/ld+json"})
if not scripts:
    print("❌ JSON-LD tidak ditemukan")
    exit()

# coba parse satu per satu
for script in scripts:
    try:
        data = json.loads(script.string)
        print(json.dumps(data, indent=4))
        

        if data.get("@type") in ["Product", "ProductGroup"]:
            product_name = data.get("name", "")
            brand_name = data.get("brand", {}).get("name", "")

            print(f"📌 Product: {product_name}")

            # jika ada varian (ProductGroup)
            if "hasVariant" in data:
                for variant in data["hasVariant"]:
                    product_name = variant.get("name", "")
                    sku = variant.get("sku", "") or variant.get("productID", "")
                    color = variant.get("color", "")
                    url = variant.get("url", "")
                    image = "https://hrd-live.cdn.scayle.cloud/"+variant.get("image", "")
                    product_desc = f"{product_name} {color}".replace(brand_name,"")

                    print(f"   ➡️ Product Id: {sku}")
                    print(f"   ➡️ SKU Id: {sku}")
                    print(f"🏷️ Brand: {brand_name}")
                    print(f"   ➡️ Product Desc: {product_desc}")
                    print(f"   ➡️ URL: {url}")
                    print(f"   ➡️ URL: {image}")
                    print("🧪 Ingredients:\n", final_text)

            else:
                # single product (Product)
                sku = data.get("sku", "") or data.get("productID", "")
                color = data.get("color", "")
                url = data.get("url", "")
                image = data.get("image", [""])[0]
                product_desc = f"{product_name} {color}".replace(brand_name,"")

                print(f"   ➡️ Product Id: {sku}")
                print(f"   ➡️ SKU Id: {sku}")
                # product_desc = f"{product_name} {color}"
                print(f"🏷️ Brand: {brand_name}")
                print(f"   ➡️ Product Desc: {product_desc}")
                print(f"   ➡️ URL: {url}")
                print(f"   ➡️ Image URL: {image}")
                print("🧪 Ingredients:\n", final_text)


    except Exception as e:
        continue
