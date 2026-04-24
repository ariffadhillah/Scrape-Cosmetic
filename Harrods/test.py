import requests
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup


majorcategory = 'Make Up'

fields  = [ "Major Category", "Specific Category", "Product ID", "SKU ID", "Product Brand", "Product Desc", "Product URL", "Product Image Link", "Product Ingredients" ]
data_save = []

filename = f'products_{majorcategory}.csv'

BASE_DOMAIN = "https://www.harrods.com"
BASE_URL = urljoin(BASE_DOMAIN, "/en-us/make-up")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_DOMAIN,
    "Connection": "keep-alive"
}

def get_proxies():
    username = "spju19f0x2"
    password = "tr4ZxZo6OY4d8i_uml"
    proxy = f"http://{username}:{password}@dc.decodo.com:10001"
    return {"http": proxy, "https": proxy}

def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, proxies=get_proxies(), timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"❌ Error mengambil URL {url}: {e}")
        return None

# ====== helper: ekstrak semua product URLs dari halaman kategori ======
def extract_product_urls_from_soup(soup):
    urls = []
    if not soup:
        return urls

    # 1) Cari article yang merupakan product card (robust terhadap beberapa atribut)
    articles = soup.find_all("article")
    for art in articles:
        # cek atribut khas product card
        if ("data-test-id" in art.attrs and "product" in art.attrs.get("data-test-id", "")) or \
           ("data-product-card-id" in art.attrs) or \
           ("data-test-id" in art.attrs and art.attrs.get("data-test-id") == "product-item"):
            a = art.find("a", href=True)
            if a:
                href = a["href"].strip()
                if "/p/" in href:  # memastikan link produk
                    full = urljoin(BASE_DOMAIN, href)
                    urls.append(full)

    # 2) Jika belum dapat, fallback: cari semua <a> yang mengandung /en-us/p/
    if not urls:
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if "/en-us/p/" in href or "/p/" in href:
                full = urljoin(BASE_DOMAIN, href)
                urls.append(full)

    # dedup while preserving order
    seen = set()
    ordered = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return ordered

# ====== proses daftar produk (panggil detail satu-satu) ======
def process_product_list(list_url, name_kategori_sub):
    print(f"\n📂 Memproses daftar produk: {list_url}  (kategori: {name_kategori_sub})")
    soup = get_soup(list_url)
    if not soup:
        return

    product_urls = extract_product_urls_from_soup(soup)
    if not product_urls:
        print("⚠️ Tidak menemukan product items di halaman ini.")
        return

    print(f"👉 Ditemukan {len(product_urls)} produk. Memproses tiap product (rate-limited).")
    for idx, p_url in enumerate(product_urls, 1):
        print(f"\n[{idx}/{len(product_urls)}] {p_url}")
        try:
            process_product_url(p_url, name_kategori_sub)
        except Exception as e:
            print(f"❌ Error memproses {p_url}: {e}")
        time.sleep(0.8)  # jeda kecil agar tidak over-request

