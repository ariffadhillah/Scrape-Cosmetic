import time
import csv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import random


BASE_URL = "https://www.superdrug.com"

def accept_cookies(page):
    """Klik tombol Accept Cookies jika ada."""
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=8000)
        page.click("#onetrust-accept-btn-handler")
        print("🍪 Cookies accepted")
        page.wait_for_timeout(4000)
    except:
        print("🍪 No cookie banner found")

# =============================
# FUNGSI: Ambil semua link produk per kategori
# =============================
def get_product_links(page, subcategory_url):
    all_products = set()   # langsung pakai set
    page_num = 0

    while True:
        url = subcategory_url if page_num == 0 else f"{subcategory_url}?currentPage={page_num}"

        # Retry untuk stabilitas
        for attempt in range(2):
            try:
                page.goto(url, timeout=10000)
                page.wait_for_selector("div.product-grid__products-list", timeout=10000)
                break
            except Exception as e:
                if attempt == 1:
                    print(f"❌ Gagal buka {url}: {e}")
                    return list(all_products)
                print(f"⚠️ Retry buka {url} ...")
                time.sleep(2)

        soup = BeautifulSoup(page.content(), "html.parser")
        product_list = soup.find("div", class_="product-grid__products-list")
        if not product_list:
            break

        products = []
        # for a in product_list.select("a.product-image-container, a.cx-product-name"):
        #     href = a.get("href")
        #     if href and "/p/" in href:
        #         # products.append(BASE_URL + href)
        #         products.append(urljoin(BASE_URL, href))

        for a in product_list.select("a.product-image-container, a.cx-product-name"):
            href = a.get("href")
            if href and "/p/" in href:
                products.append(urljoin(BASE_URL, href))

        if not products:
            break

        # masukkan langsung ke set → otomatis hapus duplikat
        all_products.update(products)
        print(f"   📄 Page {page_num+1} → {len(products)} produk (total unik: {len(all_products)})")

        page_num += 1

    return list(all_products)  # balikan list biar bisa di-loop

