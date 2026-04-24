import requests
import json
import time
import csv
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time

# === konfigurasi ===
majorcategory = 'Fragrance'

fields = [
    "Major Category",
    "Specific Category",
    "Product ID",
    "SKU ID",
    "Product Brand",
    "Product Desc",
    "Product URL",
    "Product Image Link",
    "Product Ingredients"
]
data_save = []               # akan berisi dict baris CSV
seen_rows = set()            # untuk dedup berdasarkan (product_url, sku_id)
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

def extract_product_urls_from_soup(soup):
    urls = []
    if not soup:
        return urls

    # 1) Cari article yang merupakan product card
    articles = soup.find_all("article")
    for art in articles:
        # cek atribut khas product card
        attrs = art.attrs
        if ("data-test-id" in attrs and "product" in attrs.get("data-test-id", "")) or \
           ("data-product-card-id" in attrs) or \
           (attrs.get("data-test-id") == "product-item"):
            a = art.find("a", href=True)
            if a:
                href = a["href"].strip()
                if "/p/" in href:
                    full = urljoin(BASE_DOMAIN, href)
                    urls.append(full)

    # 2) fallback: cari semua <a> yang mengandung /en-us/p/ atau /p/
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

# def process_product_list(list_url, name_kategori_sub):
#     print(f"\n📂 Memproses daftar produk: {list_url}  (kategori: {name_kategori_sub})")
#     soup = get_soup(list_url)
#     if not soup:
#         return

#     product_urls = extract_product_urls_from_soup(soup)
#     if not product_urls:
#         print("⚠️ Tidak menemukan product items di halaman ini.")
#         return

#     print(f"👉 Ditemukan {len(product_urls)} produk. Memproses tiap product (rate-limited).")
#     for idx, p_url in enumerate(product_urls, 1):
#         print(f"[{idx}/{len(product_urls)}] {p_url}")
#         try:
#             process_product_url(p_url, name_kategori_sub)
#         except Exception as e:
#             print(f"❌ Error memproses {p_url}: {e}")
#         time.sleep(0.6)  # jeda kecil agar tidak over-request

def process_product_list(list_url, name_kategori_sub):
    print(f"\n📂 Memproses daftar produk: {list_url}  (kategori: {name_kategori_sub})")
    
    page = 1
    total_found = 0
    
    while True:
        if page == 1:
            url_page = list_url
        else:
            url_page = f"{list_url}?page={page}"
        
        print(f"\n➡️ Memproses halaman {page}: {url_page}")
        soup = get_soup(url_page)
        if not soup:
            break

        product_urls = extract_product_urls_from_soup(soup)
        if not product_urls:
            print(f"⚠️ Tidak ada produk ditemukan di halaman {page}. Stop pagination.")
            break

        print(f"👉 Ditemukan {len(product_urls)} produk di halaman {page}.")
        for idx, p_url in enumerate(product_urls, 1):
            print(f"[{idx}/{len(product_urls)}] {p_url}")
            try:
                process_product_url(p_url, name_kategori_sub)
                total_found += 1
            except Exception as e:
                print(f"❌ Error memproses {p_url}: {e}")
            time.sleep(0.6)  # jeda kecil agar tidak over-request

        page += 1  # lanjut halaman berikutnya
    
    print(f"✅ Selesai memproses kategori '{name_kategori_sub}', total {total_found} produk.")


