# open_target_interactive.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
from datetime import datetime
from pathlib import Path
# https://redsky.target.com/redsky_aggregations/v1/web/general_recommendations_placement_v1?category_id=6n69n&channel=WEB&include_sponsored_recommendations=true&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&keyword=&page=%2Fc%2F6n69n&placement_id=plp&pricing_store_id=2776&purchasable_store_ids=2776%2C3393%2C3216%2C3288%2C3217&visitor_id=019A62B62B310201A01F37E81ED9980E&platform=desktop
# ---------- CONFIG ----------
# URL = "https://www.target.com/c/personal-care/-/N-5xtzq"

# URL = "https://www.vitacost.com/vitacost-magtein-magnesium-l-threonate"

URL = "https://www.vitacost.com/supplements-22"
# URL = "https://www.vitacost.com/minerals-7"
# URL = 'https://www.vitacost.com/magnesium-50'


# URL = "https://www.target.com/c/ulta-beauty-at-target/-/N-ueo8r"
# URL = "https://www.target.com/c/viral-beauty-products-trends/-/N-bjjdx"

# URL = "https://www.target.com/p/maybelline-serum-lipstick-with-hyaluronic-acid-0-12oz/-/A-94780975?preselect=94741625#lnk=sametab"
HEADLESS = False
PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ACCEPT_LANGS = "en-US,en;q=0.9"
NAV_TIMEOUT_MS = 60000
OUTPUT_DIR = Path("output_target")
OUTPUT_DIR.mkdir(exist_ok=True)
# ----------------------------