def page_details(page, product_url, major_category=None):
    for attempt in range(2):
        try:
            # page.goto(product_url, timeout=6000, wait_until="networkidle")
            # # lebih aman pakai state="attached" daripada visible
            # page.wait_for_selector("h1.product-details-title__text", timeout=5000, state="attached")

            page.goto(product_url, timeout=90000, wait_until="domcontentloaded")
            page.wait_for_selector("h1.product-details-title__text", timeout=90000, state="attached")
            page.wait_for_timeout(2000)  # tunggu render JS

            break
        except Exception as e:
            if attempt == 1:
                print(f"❌ Gagal buka produk {product_url}: {e}")
                return None
            print(f"⚠️ Retry produk {product_url} ...")
            # time.sleep(.5)
            time.sleep(random.uniform(1, 2))

    soup = BeautifulSoup(page.content(), "html.parser")

    # kalau H1 tidak ada → coba ambil title
    desc_tag = soup.select_one("h1.product-details-title__text")
    if not desc_tag:
        desc_tag = soup.select_one("title")

    product_desc = desc_tag.get_text(strip=True) if desc_tag else None

    # Brand
    brand_tag = soup.select_one("a.product-details-brand-link__text-link span") \
                or soup.select_one("a.product-details-brand-link__text-link")
    product_brand = brand_tag.get_text(strip=True) if brand_tag else None

    # Reviews
    reviews_tag = soup.select_one("span.reviews") or soup.select_one("a[href*='#reviews'] span")
    number_of_reviews = reviews_tag.get_text(strip=True).strip("()") if reviews_tag else None
    if number_of_reviews:
        number_of_reviews = f"'{number_of_reviews}"

    # Rating
    rating_tag = soup.select_one("h3.pr-review-snapshot-snippets-headline") \
                 or soup.select_one("span.sr-only")
    average_rating = rating_tag.get_text(strip=True) if rating_tag else None
    if average_rating:
        average_rating = f"'{average_rating}"

    # Product Code
    code_tag = soup.find("p", class_="product-general-information__section-item-description--articleNumber")
    product_code = code_tag.get_text(strip=True).replace("Product code:", "").strip() if code_tag else None
    if product_code:
        product_code = f"'{product_code}"

    # EAN
    ean_tag = soup.find("p", class_="product-general-information__section-item-description--ean")
    ean = ean_tag.get_text(strip=True).replace("EAN:", "").strip() if ean_tag else None
    if ean:
        ean = f"'{ean}"

    # Ingredients
    ingredients_tag = soup.find("p", class_="product-general-information__section-item-description--ingredients")
    ingredients = ingredients_tag.get_text(strip=True) if ingredients_tag else None

    # Ambil gambar 600x600
    image_tags = soup.select(".product-images-grid__image img")
    image_urls = [img.get("src") for img in image_tags if img.get("src") and "600x600" in img.get("src")]
    main_image = image_urls[0] if image_urls else None

    # Specific category
    breadcrumb_tags = soup.select("div.breadcrumb-container .breadcrumb-item__text")
    specific_category = breadcrumb_tags[-2].get_text(strip=True) if len(breadcrumb_tags) >= 2 else None

    return {
        "Major Category": major_category,
        "Specific Category": specific_category,
        "Product ID": product_code,
        "SKU ID": ean,
        "Product Brand": product_brand,
        "Product Desc": product_desc,
        "Product URL": product_url,
        "Product Image Link": main_image,
        "Product Ingredients": ingredients,
        "Rating": average_rating,
        "User Reviews": number_of_reviews
    }


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        page.goto(BASE_URL, timeout=20000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        accept_cookies(page)

        # daftar URL kategori
        category_urls = [
            # "https://www.superdrug.com/skin/body-care/stretch-mark-cream-oil-lotions/c/pt-stretch-marks",
            # # "https://www.superdrug.com/skin/body-moisturisers/body-lotions/c/pt_skin_moisturising_body_lotions?query=:ranking:masterBrandName:Africas%20Best:masterBrandName:Nivea:masterBrandName:Vaseline:masterBrandName:Vitamin%20E"
            # "https://www.superdrug.com/skin/hand-care/hand-cream/c/pt_skin_hand_moisturisers",
            # "https://www.superdrug.com/skin/fake-tan-bronzing/gradual-fake-tan/c/pt_skin_gradual_tan",
            # "https://www.superdrug.com/skin/eye-skincare/eye-creams/c/pt_skin_eye_creams",
            # "https://www.superdrug.com/skin/hand-care/hand-cream/c/pt_skin_hand_moisturisers",
            # "https://www.superdrug.com/hair/hair-conditioners/leave-in-conditioner/c/pt-hair-leave-in-conditioner",
            # "https://www.superdrug.com/hair/hair-care/colour-protect-conditioner/c/pt-hair-colour-protect-conditioner",
            # "https://www.superdrug.com/hair/hair-treatments/hair-masks/c/pt_hair_hair_masks",
            # "https://www.superdrug.com/hair/hair-treatments/conditioning-treatments/c/pt_hair_deep_conditioning_treatments"
            # "https://www.superdrug.com/hair/everyday-conditioner/c/pt-hair-everyday-conditioner"
            # "https://www.superdrug.com/c/pt-hair-leave-in-conditioner",
            "https://www.superdrug.com/hair/hair-colourants/semi-permanent/c/pt_hair_semi_permanent"


        ]

        # ambil semua product links dari semua kategori
        all_product_links = []
        for cat_url in category_urls:
            print(f"\n=== Scraping Category: {cat_url} ===")
            links = get_product_links(page, cat_url)
            all_product_links.extend(links)
            time.sleep(random.uniform(1,2))

        print(f"\nTotal produk ditemukan: {len(all_product_links)}\n")

        # ambil detail tiap produk
        results = []
        for i, url in enumerate(all_product_links, 1):
            print(f"🔗 {i}/{len(all_product_links)} {url}")
            data = page_details(page, url, major_category="Hair")
            if data:
                results.append(data)
            time.sleep(random.uniform(1,2))  # delay kecil agar lebih stabil

        # simpan ke CSV
        filename = "Hair-8.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Data tersimpan di {filename}")
        browser.close()