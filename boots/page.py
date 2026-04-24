# # # import requests
# # # from bs4 import BeautifulSoup

# # # BASE_URL = "https://www.boots.com/loreal-paris-paradise-le-shadow-stick-eyeshadow-10352443"

# # # header = {
# # #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
# # #     "Accept": "application/json, text/plain, */*",
# # #     "Accept-Language": "en-US,en;q=0.9",
# # #     "Referer": BASE_URL,
# # #     "Origin": BASE_URL,
# # #     "Connection": "keep-alive"
# # # }

# # # res = requests.get(BASE_URL, headers=header)

# # # # cek status
# # # if res.status_code == 200:
# # #     print("✅ Berhasil (200)")
# # # else:
# # #     print(f"❌ Gagal ({res.status_code})")

# # # soup = BeautifulSoup(res.text, "html.parser")
# # # print(res.status_code, res.reason)  
# # # title = soup.find("span", {"itemprop":"description"})
# # # print(title)




# # from playwright.sync_api import sync_playwright
# # from bs4 import BeautifulSoup
# # import time

# # URL = "https://www.boots.com/estee-lauder-pure-color-creme-lipstick-10325172"

# # def fetch_with_playwright(url):
# #     with sync_playwright() as p:
# #         # Pilih browser: chromium, firefox, atau webkit
# #         browser = p.chromium.launch(headless=False)  # headless=False supaya kita bisa melihatnya
# #         context = browser.new_context(
# #             user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
# #                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"),
# #             viewport={"width": 1280, "height": 800},
# #             java_script_enabled=True,
# #         )

# #         # Optional: set cookies/proxy di sini jika kamu punya
# #         page = context.new_page()

# #         # Buka halaman
# #         page.goto(url, wait_until="domcontentloaded", timeout=60000)

# #         # Interaksi kecil supaya terlihat manusiawi:
# #         time.sleep(1)
# #         page.mouse.move(300, 300)
# #         page.mouse.wheel(0, 400)   # scroll ke bawah
# #         time.sleep(10)

# #         # tunggu elemen produk yang biasa ada (sesuaikan selector)
# #         try:
# #             # contoh menunggu nama produk (ganti selector bila perlu)
# #             time.sleep(.5)
# #             page.wait_for_selector('[itemprop="name"]', state="attached", timeout=10000)

# #         except Exception as e:
# #             print("⚠️ Selector tidak muncul:", e)

# #         # ambil HTML yang sudah ter-render
# #         html = page.content()


# #         browser.close()
# #         return html

# # if __name__ == "__main__":
# #     html = fetch_with_playwright(URL)
# #     soup = BeautifulSoup(html, "html.parser")
# #     # print(soup)
# #     # productId = soup.find("div", id="productId").text.strip()
# #     # print(productId)
# # # estore_product_title
# #     # contohnya ambil nama produk dan deskripsi

# #     productId = ''
# #     productId_div = soup.find("div", id="productId")
# #     if productId_div:
# #         productId = productId_div.get_text(strip=True)
# #     else:
# #         print("❌ ProductId tidak ditemukan")


# #     name = soup.find("div", id="estore_product_title")

# #     ingredients_title = soup.find("h3", id="product_ingredients")
# #     ingredients_text = []

# #     if ingredients_title:
# #         for sib in ingredients_title.find_all_next():
# #             # berhenti kalau ketemu h3 lain
# #             if sib.name == "h3":
# #                 break
# #             if sib.name == "p":
# #                 txt = sib.get_text(" ", strip=True)
# #                 if txt:
# #                     ingredients_text.append(txt)



# #     # description = soup.find(attrs={"itemprop": "description"})

# #     print("Product ID:", productId)
# #     print("Name :", name.get_text(strip=True) if name else "Tidak ditemukan")
# #     print("Ingredients:", " ".join(ingredients_text))
# #     # print("Desc :", description.get_text(strip=True) if description else "Tidak ditemukan")


