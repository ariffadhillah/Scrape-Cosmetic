#!/usr/bin/env python3
# Final Vitacost Scraper
# Arif F — 2025

import csv
import os
import random
import time
from playwright.sync_api import sync_playwright

# ==========================
# CONFIG
# ==========================
PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}

BASE_URL = "https://www.vitacost.com"
INPUT_CSV = "vitacost_input.csv"
OUTPUT_CSV = "vitacost_output.csv"


# ==========================
# UTILITY: Safe Goto
# ==========================
def open_url_safely(page, url, retries=3):
    for attempt in range(1, retries + 1):
        try:
            page.goto(url, timeout=120000)
            return True
        except Exception as e:
            print(f"         ⚠️ Gagal buka (attempt {attempt}/{retries}): {e}")
            time.sleep(2)

    return False


# ==========================
# UTILITY: Ambil Text Sibling
# ==========================
def find_sibling_text(page, label):
    el = page.query_selector(f"td:has-text('{label}') + td")
    return el.inner_text().strip() if el else ""


def find_supplement_text(page, label):
    el = page.query_selector(f"table.suppfacts td:has-text('{label}') + td")
    return el.inner_text().strip() if el else ""


def find_other_ingredients(page):
    el = page.query_selector("p:has-text('Other Ingredients')")
    return el.inner_text().replace("Other Ingredients:", "").strip() if el else ""


def find_warning_text(page):
    el = page.query_selector("p:has-text('Warning')")
    return el.inner_text().replace("Warning:", "").strip() if el else ""


def extract_product_details(page):
    div = page.query_selector("#product-detail-text")
    return div.inner_text().strip() if div else ""


# ==========================
# EXTRACT Supplement Facts
# ==========================
def extract_supplement_facts(page):
    rows = page.query_selector_all("table.suppfacts tr")
    results = []

    for r in rows:
        t = r.inner_text().strip()
        if t and ":" not in t and len(t) > 2:
            results.append(t)

    return results


def supplement_list_to_dict(items):
    d = {}
    for it in items:
        parts = it.split(" ")
        key = parts[0]
        d[key] = it
    return d


# ==========================
# IMAGE URL
# ==========================
def get_image_url(page):
    img = page.query_selector("#productImage img")
    if not img:
        return ""

    src = img.get_attribute("src")
    if not src:
        return ""

    if src.startswith("/"):
        return BASE_URL + src
    return src


# ==========================
# SAVE TO CSV
# ==========================
def save_to_csv(data, output_file=OUTPUT_CSV):
    if not data:
        return

    csv_fields = [
        "url",
        "product_name",
        "product_manufacturer",
        "price",
        "rating",
        "review_count",
        "sku",
        "shipping_weight",
        "servings",
        "Serving Size",
        "servings_per_container",

        # supplement
        "supplement_ingredients_list",
        "supplement_ingredients_dict",
        "supplement_ingredients_joined",

        "other_ingredients",
        "warning",
        "product_details",

        "image_url",
    ]

    file_exists = os.path.exists(output_file)

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


# ==========================
# SCRAPE PRODUCT
# ==========================
def scrape_product(browser, url):
    context = browser.new_context(
        proxy=PROXY,
        ignore_https_errors=True,
    )
    page = context.new_page()

    print(f"      🔎 Buka produk: {url}")

    try:
        ok = open_url_safely(page, url)
        if not ok:
            print("         ❌ Produk gagal dibuka, skip.")
            return None

        # TITLE + BRAND
        h1 = page.query_selector("h1[itemprop='name']")
        brand_el = page.query_selector("h1[itemprop='name'] a[itemprop='brand']")

        h1_text = h1.inner_text().strip() if h1 else ""
        brand = brand_el.inner_text().strip() if brand_el else ""
        manufacturer = h1_text.replace(brand, "").strip() if brand else h1_text

        # PRICE
        price_el = page.query_selector('p[itemprop="price"]')
        if price_el:
            raw_price = price_el.inner_text().strip()
            price = raw_price.replace("Our price:", "").replace("$", "").strip()
        else:
            price = ""

        # RATING & REVIEW COUNT
        rating_el = page.query_selector(".bv_avgRating_component_container")
        rating = rating_el.inner_text().strip() if rating_el else ""

        review_count_el = page.query_selector("meta[itemprop='reviewCount']")
        review_count = review_count_el.get_attribute("content") if review_count_el else ""

        # SKUs
        sku = find_sibling_text(page, "SKU")
        weight = find_sibling_text(page, "Weight")
        servings = find_sibling_text(page, "Servings")
        serving_size = find_supplement_text(page, "Serving Size")
        servings_per_container = find_supplement_text(page, "Servings per Container")
        other_ing = find_other_ingredients(page)
        other_warning = find_warning_text(page)
        product_details = extract_product_details(page)

        # Supplement
        supplements = extract_supplement_facts(page)
        supplement_joined = ", ".join(supplements) if supplements else ""
        supplements_dict = supplement_list_to_dict(supplements)

        # Image
        image_url = get_image_url(page)

        print("         → IMAGE:", image_url)

        return {
            "url": url,
            "product_name": brand,
            "product_manufacturer": manufacturer,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "sku": sku,
            "shipping_weight": weight,
            "servings": servings,
            "Serving Size": serving_size,
            "servings_per_container": servings_per_container,

            "supplement_ingredients_list": supplements,
            "supplement_ingredients_dict": supplements_dict,
            "supplement_ingredients_joined": supplement_joined,

            "other_ingredients": other_ing,
            "warning": other_warning,
            "product_details": product_details,

            "image_url": image_url
        }

    except Exception as e:
        print("         ⚠️ ERROR produk:", e)
        return None

    finally:
        context.close()


# ==========================
# MAIN
# ==========================
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

        for i, url in enumerate(url_list, start=1):
            print(f"[{i}/{len(url_list)}] Scraping: {url}")

            data = scrape_product(browser, url)

            if data:
                save_to_csv(data, OUTPUT_CSV)

            # delay random supaya tidak terlalu cepat
            time.sleep(random.uniform(2, 5))

        browser.close()

    print("\n🎉 SELESAI! Semua URL berhasil diproses.\n")


if __name__ == "__main__":
    main()
