from playwright.sync_api import sync_playwright
import re
import random
import time
import csv
import csv
import os

# PROXY = {
#     "server": "http://dc.decodo.com:10000",
#     "username": "user-spdv8itjmq-country-us",
#     "password": "0uHrpir4~kH9Ipb6Wg"
# }

# PROXY = {
#     "server": "http://23.236.247.191:8223",
#     "username": "arssrhsq",
#     "password": "x1vpi09f4v1g"
# }


PROXY = {
    "server": "http://82.26.218.177:6485",
    "username": "arssrhsq",
    "password": "x1vpi09f4v1g"
}


# PROXY = {
#     "server": "216.205.52.253:80"
# }


INPUT_CSV = "--product_list.csv"
OUTPUT_CSV="vitacost_output-19.csv"
FAILED_CSV = "vitacost_failed-19.csv"
# CSV_FILE = "product_list.csv"   # ganti sesuai lokasi file CSV kamu

BASE = "https://www.vitacost.com"
CATEGORY_URL = "https://www.vitacost.com/supplements-22"
MAX_PAGE = 235





def save_failed_url(url, reason=""):
    file_exists = os.path.exists(FAILED_CSV)
    with open(FAILED_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["url", "reason"])
        writer.writerow([url, reason])


def save_to_csv(data, output_file=OUTPUT_CSV):
    """
    Menyimpan satu produk (dictionary) ke file CSV.
    Auto-create header jika file belum ada.
    """
    if not data:
        return
    
    # Tambahkan semua key baru di scrape_product
    csv_fields = [
        "Product Name",
        "Product Manufacturer",
        "Price",
        "Servings",
        "Rating",
        "Reviews",
        "Product Image URL",
        "Details",
        "Supplement Facts - Serving Size",
        "servings per container",
        "supplement_ingredients_dict",
        "Other Ingredients",
        "Warnings",
        "Product Url",
        "SKU",
        "Category",

        # "url",
        # "product_name",
        # "product_manufacturer",
        # "price",
        # "rating",
        # "review_count",
        # "sku",
        # "shipping_weight",
        # "servings",
        # "Serving Size",
        # "servings_per_container",

        # # supplement
        # # "supplement_ingredients_list",
        # "supplement_ingredients_dict",
        # # "supplement_ingredients_joined",

        # # new fields
        # "other_ingredients",
        # "warning",
        # "product_details",

        # # image
        # "image_url",
    ]


    file_exists = os.path.exists(output_file)

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)

        # Buat header jika file baru
        if not file_exists:
            writer.writeheader()

        # Tuliskan data (yang tidak ada akan kosong)
        writer.writerow(data)


# def open_url_safely(page, url, max_retries=10):
#     """
#     Membuka URL dengan Playwright dengan retry + delay acak agar stabil.
#     """
#     for attempt in range(1, max_retries + 1):

#         try:
#             print(f"      🔎 Buka produk: {url} (percobaan {attempt}/{max_retries})")

#             # BUKA URL — ini yang benar
#             page.goto(url, timeout=45000, wait_until="load")

#             # Random delay supaya tidak dianggap bot
#             delay = random.randint(1500, 3000)
#             page.wait_for_timeout(delay)

#             print(f"         ✅ Berhasil dibuka (delay {delay} ms)")
#             return True

#         except Exception as e:
#             print(f"         ⚠️ ERROR: {e}")

#             if attempt == max_retries:
#                 print("         ❌ Gagal total setelah 3 percobaan")
#                 return False

#             retry_delay = random.randint(2000, 4000)
#             print(f"         🔁 Retry dalam {retry_delay} ms...")
#             page.wait_for_timeout(retry_delay)

#     return False

def open_url_safely(page, url, max_retries=10):

    for attempt in range(1, max_retries + 1):
        try:
            print(f"      🔎 Buka produk: {url} (percobaan {attempt}/{max_retries})")

            page.goto(url, timeout=50000, wait_until="load")

            delay = random.randint(100, 100)
            page.wait_for_timeout(delay)

            print(f"         ✅ Berhasil dibuka (delay {delay} ms)")
            return True

        except Exception as e:
            print(f"         ⚠️ ERROR: {e}")

            # === CATAT GAGAL JIKA MAX ATTEMPT ===
            if attempt == max_retries:
                print("         ❌ Gagal total setelah 10 percobaan")
                save_failed_url(url, str(e))   # <---- ADD THIS LINE
                return False

            retry_delay = random.randint(2000, 4000)
            print(f"         🔁 Retry dalam {retry_delay} ms...")
            page.wait_for_timeout(retry_delay)

    return False



