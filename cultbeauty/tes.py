# import requests, re, json
# from bs4 import BeautifulSoup

# url_items_products = "https://www.cultbeauty.co.uk/p/patrick-ta-major-glow-highlighter-10ml-various-shades/15372589/"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
# }

# res = requests.get(url_items_products, headers=headers)
# soup = BeautifulSoup(res.text, "html.parser")

# # cari semua <script> yg ada kata "trackingObj"
# # scripts = soup.find_all("script", {"type":"application/ld+json"})[0]
# script_items = soup.find_all("script", string=re.compile("variationData"))
# print(script_items)
# # script_item_found = False
# # for script_item in script_items:
# #     text_variationData = script_items.string    
# #     if not text_variationData:
# #         continue
# #     match_variationData = re.search(r'const\s+variationData\s*=\s*(\{.*?\})\s*;', text_variationData, re.S)
# #     print(match_variationData)
#     # if match_variationData:
#     #     try:
#     #         data_items = json.loads(match_variationData.group(1))
#     #         if data_items:
#     #             script_item_found = True
#     #             print(f"\n📄 Page ({url_items_products})")
#     #             for items_product in data_items.items():
#     #                 print(items_product)




#         # except Exception as e:
#         #     print("⚠️ Error parse Data Items JSON:", e)




import requests, re, json
from bs4 import BeautifulSoup

url_items_products = "https://www.cultbeauty.co.uk/p/patrick-ta-major-glow-highlighter-10ml-various-shades/15372589/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}




def format_rating(rating):
    try:
        return f"{round(float(rating), 1)}"
    except:
        return None

def format_review_count(count):
    try:
        count = int(count)
        return f"{round(count / 1000, 1)} K" if count >= 1000 else str(count)
    except:
        return None

res = requests.get(url_items_products, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")
data = {}


# def get_section_text(soup, section_title):
#     """
#     Mengambil teks dari collapsible section berdasarkan judul (summary) seperti 'Ingredients'.
    
#     :param soup: Objek BeautifulSoup dari halaman
#     :param section_title: Judul section, misalnya 'Ingredients'
#     :return: String teks dari section atau None jika tidak ditemukan
#     """
#     # Cari semua summary di dalam details
#     details_tags = soup.find_all("accordion-item")
#     for details in details_tags:
#         summary_tag = details.find("button")
#         if summary_tag and summary_tag.get_text(strip=True) == section_title:
#             # Ambil semua teks di div collapsible__content
#             content_div = details.find("div", class_="collapsible__content")
#             if content_div:
#                 return content_div.get_text(separator="\n\n", strip=True)
#     return None

# misalnya `soup` sudah ada

# ambil div content khusus Ingredients
ingredients_container = soup.find("div", {"aria-labelledby": "Ingredients"})

if ingredients_container:
    ingredients_div = ingredients_container.find("div", class_="attribute-content")
    if ingredients_div:
        paragraphs = ingredients_div.find_all("p")

        cleaned_texts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            # jika judul ('My Love':, 'Baby':, dll) kasih newline lebih
            if text.endswith(":") or text.startswith("'"):
                cleaned_texts.append("\n" + text + "\n")
            else:
                cleaned_texts.append(text + "\n")

        final_text = "\n".join(cleaned_texts).strip()
        print(final_text)


    # --- Ambil Ingredients ---

# time.sleep(0.5)
# ingredients_text = get_section_text(soup, "Ingredients")

find_reviews = soup.find("script", {"type": "application/ld+json"})
if find_reviews:
    try:
        data = json.loads(find_reviews.string)
        # print(data)

        # ambil hanya aggregateRating
        aggregate = data.get("aggregateRating", {})
        rating_value = format_rating(aggregate["ratingValue"]) if aggregate else None
        review_count_value = format_review_count(aggregate["reviewCount"]) if aggregate else None

    except Exception as e:
        print("⚠️ Error parse JSON:", e)

# cari <script> yg mengandung "variationData"
script_items = soup.find_all("script", string=re.compile("variationData"))

for script_item in script_items:
    text_variationData = script_item.string
    if not text_variationData:
        continue

    match = re.search(r'const\s+variationData\s*=\s*(\[.*?\]);', text_variationData, re.S)
    if match:
        try:
            data_items = json.loads(match.group(1))

            for item_product in data_items:
                if isinstance(item_product, dict):
                    sku_id = item_product.get("sku")
                    product_desc = item_product.get("title")

                    images = item_product.get("images", [])
                    product_image_raw = ""
                    if isinstance(images, list) and images:
                        product_image_raw = images[0].get("original", "")

                    product_image = f"https:{product_image_raw}" if str(product_image_raw).startswith("//") else product_image_raw

                    print("sku id:", sku_id) 
                    print("Product Desc:", product_desc) 
                    print("Image Url:", product_image)
                    print(f"⭐ Rating: {rating_value}")
                    print(f"📝 Jumlah Review: {review_count_value}")
                    print(f"Ingredients: {final_text}")
                    print("-" * 50)
                    print()



        except Exception as e:
            print("⚠️ Error parse Data Items JSON:", e)
