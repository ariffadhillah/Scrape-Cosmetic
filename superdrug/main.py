# # from playwright.sync_api import sync_playwright
# # from bs4 import BeautifulSoup

# # BASE_URL = "https://www.superdrug.com"

# # def get_category_links():
# #     """Ambil semua kategori utama Makeup (kecuali 'New In Makeup')."""
# #     with sync_playwright() as p:
# #         browser = p.chromium.launch(headless=False)
# #         page = browser.new_page()
# #         page.goto(BASE_URL + "/make-up/c/makeup", timeout=95000)

# #         soup = BeautifulSoup(page.content(), "html.parser")

# #         first_wrapper = soup.find("div", class_="wrapper wrapper--0")
# #         category_links = []

# #         if first_wrapper:
# #             for a in first_wrapper.select("div.childs a.link"):
# #                 name = a.get_text(strip=True)
# #                 href = a.get("href")
# #                 if href and "new-make-up" not in href.lower():
# #                     category_links.append({"name": name, "url": BASE_URL + href})

# #         browser.close()
# #         return category_links


# # def get_subcategory_links(category_url):
# #     """Ambil semua sub kategori dari 1 kategori."""
# #     with sync_playwright() as p:
# #         browser = p.chromium.launch(headless=False)
# #         page = browser.new_page()
# #         page.goto(category_url, timeout=95000)

# #         soup = BeautifulSoup(page.content(), "html.parser")

# #         subcategory_links = []
# #         wrapper = soup.find("div", class_="wrapper wrapper--0")
# #         if wrapper:
# #             for a in wrapper.select("div.childs a.link"):
# #                 name = a.get_text(strip=True)
# #                 href = a.get("href")
# #                 if href:
# #                     subcategory_links.append({"name": name, "url": BASE_URL + href})

# #         browser.close()
# #         return subcategory_links


# # if __name__ == "__main__":
# #     categories = get_category_links()
# #     print("=== Kategori Makeup ===")
# #     for cat in categories:
# #         print(f"{cat['name']} -> {cat['url']}")

# #         # ambil sub kategori dari tiap kategori
# #         subs = get_subcategory_links(cat["url"])
# #         for sub in subs:
# #             print(f"   ↳ {sub['name']} -> {sub['url']}")




# from playwright.sync_api import sync_playwright
# from bs4 import BeautifulSoup

# BASE_URL = "https://www.superdrug.com"

# def get_category_links(page):
#     """Ambil semua kategori utama Makeup (kecuali 'New In Makeup')."""
#     page.goto(BASE_URL + "/make-up/c/makeup", timeout=95000)
#     soup = BeautifulSoup(page.content(), "html.parser")

#     first_wrapper = soup.find("div", class_="wrapper wrapper--0")
#     category_links = []

#     if first_wrapper:
#         for a in first_wrapper.select("div.childs a.link"):
#             name = a.get_text(strip=True)
#             href = a.get("href")
#             if href and "new-make-up" not in href.lower():
#                 category_links.append({"name": name, "url": BASE_URL + href})
#     return category_links


# def get_subcategory_links(page, category_url):
#     """Ambil semua sub kategori dari 1 kategori (pakai page yang sama)."""
#     page.goto(category_url, timeout=95000)
#     soup = BeautifulSoup(page.content(), "html.parser")

#     subcategory_links = []
#     wrapper = soup.find("div", class_="wrapper wrapper--0")
#     if wrapper:
#         for a in wrapper.select("div.childs a.link"):
#             name = a.get_text(strip=True)
#             href = a.get("href")
#             if href:
#                 subcategory_links.append({"name": name, "url": BASE_URL + href})
#     return subcategory_links

# def get_product_links(page, subcategory_url):
#     """Ambil semua produk dari subkategori."""
#     page.goto(subcategory_url, timeout=95000)
#     soup = BeautifulSoup(page.content(), "html.parser")

#     product_links = []
#     product_list = soup.find("div", class_="product-grid__products-list")
#     if product_list:
#         # ambil dari link gambar produk
#         for a in product_list.select("a.product-image-container, a.cx-product-name"):
#             href = a.get("href")
#             if href and "/p/" in href:
#                 product_links.append(BASE_URL + href)

#     return list(set(product_links))  # buang duplikat



# # if __name__ == "__main__":
# #     with sync_playwright() as p:
# #         browser = p.chromium.launch(headless=False)
# #         page = browser.new_page()

# #         categories = get_category_links(page)
# #         print("=== Kategori Makeup ===")
# #         for cat in categories:
# #             print(f"{cat['name']} -> {cat['url']}")

# #             subs = get_subcategory_links(page, cat["url"])
# #             for sub in subs:
# #                 print(f"   ↳ {sub['name']} -> {sub['url']}")

# #         browser.close()


# if __name__ == "__main__":
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()

#         categories = get_category_links(page)
#         for cat in categories:
#             print(f"\n=== {cat['name']} ===")
#             subcats = get_subcategory_links(page, cat["url"])

#             # kalau tidak ada subkategori → langsung proses kategori
#             if not subcats:
#                 products = get_product_links(page, cat["url"])
#                 for prod in products:
#                     print("   →", prod)
#             else:
#                 for sub in subcats:
#                     print(f"  ↳ {sub['name']}")
#                     products = get_product_links(page, sub["url"])
#                     for prod in products:
#                         print("     →", prod)

#         browser.close()



from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.superdrug.com"


def get_category_links(page):
    """Ambil semua kategori utama Makeup (kecuali 'New In Makeup')."""
    page.goto(BASE_URL + "/make-up/c/makeup", timeout=99000)
    soup = BeautifulSoup(page.content(), "html.parser")

    first_wrapper = soup.find("div", class_="wrapper wrapper--0")
    category_links = []

    if first_wrapper:
        for a in first_wrapper.select("div.childs a.link"):
            name = a.get_text(strip=True)
            href = a.get("href")
            if href and "new-make-up" not in href.lower():
                category_links.append({"name": name, "url": BASE_URL + href})
    return category_links