# # # from playwright.sync_api import sync_playwright
# # # from bs4 import BeautifulSoup
# # # import json
# # # import time

# # # URL = "https://www.boots.com/estee-lauder-pure-color-creme-lipstick-10325172"

# # # def fetch_with_playwright(url):
# # #     with sync_playwright() as p:
# # #         browser = p.chromium.launch(headless=True)
# # #         context = browser.new_context(
# # #             user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
# # #                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"),
# # #             viewport={"width": 1280, "height": 800},
# # #             java_script_enabled=True,
# # #         )

# # #         page = context.new_page()
# # #         page.goto(url, wait_until="domcontentloaded", timeout=60000)

# # #         time.sleep(2)  # kasih waktu render

# # #         html = page.content()
# # #         browser.close()
# # #         return html

# # # if __name__ == "__main__":
# # #     html = fetch_with_playwright(URL)
# # #     soup = BeautifulSoup(html, "html.parser")

# # #     # cari script JSON-LD
# # #     scripts = soup.find_all("script", type="application/ld+json")

# # #     product_data = None
# # #     for script in scripts:
# # #         try:
# # #             data = json.loads(script.string)
# # #             # cek apakah JSON ini adalah produk
# # #             if isinstance(data, dict) and data.get("@type") in ["Product", "ProductGroup"]:
# # #                 product_data = data
# # #                 break
# # #         except Exception:
# # #             continue

# # #     if product_data:
# # #         # ambil informasi penting
# # #         name = product_data.get("name")
# # #         desc = product_data.get("description")
# # #         sku = product_data.get("sku")
# # #         brand = product_data.get("brand", {}).get("name") if isinstance(product_data.get("brand"), dict) else product_data.get("brand")
# # #         offers = product_data.get("offers", {})
# # #         price = offers.get("price")
# # #         currency = offers.get("priceCurrency")
# # #         availability = offers.get("availability")

# # #         print("Name        :", name)
# # #         print("Description :", desc)
# # #         print("SKU         :", sku)
# # #         print("Brand       :", brand)
# # #         print("Price       :", price, currency)
# # #         print("Availability:", availability)
# # #     else:
# # #         print("❌ JSON-LD Product tidak ditemukan")




# # from playwright.sync_api import sync_playwright
# # from bs4 import BeautifulSoup
# # import time, json

# # URL = "https://www.boots.com/estee-lauder-pure-color-creme-lipstick-10325172"

# # def fetch_with_playwright(url):
# #     with sync_playwright() as p:
# #         browser = p.chromium.launch(headless=False)
# #         context = browser.new_context(
# #             user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
# #                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"),
# #             viewport={"width": 1280, "height": 800},
# #             java_script_enabled=True,
# #         )
# #         page = context.new_page()
# #         page.goto(url, wait_until="domcontentloaded", timeout=60000)

# #         # scroll jauh ke bawah agar Ingredients termuat
# #         for i in range(5):
# #             page.mouse.wheel(0, 1500)
# #             time.sleep(2)

# #         # tunggu sampai Ingredients muncul
# #         # try:
# #         #     page.wait_for_selector("#product_ingredients", state="visible", timeout=20000)
# #         # except Exception as e:
# #         #     print("⚠️ Ingredients title tidak muncul:", e)

# #         page.wait_for_selector("#product_ingredients", state="attached", timeout=20000)
# #         ingredients_title = page.query_selector("#product_ingredients")

# #         if ingredients_title:
# #             ingredients_div = ingredients_title.evaluate("el => el.nextElementSibling.innerText")
# #             print("Ingredients:", ingredients_div.strip())
# #         else:
# #             print("Ingredients: ❌ Tidak ditemukan")


# #         html = page.content()
# #         browser.close()
# #         return html


# # if __name__ == "__main__":
# #     html = fetch_with_playwright(URL)
# #     soup = BeautifulSoup(html, "html.parser")

