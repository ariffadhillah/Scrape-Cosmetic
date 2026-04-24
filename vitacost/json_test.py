from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import time
import os
import random
import re


# ============ CONFIG ============
PROXY = {
    "server": "http://82.26.218.177:6485",
    "username": "arssrhsq",
    "password": "x1vpi09f4v1g"
}

INPUT_CSV = "--product_list.csv"
OUTPUT_CSV = "test-6.csv"
FAILED_CSV = "tezt-6.csv"

BASE = "https://www.vitacost.com"



# =================================================================
# ===============      HELPER: SAVE TO CSV       ==================
# =================================================================

def save_failed_url(url, reason=""):
    file_exists = os.path.exists(FAILED_CSV)
    with open(FAILED_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["url", "reason"])
        writer.writerow([url, reason])


def save_to_csv(data, output_file=OUTPUT_CSV):
    if not data:
        return
    
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
    ]

    file_exists = os.path.exists(output_file)

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)



# =================================================================
# ==============      PLAYWRIGHT HELPERS        ===================
# =================================================================

def open_url_safely(page, url, max_retries=10):

    for attempt in range(1, max_retries + 1):
        try:
            print(f"      🔎 Buka produk: {url} (percobaan {attempt}/{max_retries})")
            page.goto(url, timeout=40000, wait_until="load")

            delay = random.randint(100, 100)
            page.wait_for_timeout(delay)

            print(f"         ✅ Berhasil dibuka (delay {delay} ms)")
            return True

        except Exception as e:
            print(f"         ⚠️ ERROR: {e}")

            if attempt == max_retries:
                print("         ❌ Gagal total setelah 10 percobaan")
                save_failed_url(url, str(e))
                return False

            retry_delay = random.randint(2000, 4000)
            print(f"         🔁 Retry dalam {retry_delay} ms...")
            page.wait_for_timeout(retry_delay)

    return False



# =================================================================
# ===========     PARSER & CLEANER FUNCTIONS      ================
# =================================================================

def find_sibling_text(page, label):
    """Cari li yang mengandung label lalu ambil teks setelah ':'."""
    elements = page.query_selector_all("ul.link-line li")
    for li in elements:
        txt = li.inner_text().strip()
        if label.lower() in txt.lower():
            if ":" in txt:
                return txt.split(":", 1)[1].strip()
            return txt.replace(label, "").strip()
    return ""


def find_other_ingredients(page):
    divs = page.query_selector_all("div")

    for div in divs:
        raw_text = div.inner_text().strip()
        raw_html = div.inner_html().strip()

        if raw_text.lower().startswith("other ingredients:"):
            cleaned = raw_html[len("Other Ingredients:"):].strip()
            cleaned = re.sub(r"<br\s*/?>", "\n", cleaned)
            cleaned = re.sub(r"<.*?>", "", cleaned)
            return cleaned.strip()

    return ""


def find_warning_text(page):
    spans = page.query_selector_all("span")

    for span in spans:
        txt = span.inner_text().strip().lower()

        if txt == "warnings":
            parent = span.evaluate_handle("el => el.parentElement.parentElement")
            paragraphs = parent.query_selector_all("p")
            collected = []

            for p in paragraphs:
                html = p.inner_html().strip()
                if not html:
                    continue

                html = re.sub(r"<br\s*/?>", "\n", html)
                html = re.sub(r"<.*?>", "", html).strip()

                if html:
                    collected.append(html)

            return "\n".join(collected)

    return ""


def find_supplement_text(page, label):
    elements = page.query_selector_all("div")

    for div in elements:
        txt = div.inner_text().strip()
        if txt.lower().startswith(label.lower()):
            if ":" in txt:
                return txt.split(":", 1)[1].strip()
            return txt.replace(label, "").strip()

    return ""


def extract_supplement_facts(page):
    rows = page.query_selector_all("tbody tr")
    results = []

    for tr in rows:
        tds = tr.query_selector_all("td")
        if len(tds) != 3:
            continue

        td1 = tds[0].inner_text().strip()
        td2 = tds[1].inner_text().strip()
        td3 = tds[2].inner_text().strip()

        if td1 == "" and "Amount Per Serving" in td2:
            continue

        name_html = tds[0].inner_html().strip()
        amount = td2
        dv = td3

        name_clean = re.sub(r"<.*?>", "", name_html.replace("<br>", " ")).strip()

        dv = "no dv" if dv in ["", "*"] else f"{dv} dv"

        results.append(f"{name_clean} - {amount} - {dv}")

    return results


