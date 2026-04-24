from playwright.sync_api import sync_playwright
import csv, os, re


PROXY = {
    "server": "http://23.236.247.191:8223",
    "username": "arssrhsq",
    "password": "x1vpi09f4v1g"
}

INPUT_CSV = "--product_list.csv"
OUTPUT_CSV = "vitacost_output_fast.csv"
FAILED_CSV = "vitacost_failed_fast.csv"
BASE = "https://www.vitacost.com"


# ============================================
# SMALL UTILS
# ============================================
def clean(x):
    return x.replace("\xa0", " ").replace("\n", " ").strip() if x else ""


def save_failed(url, reason):
    new = not os.path.exists(FAILED_CSV)
    with open(FAILED_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["url", "reason"])
        w.writerow([url, reason])


# ============================================
# LOAD PAGE WITH RETRY (ANTI ERROR)
# ============================================
def load_page(page, url):
    for attempt in range(1, 4):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Check if product loaded
            if page.locator("p[itemprop='price']").count() > 0:
                return True

            # If no price, reload
            page.reload(wait_until="domcontentloaded", timeout=60000)

            if page.locator("p[itemprop='price']").count() > 0:
                return True

        except Exception:
            pass

    return False


# ============================================
# PARSE SUPPLEMENT FACTS
# ============================================
def parse_supplements(page):
    supplements = {}
    rows = page.locator("#supplementFactsPanel table tr")

    for i in range(rows.count()):
        tds = rows.nth(i).locator("td")
        if tds.count() < 2:
            continue
        name = clean(tds.nth(0).inner_text())
        value = clean(tds.nth(1).inner_text())
        supplements[name] = value

    return supplements


# ============================================
# SCRAPE PRODUCT (SAFE VERSION)
# ============================================
def scrape_product(page, url):

    # LOAD PAGE SAFELY
    ok = load_page(page, url)
    if not ok:
        save_failed(url, "PAGE LOAD FAILED")
        return None

    # ===========================
    # TITLE, BRAND
    # ===========================
    h1 = page.locator("h1[itemprop='name']")
    brand_el = page.locator("h1[itemprop='name'] a[itemprop='brand']")

    name_raw = clean(h1.inner_text()) if h1.count() else ""
    brand = clean(brand_el.inner_text()) if brand_el.count() else ""
    manufacturer = name_raw.replace(brand, "").strip()

    # ===========================
    # PRICE
    # ===========================
    price_el = page.locator("p[itemprop='price']")
    price = clean(price_el.inner_text()).replace("Our price:", "").replace("$", "")

    # ===========================
    # RATING / REVIEWS
    # ===========================
    rating = ""
    if page.locator(".bv_avgRating_component_container").count():
        rating = clean(page.locator(".bv_avgRating_component_container").inner_text())

    review_count = ""
    meta_review = page.locator("meta[itemprop='reviewCount']")
    if meta_review.count():
        review_count = meta_review.get_attribute("content")

    # ===========================
    # SKU
    # ===========================
    sku = ""
    for li in page.locator("ul.link-line li").all():
        t = clean(li.inner_text())
        if "SKU" in t:
            sku = t.split(":")[-1].strip()

    # ===========================
    # CATEGORY
    # ===========================
    bc = page.locator("nav.breadcrumb h3 a")
    category = clean(bc.nth(bc.count() - 1).inner_text()) if bc.count() else ""

    # ===========================
    # PRODUCT DETAILS
    # ===========================
    details = clean(page.locator("#productDetails").inner_text()) if page.locator("#productDetails").count() else ""

    # ===========================
    # IMAGE
    # ===========================
    img = page.locator("#productImage img.pb-img")
    image_url = ""
    if img.count():
        image_url = img.get_attribute("src")
        if image_url.startswith("/"):
            image_url = BASE + image_url

    # ===========================
    # SUPPLEMENT FACTS
    # ===========================
    supplements_dict = parse_supplements(page)

    serving_size = ""
    servings_per_container = ""

    # extract serving size + servings per container
    for k, v in supplements_dict.items():
        low = f"{k} {v}".lower()
        if "serving size" in low:
            serving_size = v
        if "servings per container" in low:
            servings_per_container = v

    # ===========================
    # OTHER INGREDIENTS
    # ===========================
    other_ing = clean(page.locator("div#otherIngredients").inner_text()) if page.locator("div#otherIngredients").count() else ""

    # ===========================
    # WARNINGS
    # ===========================
    other_warning = clean(page.locator("div#warning").inner_text()) if page.locator("div#warning").count() else ""

    # RETURN FINAL STRUCTURE
    return {
        "Product Name": f"{brand} {manufacturer}",
        "Product Manufacturer": brand,
        "Price": f"'{price}",
        "Servings": "",
        "Rating": f"'{rating}",
        "Reviews": review_count,
        "Product Image URL": image_url,
        "Details": details,
        "Supplement Facts - Serving Size": serving_size,
        "servings per container": servings_per_container,
        "supplement_ingredients_dict": supplements_dict,
        "Other Ingredients": other_ing,
        "Warnings": other_warning,
        "Product Url": url,
        "SKU": sku,
        "Category": category,
    }


# ============================================
# SAVE RESULT
# ============================================
def save_row(data):
    new = not os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=data.keys())
        if new:
            w.writeheader()
        w.writerow(data)


# ============================================
# MAIN LAUNCHER
# ============================================
def main():

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        urls = [r["url"] for r in csv.DictReader(f)]

    print(f"Total URL: {len(urls)}")

    with sync_playwright() as p:

        # BEST BROWSER FOR PROXY: CHROMIUM
        browser = p.chromium.launch(proxy=PROXY, headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="en-US",
            timezone_id="America/New_York"
        )

        # BLOCK RESOURCE BERAT
        context.route("**/*", lambda route: (
            route.abort()
            if route.request.resource_type in ["image", "font", "stylesheet", "media", "other"]
            else route.continue_()
        ))

        page = context.new_page()

        # PROCESS ALL URL
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Scraping → {url}")
            try:
                data = scrape_product(page, url)
                if data:
                    save_row(data)
            except Exception as e:
                save_failed(url, f"CRASH: {e}")

        browser.close()

    print("Selesai scraping (ANTI ERROR version) ⚡")


if __name__ == "__main__":
    main()