def get_subcategory_links(page, category_url):
    """Ambil semua sub kategori dari 1 kategori (pakai page yang sama)."""
    page.goto(category_url, timeout=99000)
    soup = BeautifulSoup(page.content(), "html.parser")

    subcategory_links = []
    wrapper = soup.find("div", class_="wrapper wrapper--0")
    if wrapper:
        for a in wrapper.select("div.childs a.link"):
            name = a.get_text(strip=True)
            href = a.get("href")
            if href:
                subcategory_links.append({"name": name, "url": BASE_URL + href})
    return subcategory_links


# def get_product_links(page, subcategory_url):
#     """Ambil semua produk dari subkategori."""
#     page.goto(subcategory_url, timeout=95000)
#     time.sleep(3)  # biar sempat render
#     soup = BeautifulSoup(page.content(), "html.parser")

#     product_links = []
#     product_list = soup.find("div", class_="product-grid__products-list")
#     if product_list:
#         for a in product_list.select("a.product-image-container, a.cx-product-name"):
#             href = a.get("href")
#             if href and "/p/" in href:
#                 product_links.append(BASE_URL + href)

#     return list(dict.fromkeys(product_links))  # buang duplikat, preserve urutan


def get_product_links(page, subcategory_url):
    """Ambil semua produk dari subkategori (dengan pagination)."""
    all_products = []
    page_num = 0

    while True:
        # buat URL pagination
        if page_num == 0:
            url = subcategory_url
        else:
            url = f"{subcategory_url}?currentPage={page_num}"

        page.goto(url, timeout=99000)
        page.wait_for_timeout(9000)  # biar sempat render
        soup = BeautifulSoup(page.content(), "html.parser")

        product_list = soup.find("div", class_="product-grid__products-list")
        if not product_list:
            break  # tidak ada produk -> stop loop

        products = []
        for a in product_list.select("a.product-image-container, a.cx-product-name"):
            href = a.get("href")
            if href and "/p/" in href:
                products.append(BASE_URL + href)

        # kalau sudah tidak ada produk baru, stop
        if not products:
            break

        print(f"   📄 Page {page_num+1} → {len(products)} produk")
        all_products.extend(products)
        page_num += 1

    return list(dict.fromkeys(all_products))  # hapus duplikat, urut tetap




# if __name__ == "__main__":
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False, slow_mo=100)
#         page = browser.new_page()

#         categories = get_category_links(page)
#         for cat in categories:
#             print(f"\n=== {cat['name']} ===")
#             subcats = get_subcategory_links(page, cat["url"])

#             if not subcats:
#                 products = get_product_links(page, cat["url"])
#                 for prod in products:
#                     print(" →", prod)
#             else:
#                 for sub in subcats:
#                     print(f" ↳ {sub['name']}")
#                     products = get_product_links(page, sub["url"])
#                     for prod in products:
#                         print("   →", prod)

#         browser.close()


def page_details(page, product_url):
    """Ambil detail dari halaman produk."""
    page.goto(product_url, timeout=95000)
    page.wait_for_timeout(3000)
    soup = BeautifulSoup(page.content(), "html.parser")

    # Brand
    brand_tag = soup.select_one("a.product-details-brand-link__text-link span")
    brand = brand_tag.get_text(strip=True) if brand_tag else None

    # Description
    desc_tag = soup.select_one("h1.product-details-title__text")
    desc = desc_tag.get_text(strip=True) if desc_tag else None

    # Reviews
    reviews_tag = soup.select_one("span.reviews")
    reviews = reviews_tag.get_text(strip=True).strip("()") if reviews_tag else None

    # Rating
    rating_tag = soup.select_one("h3.pr-review-snapshot-snippets-headline")
    rating = rating_tag.get_text(strip=True) if rating_tag else None

    # Product Code
    code_tag = soup.find("p", class_="product-general-information__section-item-description--articleNumber")
    product_code = code_tag.get_text(strip=True).replace("Product code:", "").strip() if code_tag else None

    # EAN
    ean_tag = soup.find("p", class_="product-general-information__section-item-description--ean")
    ean = ean_tag.get_text(strip=True).replace("EAN:", "").strip() if ean_tag else None

    # Ingredients
    ing_tag = soup.find("p", class_="product-general-information__section-item-description--ingredients")
    ingredients = ing_tag.get_text(strip=True) if ing_tag else None

    # Images (ambil semua 600x600)
    images = []
    for img in soup.select("div.product-images-grid__images-wrapper img"):
        src = img.get("src")
        if src and "600x600" in src:
            images.append(src)

    return {
        "url": product_url,
        "brand": brand,
        "description": desc,
        "rating": rating,
        "reviews": reviews,
        "product_code": product_code,
        "ean": ean,
        "ingredients": ingredients,
        "images": images,
    }


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        categories = get_category_links(page)
        for cat in categories:
            print(f"\n=== {cat['name']} ===")
            subcats = get_subcategory_links(page, cat["url"])

            if not subcats:
                product_links = get_product_links(page, cat["url"])
                print(f"   Ditemukan {len(product_links)} produk di {cat['name']}")
                for prod in product_links:
                    details = page_details(page, prod)
                    print("   →", details["url"])
            else:
                for sub in subcats:
                    print(f"  ↳ {sub['name']}")
                    product_links = get_product_links(page, sub["url"])
                    print(f"     Ditemukan {len(product_links)} produk di {sub['name']}")
                    for prod in product_links:
                        details = page_details(page, prod)
                        print("     →", details["url"])

        browser.close()