def supplement_list_to_dict(supplements):
    return {f"Supplement Ingredient {i}": item for i, item in enumerate(supplements, 1)}


def extract_product_details(page):
    raw = page.locator("#productDetails").inner_text()
    raw = raw.replace("\xa0", " ")
    raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw)
    return raw.strip()


def get_image_url(page):
    try:
        img = page.locator("#productImage img.pb-img").first
        src = img.get_attribute("src")

        if not src:
            return ""
        return BASE + src if src.startswith("/") else src

    except Exception:
        return ""


def get_product_category(page):
    items = page.query_selector_all("nav.breadcrumb h3 a")
    return items[-1].inner_text().strip() if items else ""



# =================================================================
# ===================     SCRAPE PRODUK     =======================
# =================================================================

def scrape_product(browser, url):
    context = browser.new_context(proxy=PROXY, ignore_https_errors=True)
    page = context.new_page()

    print(f"      🔎 Buka produk: {url}")

    try:
        ok = open_url_safely(page, url)
        if not ok:
            save_failed_url(url, "open_url_safely failed")
            return None

        # =========================
        # PRODUCT NAME & BRAND
        # =========================
        h1 = page.query_selector("h1[itemprop='name']")
        brand_el = page.query_selector("h1[itemprop='name'] a[itemprop='brand']")

        h1_text = h1.inner_text().strip() if h1 else ""
        brand = brand_el.inner_text().strip() if brand_el else ""
        manufacturer = h1_text.replace(brand, "").strip() if brand else h1_text

        # PRICE
        price_el = page.query_selector('p[itemprop="price"]')
        raw_price = price_el.inner_text().strip() if price_el else ""
        price = raw_price.replace("Our price:", "").replace("$", "").strip()

        # RATING + REVIEWS
        rating_el = page.query_selector(".bv_avgRating_component_container")
        rating = rating_el.inner_text().strip() if rating_el else ""
        review_el = page.query_selector("meta[itemprop='reviewCount']")
        review_count = review_el.get_attribute("content") if review_el else ""

        # OTHERS
        sku = find_sibling_text(page, "SKU")
        servings = find_sibling_text(page, "Servings")
        serving_size = find_supplement_text(page, "Serving Size")
        servings_per_container = find_supplement_text(page, "Servings per Container")
        other_ing = find_other_ingredients(page)
        other_warning = find_warning_text(page)
        product_details = extract_product_details(page)
        category = get_product_category(page)

        supplements = extract_supplement_facts(page)
        supplements_dict = supplement_list_to_dict(supplements)

        image_url = get_image_url(page)

        # RETURN DATA
        return {
            "Product Name": f"{brand} {manufacturer}",
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
        }

    except Exception as e:
        print("         ⚠️ ERROR produk:", e)
        save_failed_url(url, str(e))
        return None

    finally:
        context.close()



# =================================================================
# ==================      MAIN LOOP CSV      ======================
# =================================================================

def scrape_from_csv(browser, csv_file):

    print(f"\n📄 Membaca URL dari CSV: {csv_file}")

    urls = []

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("url", "").strip()
            if url:
                urls.append(url)

    total = len(urls)
    print(f"   → ditemukan {total} URL produk")

    if total == 0:
        print("⚠️ Tidak ada URL ditemukan. Program stop.")
        return

    for idx, product_url in enumerate(urls, start=1):
        print(f"\n[{idx}/{total}] Scraping: {product_url}")

        try:
            data = scrape_product(browser, product_url)
            if data:
                save_to_csv(data)

        except Exception as e:
            print("❌ ERROR scrape:", e)



# =================================================================
# =========================       MAIN       =======================
# =================================================================

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        scrape_from_csv(browser, INPUT_CSV)
        browser.close()



if __name__ == "__main__":
    main()