# #     # ambil Ingredients
# #     ingredients_title = soup.find("h3", id="product_ingredients")
# #     ingredients_text = []

# #     if ingredients_title:
# #         for sib in ingredients_title.find_all_next():
# #             if sib.name == "h3":  # berhenti sebelum section berikutnya
# #                 break
# #             if sib.name == "p":
# #                 txt = sib.get_text(" ", strip=True)
# #                 if txt:
# #                     ingredients_text.append(txt)

# #     print("Ingredients:", " ".join(ingredients_text) if ingredients_text else "❌ Tidak ditemukan")



# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()
#     page.goto("https://www.boots.com/estee-lauder-pure-color-envy-soft-rouge-10340975", timeout=60000)

#     # ✅ Klik tombol "Accept cookies" kalau muncul
#     try:
#         page.wait_for_selector("#onetrust-accept-btn-handler", timeout=5000)
#         page.click("#onetrust-accept-btn-handler")
#         print("🍪 Accept cookies diklik")
#     except:
#         print("✅ Cookie banner tidak muncul")

#     # ✅ Baru tunggu elemen ingredients
#     page.wait_for_selector("#product_ingredients", timeout=20000)
#     ingredients_title = page.query_selector("#product_ingredients")

#     if ingredients_title:
#         # Ambil sibling (div yang isinya Ingredients list)
#         ingredients_div = ingredients_title.evaluate("el => el.nextElementSibling.innerText")
#         print("Ingredients:", ingredients_div.strip())
#     else:
#         print("Ingredients: ❌ Tidak ditemukan")

#     browser.close()



# from playwright.sync_api import sync_playwright

# # URL = "https://www.boots.com/dr-jart-cicapair-tiger-grass-color-correcting-treatment-30ml-10366776"
# URL = "https://www.boots.com/garnier-oil-free-perfecting-care-all-in-1-bb-cream-spf25-light-shade-50ml-10299174"

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()
#     page.goto(URL, timeout=10000)

#     # Klik Accept cookies kalau ada
#     try:
#         page.wait_for_selector("#onetrust-accept-btn-handler", timeout=20000)
#         page.click("#onetrust-accept-btn-handler")
#         print("🍪 Accept cookies diklik")
#     except:
#         print("✅ Cookie banner tidak muncul")

#     # Klik tab Ingredients
#     try:
#         page.wait_for_selector('a[href="#product_ingredients"]', timeout=10000)
#         page.click('a[href="#product_ingredients"]')
#         print("🔎 Klik tab Ingredients")
#     except:
#         print("⚠️ Tab Ingredients tidak ditemukan")

#     # Tunggu konten ingredients muncul
#     try:
#         page.wait_for_selector("#product_ingredients", timeout=20000)
#         ingredients_html = page.inner_text("#product_ingredients")
#         print("✅ Ingredients ditemukan:\n", ingredients_html.strip())
#     except:
#         print("❌ Ingredients tidak ditemukan")

#     browser.close()



from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def get_sibling_text(soup, header_text: str) -> str | None:
    """
    Cari <h3> berdasarkan teks (misalnya 'Ingredients'),
    lalu ambil sibling <p> berikutnya yang punya teks.
    """
    h3 = soup.find("h3", string=lambda t: t and header_text.lower() in t.lower())
    if not h3:
        return None

    # loop ke semua sibling setelah <h3>
    for sibling in h3.find_all_next():
        if sibling.name == "p":  # hanya ambil <p>
            text = sibling.get_text(" ", strip=True)
            if text:  # skip kalau kosong
                return text
    return None