def find_sibling_text(page, label):
    """
    Cari li yang mengandung label, lalu ambil teks setelah ':'.
    Contoh:
    <li>SKU #: 12345</li> → "12345"
    """
    elements = page.query_selector_all("ul.link-line li")
    for li in elements:
        txt = li.inner_text().strip()
        if label.lower() in txt.lower():
            if ":" in txt:
                return txt.split(":", 1)[1].strip()
            # fallback jika tidak ada ':'
            return txt.replace(label, "").strip()
    return ""


def find_other_ingredients(page):
    """
    Cari <div> yang mengandung 'Other Ingredients:'.
    <br> diubah menjadi newline.
    Tag HTML lain dihapus.
    """
    divs = page.query_selector_all("div")

    for div in divs:
        raw_text = div.inner_text().strip()
        raw_html = div.inner_html().strip()

        if raw_text.lower().startswith("other ingredients:"):

            # Ambil HTML tanpa label awal
            cleaned = raw_html[len("Other Ingredients:"):].strip()

            # Ganti <br> atau <br/> atau <br /> menjadi newline
            cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)

            # Hapus tag HTML lainnya seperti <p>, </p>, <i>, dll
            cleaned = re.sub(r"<.*?>", "", cleaned)

            # Bersihkan whitespace
            cleaned = cleaned.strip()

            return cleaned

    return ""



def find_warning_text(page):
    """
    Cari teks 'Warnings' lalu ambil semua <p> sibling setelahnya.
    Tidak menggunakan class.
    """
    # Ambil semua span untuk cari yang tulisannya 'Warnings'
    spans = page.query_selector_all("span")

    for span in spans:
        txt = span.inner_text().strip().lower()

        if txt == "warnings":
            # Ambil parent div
            parent = span.evaluate_handle("el => el.parentElement.parentElement")

            # Ambil semua <p> di dalam parent
            paragraphs = parent.query_selector_all("p")

            collected = []

            for p in paragraphs:
                html = p.inner_html().strip()

                if not html:
                    continue  # skip paragraf kosong

                # Ganti <br> jadi newline
                html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)

                # Hapus tag HTML lainnya
                html = re.sub(r"<.*?>", "", html).strip()

                if html:
                    collected.append(html)

            # Gabung semua paragraf menjadi satu teks
            return "\n".join(collected)

    return ""


def find_supplement_text(page, label):
    """
    Cari <div> yang teksnya mengandung label supplement, contoh:
    'Serving Size:' atau 'Servings per Container:'.

    Tidak menggunakan class, hanya mendeteksi berdasarkan TEXT.
    """
    elements = page.query_selector_all("div")  # ambil semua <div>

    for div in elements:
        txt = div.inner_text().strip()
        
        # cek apakah mengandung label
        if txt.lower().startswith(label.lower()):
            if ":" in txt:
                return txt.split(":", 1)[1].strip()

            # fallback jika tidak ada ':'
            return txt.replace(label, "").strip()
    
    return ""


def extract_supplement_ingredients(page):
    """
    Ambil ingredient di dalam Supplement Facts.
    Hasil: list string 'Name - Amount - DV'
    """
    results = []

    # Ambil semua row dari table Facts
    rows = page.query_selector_all("table tr, tr")

    for tr in rows:
        tds = tr.query_selector_all("td")
        if len(tds) >= 3:
            name  = tds[0].inner_text().strip()
            amt   = tds[1].inner_text().strip()
            dv    = tds[2].inner_text().strip()

            if not name:
                continue

            # Normalisasi DV
            dv_clean = dv if dv not in ["", "*", "-", "†"] else "no dv"

            # Format final
            full = f"{name} - {amt} - {dv_clean}"
            results.append(full)

    return results