INJECT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
"""

# 🧩 fungsi scroll ke bawah agar semua produk ter-load
def auto_scroll_to_bottom(page, step=1000, max_wait=40):
    print("\n🌀 Scrolling ke bawah untuk memuat semua produk...")
    last_height = 0
    same_height_count = 0
    start_time = time.time()

    while True:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(1.5)  # beri waktu JS untuk load produk

        # ambil tinggi halaman sekarang
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            same_height_count += 1
        else:
            same_height_count = 0
        last_height = new_height

        # kalau sudah 3x tidak berubah, artinya sudah sampai bawah
        if same_height_count >= 3:
            print("✅ Sudah mencapai bagian paling bawah halaman.")
            break

        # stop kalau sudah terlalu lama
        if time.time() - start_time > max_wait:
            print("⚠️ Waktu scroll habis, mungkin masih ada item yang belum muncul.")
            break

def inspect_product_cards(page, do_scroll_if_empty=True):
    print("\n🔍 Mencari produk di Vitacost (fallback multi-selector)...")

    # helper kecil untuk ambil teks / attr aman
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

    # kalau belum discroll, lakukan scroll singkat agar lazy-load mulai
    if do_scroll_if_empty:
        print("→ Melakukan scroll singkat untuk memicu lazy-load...")
        page.evaluate("window.scrollBy(0, 1000);")
        page.wait_for_timeout(1200)

    # list selector kandidat (cek satu-per-satu)
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
        try:
            container = page.query_selector(sel)
        except Exception as e:
            container = None

        if not container:
            # print(f" - not found: {sel}")
            continue

        # kalau container ada, coba temukan item di dalamnya
        print(f"✅ Menemukan container: {sel}")
        # beberapa kemungkinan item selector
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

        # ambil semua candidate items (gabungan)
        items = []
        for it_sel in item_selectors:
            hits = container.query_selector_all(it_sel)
            if hits and len(hits) > 0:
                # gunakan hits jika lebih banyak dari items sekarang
                if len(hits) > len(items):
                    items = hits

        # fallback: kalau items kosong, ambil semua direct children
        if not items:
            items = container.query_selector_all(":scope > *")

        print(f"   → Mengambil {len(items)} elemen kandidat dalam {sel}")

        # tampilkan sampai 50 item (atau kurang)
        max_show = min(200, len(items))
        rows = []
        for i, item in enumerate(items[:max_show], start=1):
            # coba beberapa path untuk title / href / price
            title_el = (item.query_selector("a.product-description")
                        or item.query_selector("a.productTile__Title-sc-1akb0qj-5")
                        or item.query_selector("a.product-page-link")
                        or item.query_selector("a[data-test='@web/ProductCard/ProductCardLink']")
                        or item.query_selector("a[href]"))
            name = safe_text(title_el) or "(no title)"

            href = safe_attr(title_el, "href") if title_el else None
            # normalize href
            if href and href.startswith("/"):
                href = "https://www.vitacost.com" + href
            elif href and href.startswith("http"):
                pass

            # price selectors
            price_el = (item.query_selector("p.pOurPriceM")
                        or item.query_selector("span.sale-price")
                        or item.query_selector("span.productPrice__SalePrice-sc-1gvn2sf-3")
                        or item.query_selector("[data-test='current-price']")
                        or item.query_selector(".productPrice")
                        or item.query_selector(".price")
                        or item.query_selector("span"))
            price = safe_text(price_el) if price_el else "(no price)"

            rows.append((name, price, href))

        # print hasil ringkas
        for idx, (name, price, href) in enumerate(rows[:50], start=1):
            print(f"{idx}. {name} | {price}")
            if href:
                print(f"   → {href}")

        found = True
        break  # cukup pakai container pertama yang valid

    if not found:
        print("❌ Gagal menemukan container produk dengan kandidat selector.")
        # tampilkan beberapa debug info supaya kita bisa tahu DOM mana muncul
        try:
            title = page.title()
            url = page.url
            print("Page title:", title)
            print("Page URL  :", url)
            # print snippet element body pertama 2000 chars
            body_html = page.content()
            print("\n--- SNIPPET HTML (awal halaman, 3000 chars) ---")
            print(body_html[:3000])
            print("\n--- END SNIPPET ---")
        except Exception as e:
            print("Tidak dapat mengambil snippet halaman:", e)

    print("\nSelesai inspect. Jika tidak muncul product, coba ketik 'scroll' lalu 'show' lagi.")


def main():
    print("Starting Playwright (headful). A window should appear...\n")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
            proxy={
                "server": PROXY["server"],
                "username": PROXY.get("username"),
                "password": PROXY.get("password")
            }
        )
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US",
            viewport={"width": 1366, "height": 900},
            timezone_id="America/New_York",
            java_script_enabled=True,
            bypass_csp=True
        )
        context.add_init_script(INJECT_SCRIPT)

        page = context.new_page()
        page.set_extra_http_headers({"Accept-Language": ACCEPT_LANGS})

        try:
            print(f"Navigating to {URL} ... (timeout {NAV_TIMEOUT_MS} ms)")
            page.goto(URL, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            print("⚠️ Timeout, tapi halaman mungkin masih terbuka.")
        except Exception as e:
            print("Navigation error:", e)
            browser.close()
            return

        print("\nHalaman terbuka. Kamu bisa:")
        print(" - Ketik: scroll → scroll otomatis ke bawah")
        print(" - Ketik: show   → tampilkan daftar produk")
        print(" - Ketik: exit   → keluar\n")

        while True:
            cmd = input("command (scroll / show / exit): ").strip().lower()
            if cmd == "scroll":
                auto_scroll_to_bottom(page)
            elif cmd == "show":
                inspect_product_cards(page)
            elif cmd in ["exit", ""]:
                print("Menutup browser dan keluar...")
                try:
                    context.close()
                except:
                    pass
                browser.close()
                break
            else:
                print("Perintah tidak dikenali. Ketik 'scroll', 'show', atau 'exit'.")

if __name__ == "__main__":
    main()


# https://www.target.com/p/maybelline-serum-lipstick-with-hyaluronic-acid-0-12oz/-/A-94780975?preselect=94741625#lnk=sametab
# https://www.target.com/p/e-l-f-glow-reviver-melting-lip-balm-0-52oz/-/A-94414483?preselect=94743503#lnk=sametab
# https://www.target.com/p/summer-fridays-lip-butter-balm-brown-sugar-0-5-oz/-/A-1006820798#lnk=sametab