import json
import time
import random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc


# =========================
# START BROWSER STEALTH
# =========================
def start_browser():

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)

    return driver


# =========================
# AMBIL URL PRODUK
# =========================
def ambil_semua_url_produk_kategori(driver, category_url):

    print(f"\n🔎 Memindai halaman kategori:")
    print(category_url)

    driver.get(category_url)

    # tunggu halaman render
    time.sleep(random.uniform(5,8))

    soup = BeautifulSoup(driver.page_source, "html.parser")

    product_urls = set()

    # Walmart search pakai NEXT_DATA
    script = soup.find("script", id="__NEXT_DATA__")

    if not script:
        print("❌ NEXT_DATA tidak ditemukan")
        return []

    try:
        data = json.loads(script.string)

        stacks = (
            data["props"]["pageProps"]
            ["initialData"]["searchResult"]["itemStacks"]
        )

        for stack in stacks:
            for item in stack.get("items", []):
                url = item.get("canonicalUrl")
                if url:
                    product_urls.add("https://www.walmart.com" + url)

    except Exception as e:
        print("❌ Error parsing:", e)

    print(f"\n✅ Total URL produk ditemukan: {len(product_urls)}")
    return list(product_urls)


# =========================
# MAIN
# =========================
save_file = "Url-PetFood-2.csv"

if __name__ == "__main__":

    driver = start_browser()

    BASE_URL = "https://www.walmart.com/search"
    PARAMS = "q=pet+food&affinityOverride=store_led"

    semua_produk = set()
    MAX_PAGES = 13

    # buka homepage dulu (penting supaya cookie valid)
    print("🌐 Warmup homepage...")
    driver.get("https://www.walmart.com/")
    time.sleep(5)

    for page_num in range(1, MAX_PAGES + 1):

        page_url = f"{BASE_URL}?{PARAMS}&page={page_num}"

        print(f"\n🚀 MEMPROSES HALAMAN {page_num} DARI {MAX_PAGES}")

        urls = ambil_semua_url_produk_kategori(driver, page_url)

        if not urls:
            print(f"⚠️ Tidak ditemukan produk di halaman {page_num}")

        semua_produk.update(urls)

        print(f"⏳ Jeda keamanan... (Total terkumpul: {len(semua_produk)} URL)")
        time.sleep(random.uniform(4,7))

    print(f"\n🏁 SELESAI!")
    print(f"TOTAL PRODUK UNIK: {len(semua_produk)}")

    with open(save_file, "w", encoding="utf-8") as f:
        for url in semua_produk:
            f.write(url + "\n")

    print(f"💾 Semua URL disimpan ke '{save_file}'")

    driver.quit()