def extract_supplement_facts(page):
    rows = page.query_selector_all("tbody tr")
    results = []

    for tr in rows:
        tds = tr.query_selector_all("td")

        # --- Skip jika bukan 3 kolom ingredient ---
        if len(tds) != 3:
            continue

        # --- Skip HEADER row (Amount Per Serving / % Daily Value) ---
        td1 = tds[0].inner_text().strip()
        td2 = tds[1].inner_text().strip()
        td3 = tds[2].inner_text().strip()

        # Jika kolom pertama kosong & kolom kedua = 'Amount Per Serving'
        if td1 == "" and "Amount Per Serving" in td2:
            continue

        # --- Extract HTML nama ---
        name_html = tds[0].inner_html().strip()
        amount = td2
        dv = td3

        # --- Bersihkan nama ingredient (gabungkan <br> dan hapus HTML tag) ---
        name_clean = (
            name_html.replace("<br>", " ")
                     .replace("<br/>", " ")
                     .replace("<br />", " ")
        )

        import re
        name_clean = re.sub(r"<.*?>", "", name_clean).strip()

        # --- Daily Value ---
        if dv == "*" or dv == "":
            dv = "no dv"
        else:
            dv = f"{dv} dv"

        # --- Final ingredient format ---
        final_text = f"{name_clean} - {amount} - {dv}"
        results.append(final_text)

    return results


def supplement_list_to_dict(supplements):
    """
    Ubah list supplement menjadi dict:
    {
        "Supplement Ingredient 1": "...",
        "Supplement Ingredient 2": "..."
    }
    """
    result = {}
    for i, item in enumerate(supplements, 1):
        result[f"Supplement Ingredient {i}"] = item
    return result




def extract_product_details(page):
    # Ambil teks apa adanya dari browser (paling bersih & rapi)
    raw = page.locator("#productDetails").inner_text()

    # Hapus &nbsp;
    raw = raw.replace("\xa0", " ")

    # Rapikan newline berlebihan
    raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw)

    return raw.strip()


def get_image_url(page):
    """
    Mengambil URL utama image hanya dari dalam elemen #productImage.
    """
    try:
        # Cari img.pb-img yang berada di dalam #productImage
        img_locator = page.locator("#productImage img.pb-img").first
        
        # Ambil atribut src
        src = img_locator.get_attribute("src")

        if not src:
            return ""

        # Gabungkan dengan BASE jika berupa relative path
        if src.startswith("/"):
            return BASE + src
        else:
            return src

    except Exception as e:
        print("Error get_image_url:", e)
        return ""


def get_product_category(page):
    """Ambil kategori utama (breadcrumb terakhir)"""
    items = page.query_selector_all("nav.breadcrumb h3 a")
    if not items:
        return ""

    # Ambil teks breadcrumb terakhir
    return items[-1].inner_text().strip()



def scrape_product(browser, url):
    """Scrape halaman produk"""
    # context = browser.new_context(
    #     proxy=PROXY,
    #     ignore_https_errors=True,
    # )

    context = browser.new_context(
        proxy=PROXY,
        ignore_https_errors=True,
    )

    context.route("**/*", lambda route: (
        route.fulfill(status=200, body="") 
        if route.request.resource_type in ["stylesheet", "font"]
        else route.continue_()
    ))

    page = context.new_page()

    # print(f"      🔎 Buka produk: {url}")

    # try:
    #     # page.goto(url, timeout=120000)
    #     # open_url_safely(page, url)

    #     ok = open_url_safely(page, url)
    #     if not ok:
    #         print("         ❌ Produk gagal dibuka, skip.")
    #         return None

    try:
        ok = open_url_safely(page, url)
        if not ok:
            save_failed_url(url, "open_url_safely failed")
            return None


        # ---------------------------
        # BRAND + MANUFACTURER
        # ---------------------------
        h1 = page.query_selector("h1[itemprop='name']")
        brand_el = page.query_selector("h1[itemprop='name'] a[itemprop='brand']")

        h1_text = h1.inner_text().strip() if h1 else ""
        brand = brand_el.inner_text().strip() if brand_el else ""
        manufacturer = h1_text.replace(brand, "").strip() if brand else h1_text

        # ---------------------------
        # PRICE
        # ---------------------------
        price_el = page.query_selector('p[itemprop="price"]')
        if price_el:
            raw_price = price_el.inner_text().strip()
            price = raw_price.replace("Our price:", "").replace("$", "").strip()
        else:
            price = ""

        # ---------------------------
        # RATING + REVIEW COUNT
        # ---------------------------
        rating_el = page.query_selector(".bv_avgRating_component_container")
        rating = rating_el.inner_text().strip() if rating_el else ""

        review_count_el = page.query_selector("meta[itemprop='reviewCount']")
        review_count = review_count_el.get_attribute("content") if review_count_el else ""


        # ---------------------------
        # SKU + SHIPPING WEIGHT + SERVINGS
        # ---------------------------
        sku = find_sibling_text(page, "SKU")
        weight = find_sibling_text(page, "Weight")
        servings = find_sibling_text(page, "Servings")
        serving_size = find_supplement_text(page, "Serving Size")
        servings_per_container = find_supplement_text(page, "Servings per Container")
        other_ing = find_other_ingredients(page)
        other_warning = find_warning_text(page)
        product_details = extract_product_details(page)
        category = get_product_category(page)

        # ---------------------------
        # SUPPLEMENT INGREDIENTS
        # ---------------------------
        # supplements = extract_supplement_ingredients(page)
        # supplement_joined = ", ".join(supplements) if supplements else ""

        # ---------------------------
        # SUPPLEMENT INGREDIENTS
        # ---------------------------
        supplements = extract_supplement_facts(page)
        supplement_joined = ", ".join(supplements) if supplements else ""
        supplements_dict = supplement_list_to_dict(supplements)

        image_url = get_image_url(page)
        




        # PRINT OUTPUT
        print("         → Product Manufacturer:", manufacturer)


        return {
            "Product Name": f'{brand} {manufacturer}',
            "Product Manufacturer": brand,
            "Price": f"'{price}",
            "Servings": servings,
            "Rating": f"'{rating}",
            "Reviews": review_count,
            "Product Image URL": image_url,
            "Details": product_details,
            "Supplement Facts - Serving Size": serving_size,
            "servings per container": servings_per_container,
            "supplement_ingredients_dict": supplements_dict,
            "Other Ingredients": other_ing,
            "Warnings": other_warning,
            "Product Url": url,
            "SKU": sku,
            "Category": category,

            # "shipping_weight": weight,

            # "supplement_ingredients_list": supplements,
            # "supplement_ingredients_joined": supplement_joined,


        }



    except Exception as e:
        print("         ⚠️ ERROR produk:", e)
        save_failed_url(url, str(e))
        return None

    finally:
        context.close()


