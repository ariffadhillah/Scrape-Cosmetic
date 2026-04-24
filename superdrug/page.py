from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
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

def accept_cookies(page):
    """Klik tombol Accept Cookies jika ada."""
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=8000)
        page.click("#onetrust-accept-btn-handler")
        print("🍪 Cookies accepted")
        page.wait_for_timeout(4000)
    except:
        print("🍪 No cookie banner found")

def get_category_links(page):
    """Ambil semua kategori utama Makeup (kecuali 'New In Makeup')."""
    time.sleep(5)
    page.goto(BASE_URL + "/c/hair", timeout=99000)
    time.sleep(5)
    soup = BeautifulSoup(page.content(), "html.parser")
    # print(soup)

    time.sleep(20)
    first_wrapper = soup.find("div", class_="wrapper wrapper--0")
    
    category_links = []

    if first_wrapper:
        for a in first_wrapper.select("div.childs a.link"):
            print(a)
            name = a.get_text(strip=True)
            href = a.get("href")
            if href and "Views All" not in href.lower():
                category_links.append({"name": name, "url": BASE_URL + href})
    return category_links

def get_subcategory_links(page, category_url):
    """Ambil sub kategori dari 1 kategori."""
    page.goto(category_url, timeout=99000)
    time.sleep(10)
    soup = BeautifulSoup(page.content(), "html.parser")

    time.sleep(10)
    subcategory_links = []
    wrapper = soup.find("div", class_="wrapper wrapper--0")
    if wrapper:
        for a in wrapper.select("div.childs a.link"):
            name = a.get_text(strip=True)
            href = a.get("href")
            if href:
                subcategory_links.append({"name": name, "url": BASE_URL + href})
    return subcategory_links

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
            break  # kalau list produk tidak muncul, hentikan loop

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

    # Hapus duplikat URL, preserve urutan
    return list(dict.fromkeys(all_products))


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        page.goto(BASE_URL, timeout=40000)
        accept_cookies(page)

        with open("hair-superdrug_product_urls.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Major Category", "Specific Category", "Product URL"])  # header

            categories = get_category_links(page)
            for cat in categories:
                print(f"\n=== {cat['name']} ===")
                subcats = get_subcategory_links(page, cat["url"])
                targets = subcats if subcats else [{"name": cat["name"], "url": cat["url"]}]

                for sub in targets:
                    print(f"  ↳ {sub['name']}")
                    product_urls = get_product_links(page, sub["url"])
                    for prod_url in product_urls:
                        writer.writerow([cat["name"], sub["name"], prod_url])
                        print("   →", prod_url)

        browser.close()

