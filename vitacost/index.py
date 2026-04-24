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


# =================== INSPECT PRODUCTS ======================
def inspect_product_cards(page):
    print("\n🔍 Mencari produk (fallback multi-selector)...")

    def safe_text(el):
        try:
            return el.inner_text().strip()
        except:
            return ""

    def safe_attr(el, name):
        try:
            return el.get_attribute(name)
        except:
            return None

    candidate_containers = [
        "#resultsForm",
        "ul.productWrapper.spPLB",
        "ul.productWrapper",
        "div.productTileList",
        "div.productTile",
        "div.searchResults",
        "section.product-list",
        "div[data-module-type='ListingPageProductListCards']",
        "div.productBlockWrapper",
        "div.product-grid",
    ]

    found = False
    for sel in candidate_containers:
        container = None
        try:
            container = page.query_selector(sel)
        except:
            pass

        if not container:
            continue

        print(f"✅ Menemukan container: {sel}")

        item_selectors = [
            "li.product-block",
            "div.product-block",
            "div.product-item",
            "div.productTile",
            "div[data-test='@web/ProductCard/ProductCardVariantDefault']",
            "article.product",
            "div.prd",
            "li",
            "div"
        ]

        items = []
        for it_sel in item_selectors:
            hits = container.query_selector_all(it_sel)
            if hits and len(hits) > 0:
                if len(hits) > len(items):
                    items = hits

        # fallback
        if not items:
            items = container.query_selector_all(":scope > *")

        print(f"   → Mengambil {len(items)} elemen kandidat\n")

        rows = []
        for i, item in enumerate(items[:200], start=1):
            title_el = (
                item.query_selector("a.product-description")
                or item.query_selector("a.productTile__Title-sc-1akb0qj-5")
                or item.query_selector("a.product-page-link")
                or item.query_selector("a[data-test='@web/ProductCard/ProductCardLink']")
                or item.query_selector("a[href]")
            )

            name = safe_text(title_el) or "(no title)"
            href = safe_attr(title_el, "href") if title_el else None

            if href and href.startswith("/"):
                href = "https://www.vitacost.com" + href

            price_el = (
                item.query_selector("p.pOurPriceM")
                or item.query_selector("span.sale-price")
                or item.query_selector("span.productPrice__SalePrice-sc-1gvn2sf-3")
                or item.query_selector("[data-test='current-price']")
                or item.query_selector(".productPrice")
                or item.query_selector(".price")
                or item.query_selector("span")
            )

            price = safe_text(price_el) if price_el else "(no price)"

            rows.append((name, price, href))

        for idx, (name, price, href) in enumerate(rows, start=1):
            print(f"{idx}. {name} | {price}")
            if href:
                print(f"   → {href}")
            print()

        found = True
        break

    if not found:
        print("❌ Tidak menemukan container produk apa pun.")


# ======================== MAIN =============================
def main():
    print("🚀 Starting Playwright...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
            proxy=PROXY
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

        # 1️⃣ Scroll otomatis
        auto_scroll(page)

        # 2️⃣ Langsung extract produk
        inspect_product_cards(page)

        page.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