def scrape_from_csv(browser, csv_file):
    """Baca URL produk dari CSV lalu scrape satu per satu sampai selesai."""
    print(f"\n📄 Membaca URL dari CSV: {csv_file}")

    urls = []

    # --- Ambil URL dari kolom 'url' ---
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            product_url = row.get("url", "").strip()
            if product_url:
                urls.append(product_url)

    total = len(urls)
    print(f"   → ditemukan {total} URL produk")

    if total == 0:
        print("⚠️ Tidak ada URL ditemukan di dalam CSV. Program dihentikan.")
        return

    # --- Proses satu per satu ---
    success = 0

    for idx, product_url in enumerate(urls, start=1):
        print(f"\n[{idx}/{total}] Scraping: {product_url}")

        try:
            scrape_product(browser, product_url)
            success += 1

        except Exception as e:
            print(f"❌ ERROR saat scrape produk: {product_url}")
            print("   →", e)

    print("\n====================================")
    print(f"  🎉 SEMUA URL SELESAI DI-PROSES 📦")
    print(f"  ✔ Total URL: {total}")
    print(f"  ✔ Berhasil  : {success}")
    print(f"  ✘ Gagal     : {total - success}")
    print("====================================\n")



def main():
    # Baca CSV input
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        url_list = [row["url"] for row in reader if row.get("url")]

    print(f"\n=== Total URL yang akan di-scrape: {len(url_list)} ===\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--ignore-certificate-errors"]
        )
        # browser = p.chromium.launch(headless=True)

        # for i, url in enumerate(url_list, start=1):
        #     print(f"[{i}/{len(url_list)}] Scraping: {url}")

        #     data = scrape_product(browser, url)

        #     if data:
        #         save_to_csv(data, OUTPUT_CSV)

        #     # delay random supaya tidak terlalu cepat
        #     time.sleep(random.uniform(2, 5))


        for i, url in enumerate(url_list, start=1):
            print(f"[{i}/{len(url_list)}] Scraping: {url}")

            try:
                data = scrape_product(browser, url)

                if data:
                    save_to_csv(data, OUTPUT_CSV)
                else:
                    save_failed_url(url, "scrape_product returned None")

            except Exception as e:
                print("❌ ERROR fatal:", e)
                save_failed_url(url, str(e))

            time.sleep(random.uniform(1, 1))



        browser.close()

    print("\n🎉 SELESAI! Semua URL berhasil diproses.\n")


if __name__ == "__main__":
    main()