def process_product_url(product_url, name_kategori_sub):
    print(f"🔎 Memproses product detail: {product_url}  (kategori: {name_kategori_sub})")
    soup = get_soup(product_url)
    if not soup:
        return

    # Ambil ingredients (jika ada)
    time.sleep(.5)
    final_text = ""
    ingredients_container = soup.find("div", id="benefits-dients-body")
    if ingredients_container:
        paragraphs = ingredients_container.find_all("p")
        cleaned_texts = [p.get_text(strip=True) for p in paragraphs]
        final_text = "\n".join(cleaned_texts).strip().title()

    # Ambil JSON-LD scripts
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    if not scripts:
        print("❌ JSON-LD tidak ditemukan di halaman produk ini.")
        # simpan minimal info kalau mau (opsional) -> skip saat JSON-LD tidak ada
        if final_text:
            print("🧪 Ingredients:\n", final_text)
        return

    def append_row(product_id, sku_id, brand_name, product_desc, url, image, ingredients):
        # dedup berdasarkan (url, sku_id)
        key = (url or "", sku_id or "")
        if key in seen_rows:
            return
        seen_rows.add(key)

        row = {
            "Major Category": majorcategory,
            "Specific Category": name_kategori_sub,
            "Product ID": "'"+product_id or "",
            "SKU ID": "'"+sku_id or "",
            "Product Brand": brand_name or "",
            "Product Desc": product_desc or "",
            "Product URL": url or "",
            "Product Image Link": image or "",
            "Product Ingredients": ingredients or ""
        }
        data_save.append(row)
        print("✅ Row ditambahkan:", row["Product ID"], row["SKU ID"])

    def handle_product_dict(d):
        if not isinstance(d, dict):
            return
        typ = d.get("@type", "")
        if isinstance(typ, list):
            if "Product" not in typ and "ProductGroup" not in typ:
                return
        else:
            if typ not in ("Product", "ProductGroup"):
                return

        
        time.sleep(.5)
        product_name = d.get("name", "") or ""
        brand_name = ""
        brand = d.get("brand", {})
        if isinstance(brand, dict):
            brand_name = brand.get("name", "") or ""

        # jika ada varian
        if "hasVariant" in d and isinstance(d["hasVariant"], list):
            for variant in d["hasVariant"]:
                # product_id / sku_id
                product_id = variant.get("productID") or variant.get("sku") or ""
                sku_id = variant.get("sku") or variant.get("productID") or ""
                color = variant.get("color") or ""
                url = variant.get("url") or d.get("url") or product_url
                image_field = variant.get("image", "")
                image = ""
                if isinstance(image_field, str) and image_field.startswith("/"):
                    image = urljoin("https://hrd-live.cdn.scayle.cloud/", image_field.lstrip("/"))
                else:
                    image = image_field or ""
                product_desc = (product_name + " " + (color or "")).replace(brand_name, "").strip()
                # print(f"   ➡️ Major Category: {majorcategory}")
                # print(f"   ➡️ Specific Category: {name_kategori_sub}")
                # print(f"   ➡️ Product Id: {product_id}")
                # print(f"   ➡️ SKU Id: {sku_id}")
                # print(f"🏷️ Brand: {brand_name}")
                print(f"   ➡️ Product Desc: {product_desc}")
                print(f"   ➡️ Product URL: {url}")
                # print(f"   ➡️ Product Image Link: {image}")
                # if final_text:
                #     print("🧪 Product Ingredients:\n", final_text)
                append_row(product_id, sku_id, brand_name, product_desc, url, image, final_text)

        else:
            product_id = d.get("productID") or d.get("sku") or ""
            sku_id = d.get("sku") or d.get("productID") or ""
            color = d.get("color") or ""
            url = d.get("url") or product_url
            image_field = d.get("image", "")
            image = ""
            if isinstance(image_field, list) and image_field:
                image = image_field[0]
            elif isinstance(image_field, str):
                image = image_field
            product_desc = (product_name + " " + (color or "")).replace(brand_name, "").strip()
            # print(f"   ➡️ Major Category: {majorcategory}")
            # print(f"   ➡️ Specific Category: {name_kategori_sub}")
            # print(f"   ➡️ Product Id: {product_id}")
            # print(f"   ➡️ SKU Id: {sku_id}")
            # print(f"🏷️ Brand: {brand_name}")
            print(f"   ➡️ Product Desc: {product_desc}")
            print(f"   ➡️ Product URL: {url}")
            # print(f"   ➡️ Product Image Link: {image}")
            # if final_text:
            #     print("🧪 Product Ingredients:\n", final_text)
            append_row(product_id, sku_id, brand_name, product_desc, url, image, final_text)

    # parse setiap script (bisa berupa dict atau list)
    for script in scripts:
        script_text = script.string or script.get_text() or ""
        script_text = script_text.strip()
        if not script_text:
            continue
        try:
            data = json.loads(script_text)
        except Exception:
            continue

        if isinstance(data, list):
            for item in data:
                handle_product_dict(item)
        elif isinstance(data, dict):
            if "@graph" in data and isinstance(data["@graph"], list):
                for item in data["@graph"]:
                    handle_product_dict(item)
            else:
                handle_product_dict(data)

def proses_menu_url(soup):
    time.sleep(.5)
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
    time.sleep(.5)
    soup = get_soup(url_menu)
    if not soup:
        return
    full_kategory = soup.find("div", id="filter-category-body")
    if not full_kategory:
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

def save_csv():
    if not data_save:
        print("⚠️ Tidak ada data untuk disimpan.")
        return
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in data_save:
                writer.writerow(row)
        print(f"\n✅ Selesai. {len(data_save)} baris tersimpan ke '{filename}'")
    except Exception as e:
        print(f"❌ Gagal menyimpan CSV: {e}")

def main():
    soup = get_soup(BASE_URL)
    if not soup:
        return
    proses_menu_url(soup)
    # setelah crawling selesai, simpan CSV
    save_csv()

if __name__ == "__main__":
    main()
