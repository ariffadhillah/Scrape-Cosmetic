from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

BASE_URL = "https://www.superdrug.com"

fields = [
    "Major Category",
    "Specific Category",
    "Product ID",
    "SKU ID",
    "Product Brand",
    "Product Desc",
    "Product URL",
    "Product Image Link",
    "Product Ingredients",
    "Rating",
    "User Reviews",
]

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless=new")  # aktifkan kalau mau headless
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(90)
    return driver

def get_category_links(driver):
    driver.get(BASE_URL + "/make-up/c/makeup")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.wrapper.wrapper--0"))
        )
    except:
        pass

    category_links = []
    try:
        wrapper = driver.find_element(By.CSS_SELECTOR, "div.wrapper.wrapper--0")
        anchors = wrapper.find_elements(By.CSS_SELECTOR, "div.childs a.link")
        for a in anchors:
            name = a.text.strip()
            href = a.get_attribute("href")
            if href and "new-make-up" not in href.lower():
                category_links.append({"name": name, "url": href})
    except Exception as e:
        print("⚠️ Gagal ambil kategori:", e)
    return category_links

def get_subcategory_links(driver, category_url):
    driver.get(category_url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.wrapper.wrapper--0"))
        )
    except:
        pass

    subcategory_links = []
    try:
        wrapper = driver.find_element(By.CSS_SELECTOR, "div.wrapper.wrapper--0")
        anchors = wrapper.find_elements(By.CSS_SELECTOR, "div.childs a.link")
        for a in anchors:
            name = a.text.strip()
            href = a.get_attribute("href")
            if href:
                subcategory_links.append({"name": name, "url": href})
    except Exception as e:
        # beberapa kategori mungkin tidak punya subkategori
        # print("⚠️ get_subcategory_links:", e)
        pass
    return subcategory_links

def page_details(driver, product_url, major_category=None, retries=1):
    """Ambil detail produk. retries = jumlah retry kalau timeout load."""
    for attempt in range(retries + 1):
        try:
            driver.get(product_url)
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-details-title__text"))
            )
            break
        except Exception as e:
            if attempt < retries:
                print("   ⚠️ Retry load produk:", product_url, "| attempt", attempt+1)
                time.sleep(2)
                continue
            else:
                print("   ❌ Timeout load produk:", product_url, "| error:", e)
                return None

    def safe_text(by, selector, remove=None):
        try:
            el = driver.find_element(by, selector)
            txt = el.text.strip()
            if remove:
                txt = txt.replace(remove, "").strip()
            return txt or None
        except:
            return None

    product_brand = safe_text(By.CSS_SELECTOR, "a.product-details-brand-link__text-link span")
    product_desc = safe_text(By.CSS_SELECTOR, "h1.product-details-title__text")

    number_of_reviews = safe_text(By.CSS_SELECTOR, "span.reviews")
    if number_of_reviews:
        number_of_reviews = f"'{number_of_reviews.strip('()')}"

    average_rating = safe_text(By.CSS_SELECTOR, "h3.pr-review-snapshot-snippets-headline")
    if average_rating:
        average_rating = f"'{average_rating}"

    product_code = safe_text(By.CSS_SELECTOR, "p.product-general-information__section-item-description--articleNumber", "Product code:")
    if product_code:
        product_code = f"'{product_code}"

    ean = safe_text(By.CSS_SELECTOR, "p.product-general-information__section-item-description--ean", "EAN:")
    if ean:
        ean = f"'{ean}"

    ingredients = safe_text(By.CSS_SELECTOR, "p.product-general-information__section-item-description--ingredients")

    main_image = None
    try:
        imgs = driver.find_elements(By.CSS_SELECTOR, ".product-images-grid__image img")
        for img in imgs:
            src = img.get_attribute("src")
            if src and "600x600" in src:
                main_image = src
                break
    except:
        pass

    specific_category = None
    try:
        crumbs = driver.find_elements(By.CSS_SELECTOR, "div.breadcrumb-container .breadcrumb-item__text")
        if len(crumbs) >= 2:
            specific_category = crumbs[-2].text.strip()
    except:
        pass

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

def process_products_with_pagination(driver, sub_url, writer, processed_urls, major_category):
    """
    Untuk setiap halaman di sub_url:
     - ambil semua href produk sebagai string
     - proses tiap URL segera
     - lanjut ke halaman berikutnya
    """
    page_num = 0
    while True:
        url = sub_url if page_num == 0 else f"{sub_url}?currentPage={page_num}"
        print("   ↪ Buka listing:", url)
        driver.get(url)

        # tunggu product grid muncul (atau timeout)
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-grid__products-list"))
            )
        except:
            # jika tidak ada grid, coba cek anchor langsung (beberapa layout beda)
            try:
                WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.cx-product-name"))
                )
            except:
                print(f"   ❌ Produk tidak ditemukan di halaman ini (Page {page_num+1})")
                break

        # ambil URL produk sebagai string (hindari menyimpan webelement)
        anchors = driver.find_elements(By.CSS_SELECTOR, "a.cx-product-name, a.product-image-container")
        product_urls = []
        for a in anchors:
            href = a.get_attribute("href")
            if href and "/p/" in href and href not in product_urls:
                product_urls.append(href)

        if not product_urls:
            print(f"   ❌ Tidak ada produk di halaman {page_num+1}, stop pagination")
            break

        print(f"   📄 Page {page_num+1} → {len(product_urls)} produk")

        # proses produk satu-per-satu segera (sebelum pindah halaman)
        for idx, prod_url in enumerate(product_urls, start=1):
            if prod_url in processed_urls:
                print("   ⚠️ Skip duplikat:", prod_url)
                continue
            print(f"   🔍 url sedang diproses ({idx}/{len(product_urls)}): {prod_url}")
            try:
                details = page_details(driver, prod_url, major_category=major_category, retries=1)
                if details:
                    writer.writerow(details)
                    processed_urls.add(prod_url)
                    print("   ✅ Selesai:", details["Product URL"])
                else:
                    print("   ❌ Detail kosong:", prod_url)
            except Exception as e:
                print("   ❌ Gagal ambil detail:", prod_url, "| error:", e)

        page_num += 1
        time.sleep(2)  # jeda kecil supaya tidak terlalu cepat

if __name__ == "__main__":
    driver = init_driver()
    driver.get(BASE_URL)

    processed_urls = set()

    with open("superdrug_products_selenium.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        categories = get_category_links(driver)
        for cat in categories:
            print(f"\n=== {cat['name']} ===")
            subcats = get_subcategory_links(driver, cat["url"])
            targets = subcats if subcats else [{"name": cat["name"], "url": cat["url"]}]

            for sub in targets:
                print(f"  ↳ {sub['name']}")
                # Proses produk per halaman di sini (langsung menulis CSV)
                process_products_with_pagination(driver, sub["url"], writer, processed_urls, cat["name"])

    driver.quit()
