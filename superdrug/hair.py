from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.superdrug.com"

fields = ["Major Category", "Specific Category", "Product URL"]

TARGET_URLS = [
    ("Bundles", "Bundles Supersize", "https://www.superdrug.com/bundles-supersize/c/bundles"),
    ("Hair", "Hair Colourants", "https://www.superdrug.com/hair/hair-colourants/c/hair-colourants"),
    ("Hair", "Shampoo", "https://www.superdrug.com/hair/shampoo/c/pt_hair_shampoo"),
    ("Hair", "Conditioners", "https://www.superdrug.com/hair/hair-conditioners/c/pt_hair_hair_conditioners"),
    ("Hair", "Styling", "https://www.superdrug.com/hair/hair-styling/c/hair-styling"),
    ("Hair", "Treatments", "https://www.superdrug.com/hair/hair-treatments/c/hair-treatments"),
    ("Hair", "Curly Hair Products", "https://www.superdrug.com/hair/curly-hair-products-/c/curly-hair"),
    ("Hair", "Hair Accessories", "https://www.superdrug.com/hair/hair-accessories/c/hair-access"),
    ("Hair", "Hair Masks", "https://www.superdrug.com/hair/hair-treatments/hair-masks/c/pt_hair_hair_masks"),
    ("Hair", "Hair Oils", "https://www.superdrug.com/hair/hair-treatments/hair-care-oils/c/pt_hair_hair_care_oils"),
    ("Electricals", "Hair Stylers", "https://www.superdrug.com/electricals/hair-stylers/c/elec-hairstylers"),
]

def accept_cookies(page):
    """Klik tombol Accept Cookies jika ada."""
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=8000)
        page.click("#onetrust-accept-btn-handler")
        print("🍪 Cookies accepted")
        page.wait_for_timeout(2000)
    except:
        print("🍪 No cookie banner found")

def get_product_links(page, subcategory_url):
    """Ambil semua produk dari subkategori (dengan pagination)."""
    all_products = []
    page_num = 0

    while True:
        url = subcategory_url if page_num == 0 else f"{subcategory_url}?currentPage={page_num}"
        page.goto(url, timeout=60000)

        try:
            page.wait_for_selector("div.product-grid__products-list", timeout=7000)
        except:
            break

        soup = BeautifulSoup(page.content(), "html.parser")
        product_list = soup.find("div", class_="product-grid__products-list")
        if not product_list:
            break

        products = []
        for a in product_list.select("a.product-image-container, a.cx-product-name"):
            href = a.get("href")
            if href and "/p/" in href:
                products.append(BASE_URL + href)

        if not products:
            break

        print(f"   📄 Page {page_num+1} → {len(products)} produk")
        all_products.extend(products)
        page_num += 1

    return list(dict.fromkeys(all_products))  # hapus duplikat

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=30)
        page = browser.new_page()

        page.goto(BASE_URL, timeout=40000)
        accept_cookies(page)

        with open("hair-superdrug_product_urls.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(fields)

            for major, specific, url in TARGET_URLS:
                print(f"\n=== {major} → {specific} ===")
                product_urls = get_product_links(page, url)
                for prod_url in product_urls:
                    writer.writerow([major, specific, prod_url])
                    print("   →", prod_url)

        browser.close()
