from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

# ====================== CONFIG ===========================
URL = "https://www.vitacost.com/supplements-22"

PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
HEADLESS = False
NAV_TIMEOUT = 60000

# Anti-bot JS injection
INJECT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
"""


# =================== AUTO SCROLL ==========================
def auto_scroll(page, max_wait=40):
    print("\n🌀 Scrolling ke bawah untuk memuat semua produk...")
    last_height = 0
    unchanged = 0
    start = time.time()

    while True:
        page.evaluate("window.scrollBy(0, 2000)")
        time.sleep(1.2)

        new_height = page.evaluate("document.body.scrollHeight")

        if new_height == last_height:
            unchanged += 1
        else:
            unchanged = 0

        last_height = new_height

        if unchanged >= 3:
            print("✅ Sudah mencapai dasar halaman.")
            break

        if time.time() - start > max_wait:
            print("⚠️ Timeout scroll.")
            break


# =================== EXTRACT PRODUCTS ======================
def extract_products(page):
    print("\n🔍 Mengambil data produk...")

    page.wait_for_selector(".product-grid", timeout=15000)

    items = page.query_selector_all(".product-grid .product-grid__item")

    print(f"📦 Total produk ditemukan: {len(items)}\n")

    results = []

    for i, item in enumerate(items, 1):
        try:
            title_el = item.query_selector(".product-tile__title")
            price_el = item.query_selector(".product-sales-price")
            link_el = item.query_selector("a.product-tile")

            name = title_el.inner_text().strip() if title_el else "(no title)"
            price = price_el.inner_text().strip() if price_el else "(no price)"
            href = link_el.get_attribute("href") if link_el else None

            if href and not href.startswith("http"):
                href = "https://www.vitacost.com" + href

            print(f"{i}. {name} | {price}")
            print(f"   → {href}\n")

            results.append({
                "name": name,
                "price": price,
                "url": href
            })

        except Exception as e:
            print(f"⚠️ Error membaca item {i}: {e}")

    print("\n🎉 Extract selesai!\n")
    return results


# ======================== MAIN =============================
def main():
    print("🚀 Memulai Playwright...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
            proxy={
                "server": PROXY["server"],
                "username": PROXY["username"],
                "password": PROXY["password"]
            }
        )

        context = browser.new_context(
            user_agent=USER_AGENT,
            java_script_enabled=True,
            viewport={"width": 1366, "height": 900},
            timezone_id="America/New_York"
        )
        context.add_init_script(INJECT_SCRIPT)

        page = context.new_page()

        print(f"Membuka halaman: {URL}")

        try:
            page.goto(URL, wait_until="networkidle", timeout=NAV_TIMEOUT)
        except PlaywrightTimeoutError:
            print("⚠️ Timeout warning, halaman mungkin tetap terbuka.")

        # Auto scroll dulu
        auto_scroll(page)

        # Extract semua produk
        extract_products(page)

        page.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
