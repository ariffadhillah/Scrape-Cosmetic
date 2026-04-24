from playwright.sync_api import sync_playwright
import csv
import time
import os
import random


# ====================================================
# 1️⃣ LIST PROXY (rotate otomatis)
# ====================================================
PROXIES = [
    {
        "server": "http://dc.decodo.com:10000",
        "username": "user-spdv8itjmq-country-us",
        "password": "0uHrpir4~kH9Ipb6Wg"
    },
    # kamu bisa menambah proxy lain:
    # { "server": "...", "username": "...", "password": "..." },
]


BASE = "https://www.vitacost.com"
CATEGORY_URL = "https://www.vitacost.com/supplements-22"
MAX_PAGE = 235

CSV_FILE = "--product_list.csv"
FAILED_FILE = "--failed_pages.csv"


# ====================================================
# 2️⃣ INIT CSV
# ====================================================
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["url"])

    if not os.path.exists(FAILED_FILE):
        with open(FAILED_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["page", "url", "error"])


# ====================================================
# 3️⃣ SAVE SUKSES
# ====================================================
def save_to_csv(url_list):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for u in url_list:
            writer.writerow([u])


# ====================================================
# 4️⃣ SAVE GAGAL
# ====================================================
def save_failed(page_number, url, error_message):
    with open(FAILED_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([page_number, url, error_message])


# ====================================================
# 5️⃣ AMBIL PROXY SECARA ROTATE
# ====================================================
def get_proxy(i):
    return PROXIES[i % len(PROXIES)]


# ====================================================
# 6️⃣ PROSES SATU HALAMAN (dengan retry)
# ====================================================
def process_page(p, browser, pg):
    page_url = f"{CATEGORY_URL}?pg={pg}"
    print(f"\n📄 Membuka halaman {pg}/{MAX_PAGE}: {page_url}")

    retries = 3

    for attempt in range(1, retries + 1):
        print(f"   🔁 Attempt {attempt}/{retries}")

        proxy = get_proxy(pg + attempt)  # rotate proxy
        context = browser.new_context(
            proxy=proxy,
            ignore_https_errors=True
        )
        page = context.new_page()

        try:
            page.goto(page_url, timeout=250000)
            page.wait_for_selector("ul.productWrapper.spPLB", timeout=90000)

            items = page.query_selector_all("li.product-block a.ellipsis60")
            print(f"   → ditemukan {len(items)} produk")

            links = []

            for a in items:
                href = a.get_attribute("href")
                if not href:
                    continue
                full = BASE + href.strip()
                links.append(full)
                print("      →", full)

            save_to_csv(links)
            context.close()
            return True  # sukses

        except Exception as e:
            print(f"   ⚠️ Error attempt {attempt}: {e}")
            context.close()

            if attempt == retries:
                print(f"   ❌ Halaman {pg} tetap gagal setelah {retries} attempt")
                save_failed(pg, page_url, str(e))
                return False

            # delay sebelum retry
            time.sleep(random.uniform(2, 5))


# ====================================================
# 7️⃣ MAIN
# ====================================================
def main():
    init_csv()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for pg in range(1, MAX_PAGE + 1):

            # delay random per halaman
            time.sleep(random.uniform(2, 5))

            process_page(p, browser, pg)

        browser.close()

    print("\n============================")
    print(f"✔ Selesai scraping sampai {MAX_PAGE} halaman")
    print("🟡 Halaman gagal ada di failed_pages.csv")
    print("============================")


if __name__ == "__main__":
    main()