# ====== proses detail produk (parsing JSON-LD + ingredients) ======
def process_product_url(product_url, name_kategori_sub):
    print(f"🔎 Memproses product detail: {product_url}  (kategori: {name_kategori_sub})")
    soup = get_soup(product_url)
    if not soup:
        return

    # Ambil ingredients (jika struktur HTML sama seperti contoh)
    final_text = ""
    ingredients_container = soup.find("div", id="benefits-dients-body")
    if ingredients_container:
        # fleksibel mencari isi
        paragraphs = ingredients_container.find_all("p")
        cleaned_texts = [p.get_text(strip=True) for p in paragraphs]
        final_text = "\n".join(cleaned_texts).strip().title()

    # Ambil JSON-LD scripts
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    if not scripts:
        print("❌ JSON-LD tidak ditemukan di halaman produk ini.")
        # tetap print ingredients jika ada
        if final_text:
            print("🧪 Ingredients:\n", final_text)
        return

    def handle_product_dict(d):
        # d adalah dict JSON-LD yang merepresentasikan Product atau ProductGroup
        if not isinstance(d, dict):
            return
        typ = d.get("@type", "")
        if isinstance(typ, list):
            # kadang @type: ["Thing","Product"]
            if "Product" not in typ and "ProductGroup" not in typ:
                return
        else:
            if typ not in ("Product", "ProductGroup"):
                return

        product_name = d.get("name", "")
        brand_name = ""
        brand = d.get("brand", {})
        if isinstance(brand, dict):
            brand_name = brand.get("name", "")
        print(f"📌 Product: {product_name}")
        if "hasVariant" in d and isinstance(d["hasVariant"], list):
            for variant in d["hasVariant"]:
                sku = variant.get("sku", "") or variant.get("productID", "")
                color = variant.get("color", "")
                url = variant.get("url", "")
                # image kadang path relatif atau penuh
                image_field = variant.get("image", "")
                image = image_field
                if isinstance(image_field, str) and image_field and image_field.startswith("/"):
                    image = urljoin("https://hrd-live.cdn.scayle.cloud/", image_field.lstrip("/"))

                print(f"   ➡️ Major Category: {majorcategory}")
                print(f"   ➡️ Specific Category: {name_kategori_sub}")
                print(f"   ➡️ Product Id: {sku}")
                print(f"🏷️ Brand: {brand_name}")
                print(f"   ➡️ Product Desc: {(product_name + ' ' + (color or '')).replace(brand_name, '').strip()}")
                print(f"   ➡️ Product URL: {url}")
                print(f"   ➡️ Product Image Link: {image}")
                if final_text:
                    print("🧪 Product Ingredients:\n", final_text)
        else:
            sku = d.get("sku", "") or d.get("productID", "")
            color = d.get("color", "")
            url = d.get("url", "")
            image_field = d.get("image", "")
            image = ""
            if isinstance(image_field, list) and image_field:
                image = image_field[0]
            elif isinstance(image_field, str):
                image = image_field
            print(f"   ➡️ Major Category: {majorcategory}")
            print(f"   ➡️ Specific Category: {name_kategori_sub}")
            print(f"   ➡️ Product Id: {sku}")
            print(f"🏷️ Brand: {brand_name}")
            print(f"   ➡️ Product Desc: {(product_name + ' ' + (color or '')).replace(brand_name, '').strip()}")
            print(f"   ➡️ Product URL: {url}")
            print(f"   ➡️ Product Image Link: {image}")
            if final_text:
                print("🧪 Product Ingredients:\n", final_text)

    # parse setiap script (bisa berupa dict atau list)
    for script in scripts:
        script_text = script.string or script.get_text() or ""
        script_text = script_text.strip()
        if not script_text:
            continue
        try:
            data = json.loads(script_text)
        except Exception:
            # kadang ada beberapa JSON object concatenated -> skip
            continue

        # data bisa dict atau list
        if isinstance(data, list):
            for item in data:
                handle_product_dict(item)
        elif isinstance(data, dict):
            # kadang JSON-LD top-level adalah dict with "@graph"
            if "@graph" in data and isinstance(data["@graph"], list):
                for item in data["@graph"]:
                    handle_product_dict(item)
            else:
                handle_product_dict(data)

# ====== Ambil menu utama & subkategori ======
def proses_menu_url(soup):
    full_menu = soup.find("div", id="filter-category-body")
    if not full_menu:
        print("Menu utama tidak ditemukan")
        return

    ul_ = full_menu.find("ul")
    if not ul_:
        print("Tidak menemukan daftar <ul> kategori")
        return
    li_items = ul_.find_all("li", recursive=False)
    for list_menu in li_items:
        a_tag = list_menu.find("a")
        if a_tag and a_tag.get("href"):
            url_menu = urljoin(BASE_DOMAIN, a_tag["href"])
            text_menu = a_tag.get_text(strip=True)
            if "(" in text_menu and ")" in text_menu:
                name_kategori, jumlah_items = text_menu.rsplit("(", 1)
                name_kategori = name_kategori.strip()
                jumlah_items = jumlah_items.strip(")")
            else:
                name_kategori = text_menu.strip()
                jumlah_items = "0"
            print(f"\n=== KATEGORI UTAMA ===\nNama: {name_kategori}\nJumlah items: {jumlah_items}\nURL: {url_menu}\n")
            proses_kategory(url_menu)

def proses_kategory(url_menu):
    soup = get_soup(url_menu)
    if not soup:
        return
    full_kategory = soup.find("div", id="filter-category-body")
    if not full_kategory:
        # kalau tidak ada subkategori, proses langsung daftar produk
        process_product_list(url_menu, "Uncategorized")
        return
    ul_kategory = full_kategory.find("ul")
    if not ul_kategory:
        process_product_list(url_menu, "Uncategorized")
        return
    li_items = ul_kategory.find_all("li", recursive=False)
    for list_menu in li_items:
        a_tag = list_menu.find("a")
        if a_tag and a_tag.get("href"):
            sub_url = urljoin(BASE_DOMAIN, a_tag["href"])
            text_menu = a_tag.get_text(strip=True)
            if "(" in text_menu and ")" in text_menu:
                name_kategori_sub, jumlah_items = text_menu.rsplit("(", 1)
                name_kategori_sub = name_kategori_sub.strip()
                jumlah_items = jumlah_items.strip(")")
            else:
                name_kategori_sub = text_menu.strip()
                jumlah_items = "0"
            print(f"\n--- SUB KATEGORI ---\nNama: {name_kategori_sub}\nJumlah items: {jumlah_items}\nURL: {sub_url}\n")
            process_product_list(sub_url, name_kategori_sub)

# ====== MAIN ======
def main():
    soup = get_soup(BASE_URL)
    if not soup:
        return
    proses_menu_url(soup)

if __name__ == "__main__":
    main()