# URL = "https://www.boots.com/dr-jart-cicapair-tiger-grass-color-correcting-treatment-30ml-10366776"
URL = "https://www.boots.com/garnier-oil-free-perfecting-care-all-in-1-bb-cream-spf25-light-shade-50ml-10299174"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, timeout=50000)

    # Klik Accept cookies kalau ada
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=50000)
        page.click("#onetrust-accept-btn-handler")
        print("🍪 Accept cookies diklik")
    except:
        print("✅ Cookie banner tidak muncul")
    html = page.content()


# # === Parse dengan BeautifulSoup ===
    soup = BeautifulSoup(html, "html.parser")


    # Brand
    brand_tag = soup.select_one("a.product-details-brand-link__text-link span")
    if brand_tag:
        product_brand = brand_tag.get_text(strip=True)
    else:
        brand_tag = soup.select_one('span[itemprop="Brand"]')
        product_brand = brand_tag.get_text(strip=True) if brand_tag else None


    # Description
    desc_tag = soup.select_one("h1.pdpTitle")
    product_desc = desc_tag.get_text(strip=True) if desc_tag else None

    # Reviews count
    # rating_value = soup.select_one('[itemprop="ratingValue"]')

    # Rating Value
    rating_value_tag = soup.select_one('[itemprop="ratingValue"]')
    rating_value = rating_value_tag.get_text(strip=True) if rating_value_tag else None

    # Review Count (pakai meta lebih aman)
    review_count_tag = soup.select_one('meta[itemprop="reviewCount"]')
    if review_count_tag and review_count_tag.has_attr("content"):
        review_count = review_count_tag["content"]
    else:
        review_count_div = soup.select_one("div.bv_numReviews_text")
        review_count = review_count_div.get_text(strip=True) if review_count_div else None



    # Product Code
    product_id_tag = soup.select_one('div#productId')
    product_id = product_id_tag.get_text(strip=True) if product_id_tag else None

    # EAN
    sku_id = URL.split("-")[-1] if "-" in URL else None
    # print("SKU ID:", sku_id)
    
    # Cari elemen H3 yang teksnya persis "Ingredients"
    # ingredients_h3 = soup.find("h3", string=lambda t: t and "Ingredients" in t)

    # product_ingredients = None
    # if ingredients_h3:
    #     # ambil sibling berikutnya yang <p>
    #     ingredients_p = ingredients_h3.find_next_sibling("p")
    #     if ingredients_p:
    #         # gabungkan isi teksnya, termasuk <br> jadi spasi
    #         product_ingredients = ingredients_p.get_text(" ", strip=True)

        
    # soup1 = BeautifulSoup(soup, "html.parser")
    # soup2 = BeautifulSoup(html_2, "html.parser")

    


    # Image (ambil yang 600x600)
    # img_tag = soup.select_one("e2core-media img")
    # image_url = img_tag["src"] if img_tag and "600x600" in img_tag["src"] else None

    # Ambil semua gambar dari gallery (600x600)
    # Product Image
    image_tag = soup.select_one('img[itemprop="image"]')
    product_image = image_tag["src"] if image_tag and image_tag.has_attr("src") else None



    # print("Main Image:", main_image)
    # print("All Images:", image_urls)



    # Specific category (breadcrumb sebelum terakhir)
    breadcrumb_tags = soup.select("div.breadcrumb-container .breadcrumb-item__text")
    specific_category = breadcrumb_tags[-2].get_text(strip=True) if len(breadcrumb_tags) >= 2 else None

    print("Brand:", product_brand)
    print("Description:", product_desc)
    # print("Reviews:", number_of_reviews)
    # print("Rating:", average_rating)
    print("Rating Value:", rating_value)
    print("Review Count:", review_count)
    print("Product Code:", product_id)
    print("SKU ID:", sku_id)
    # print("Ingredients:", product_ingredients)
    # print("Image:", main_image)
    print("Case A:", get_sibling_text(soup, "Ingredients"))
    # print("Case B:", get_sibling_text(soup, "Ingredients"))

    print("Product Image:", product_image)
    print("Specific Category:", specific_category)

browser.close()
