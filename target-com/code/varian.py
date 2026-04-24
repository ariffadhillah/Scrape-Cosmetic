# open_target_auto_full_variants.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import re

# ---------- CONFIG ----------
URL = "https://www.target.com/c/new-in-makeup/-/N-6n69n"
HEADLESS = False
PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ACCEPT_LANGS = "en-US,en;q=0.9"
NAV_TIMEOUT_MS = 60000
# ----------------------------

INJECT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
"""

# ---------- HELPERS ----------
def auto_scroll_to_bottom(page, step=1000, max_wait=40):
    """Scroll sampai tidak berubah lagi (lazy load)."""
    print("\n🌀 Scrolling ke bawah untuk memuat semua produk...")
    last_height = 0
    same_height_count = 0
    start_time = time.time()

    while True:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(2)
        new_height = page.evaluate("document.body.scrollHeight")

        if new_height == last_height:
            same_height_count += 1
        else:
            same_height_count = 0
        last_height = new_height

        if same_height_count >= 3:
            print("✅ Sudah mencapai bagian paling bawah halaman.")
            break
        if time.time() - start_time > max_wait:
            print("⚠️ Waktu scroll habis (mungkin masih ada item belum muncul).")
            break


def click_and_extract_details(product_page):
    """
    Klik accordion 'Details' / 'Description' lalu ekstrak:
    - Highlights (list)
    - Description (string)
    """
    print("🟦 Mencari accordion 'Details'...")

    # cari tombol Details
    btn = product_page.query_selector('button:has(h3:text("Details"))')
    if not btn:
        btn = product_page.query_selector('button:has-text("Details")')
    if not btn:
        print("❌ Accordion 'Details' tidak ditemukan.")
        return {
            "highlights": [],
            "description": None
        }

    # cek apakah sudah terbuka
    expanded = btn.get_attribute("aria-expanded")
    if expanded == "false":
        print("➡️ Membuka accordion Details...")
        try:
            btn.click()
        except:
            product_page.evaluate("(el) => el.click()", btn)

        product_page.wait_for_timeout(800)

    # ✅ Ambil description
    desc = None
    try:
        d = product_page.query_selector('[data-test="item-details-description"]')
        desc = d.inner_text().strip() if d else None
    except:
        desc = None

    # ✅ Ambil highlights (jika ada)
    highlights = []
    try:
        li_list = product_page.query_selector_all('[data-test="@web/ProductDetailPageHighlights"] li span')
        for li in li_list:
            txt = li.inner_text().strip()
            if txt:
                highlights.append(txt)
    except:
        pass

    print("   → Description ditemukan" if desc else "   → Description tidak ada")
    print(f"   → {len(highlights)} highlights ditemukan")

    return {
        "highlights": highlights,
        "description": desc
    }



def wait_for_product_cards(page, timeout=15000):
    """Tunggu sampai container & minimal 1 product card muncul."""
    print("⏳ Menunggu product list muncul...")

    try:
        # Tunggu container
        page.wait_for_selector('div[data-module-type="ListingPageProductListCards"]',
                               timeout=timeout)

        # Tunggu minimal 1 card
        page.wait_for_selector('div[data-test="@web/ProductCard/ProductCardVariantDefault"]',
                               timeout=timeout)

        print("✅ Product list siap ditampilkan.")
        return True
    except:
        print("❌ Product list tidak muncul dalam batas waktu.")
        return False


def open_product_page(context, full_url):
    """Buka halaman produk di tab baru dan kembalikan page object (tidak menutupnya)."""
    print(f"\n🔍 Membuka halaman produk: {full_url}")
    new_page = context.new_page()
    try:
        # DOMContentLoaded lebih stabil pada situs besar
        new_page.goto(full_url, timeout=60000, wait_until="domcontentloaded")
        # Sedikit scroll supaya elemen lazy-load muncul
        new_page.wait_for_timeout(1000)
        new_page.evaluate("window.scrollBy(0, 300)")
        new_page.wait_for_timeout(1500)
        print("✅ Halaman produk terbuka.")
        return new_page
    except Exception as e:
        print(f"   ❌ Gagal membuka halaman produk: {e}")
        try:
            new_page.close()
        except:
            pass
        return None

# ---------- CORE: klik varian lalu ekstrak data ----------
def click_and_extract_variants(product_page):
    """
    Pada page produk yang sudah terbuka, cari variation selector,
    klik setiap <ul><li><a> varian, lalu ekstrak data produk hasil klik.
    Kembalikan list dict per varian.
    """
    results = []
    if not product_page:
        print("❌ product_page is None — skip variants.")
        return results

    print("\n🎨 Mencari variation selector di page produk...")
    selectors = product_page.query_selector_all('div[data-module-type="ProductDetailVariationSelector"]')

    if not selectors:
        print("⚠️ Tidak menemukan ProductDetailVariationSelector di halaman ini.")
        return results

    print(f"✅ Ditemukan {len(selectors)} variation section(s).")

    for s_idx, selector in enumerate(selectors, start=1):
        print(f"\n--- Section #{s_idx} ---")
        # ambil list links (ul li a)
        links = selector.query_selector_all("ul li a")
        if not links:
            print("⚠️ Section ini tidak memiliki ul>li>a (skip).")
            continue

        print(f"✅ {len(links)} varian ditemukan di section #{s_idx} — mulai klik satu-per-satu...")

        # iterate by index: re-query needed each loop because DOM may change after click
        for i in range(len(links)):
            # re-query selector & links to avoid stale handles
            selector = product_page.query_selector_all('div[data-module-type="ProductDetailVariationSelector"]')[s_idx-1]
            links = selector.query_selector_all("ul li a")

            if i >= len(links):
                print(f"   ⚠️ Index {i} out of range after re-query. break")
                break

            a = links[i]
            href = a.get_attribute("href") or ""
            label = a.get_attribute("aria-label") or ""
            # print minimal info
            print(f"➡️ Klik varian #{i+1}: {label} ({href})")

            # attempt to click — if clicking navigates away (rare), we handle it
            try:
                a.click()
            except Exception as e:
                # some elements may require JS click via evaluate
                try:
                    product_page.evaluate("(el) => el.click()", a)
                except Exception as e2:
                    print(f"   ❌ Gagal klik varian: {e} / {e2}")
                    continue

            # wait a bit for UI to update (not networkidle; product detail updates in-place)
            product_page.wait_for_timeout(1200)

            # EXTRACT data after click
            # 1) product name/title
            title = None
            try:
                t = product_page.query_selector('h1') or product_page.query_selector('[data-test="product-title"]')
                title = t.inner_text().strip() if t else None
            except:
                title = None

            # 2) price — try multiple selectors
            price = None
            try:
                p = product_page.query_selector('[data-test="current-price"]') \
                    or product_page.query_selector('[data-test="product-price"]') \
                    or product_page.query_selector('[data-test="selling-price"]') \
                    or product_page.query_selector('span[data-test="price"]') \
                    or product_page.query_selector('.h-padding-r-tight')  # fallback
                price = p.inner_text().strip() if p else None
            except:
                price = None

            # 3) availability / stock
            availability = None
            try:
                # check for common indicators of out-of-stock
                sold_out_el = product_page.query_selector("text=Out of stock") or product_page.query_selector("text=Out of Stock") \
                    or product_page.query_selector("text=Sold out") or product_page.query_selector('[data-test="out-of-stock"]')
                if sold_out_el:
                    availability = "Out of stock"
                else:
                    # check add-to-cart button text / disabled state
                    add_btn = product_page.query_selector('button[data-test="add-to-cart-button"]') \
                        or product_page.query_selector('button[aria-label*="Add to cart"]') \
                        or product_page.query_selector('button[data-test="addToCartButton"]')
                    if add_btn:
                        disabled = add_btn.get_attribute("disabled")
                        if disabled is not None:
                            availability = "Out of stock"
                        else:
                            availability = add_btn.inner_text().strip() or "Available"
                    else:
                        availability = "Unknown"
            except:
                availability = "Unknown"

            # 4) main image URL
            image_url = None
            try:
                img = product_page.query_selector('img[data-test="image-gallery-item-0"]') \
                      or product_page.query_selector('div img') \
                      or product_page.query_selector('img[src*="target.scene7.com"]')
                if img:
                    image_url = img.get_attribute("src") or img.get_attribute("data-src")
            except:
                image_url = None

            # 5) SKU / TCIN (try meta tags, visible labels, or URL fallback)
            sku = None
            try:
                m = product_page.query_selector('meta[itemprop="sku"]') or product_page.query_selector('meta[name="sku"]')
                if m:
                    sku = m.get_attribute("content")
            except:
                sku = None

            if not sku:
                # try to find TCIN label on page
                try:
                    tcin_el = product_page.query_selector("text=TCIN") or product_page.query_selector("text=TCIN:")
                    if tcin_el:
                        # get sibling text: evaluate simple JS
                        sku = product_page.evaluate("""
                            () => {
                                const el = document.querySelector('div:has(span:contains("TCIN"))') || document.querySelector('div:contains("TCIN")');
                                if (!el) return null;
                                return el.innerText.replace(/\\s+/g,' ').trim();
                            }
                        """)
                except:
                    sku = None

            if not sku:
                # fallback: try parse product id in URL (A-xxxx)
                try:
                    match = re.search(r'/A-(\d+)', (href or ""))
                    if match:
                        sku = "A-" + match.group(1)
                    else:
                        # try product page url
                        cur = product_page.url
                        m2 = re.search(r'/A-(\d+)', cur)
                        if m2:
                            sku = "A-" + m2.group(1)
                except:
                    pass

            # collect result
            variant_info = {
                "section_index": s_idx,
                "variant_index": i+1,
                "variant_label": label,
                "variant_href": href,
                "product_title": title,
                "price": price,
                "availability": availability,
                "image": image_url,
                "sku": sku,
                "product_page_url": product_page.url
            }
            results.append(variant_info)

            # print summary for this variant
            print("   → title:", title)
            print("   → price:", price)
            print("   → availability:", availability)
            print("   → image:", image_url)
            print("   → sku:", sku)

    print("\n🎉 Selesai klik + ekstrak varian untuk halaman ini.")
    return results

# ---------- PRODUCT LISTING & PAGINATION ----------
def inspect_product_cards(page, context):
    """Ambil semua product card dari listing, buka product page, klik varian, ekstrak data."""
    print("\n🔍 Mencari daftar produk...")
    container = page.query_selector('div[data-module-type="ListingPageProductListCards"]')
    if not container:
        print("❌ Tidak menemukan container 'ListingPageProductListCards'.")
        return

    items = container.query_selector_all('div[data-test="@web/ProductCard/ProductCardVariantDefault"]')
    print(f"✅ Ditemukan {len(items)} produk.\n")

    for i, item in enumerate(items, start=1):
        try:
            title_el = item.query_selector('a[data-test="product-title"]') or item.query_selector('a[data-test="@web/ProductCard/ProductCardLink"]')
            name = title_el.inner_text().strip() if title_el else "(no title)"
            href = title_el.get_attribute("href") if title_el else None
            price_el = item.query_selector('[data-test="current-price"]') or item.query_selector('[data-test="product-price"]')
            price_text = price_el.inner_text().strip() if price_el else "(no price)"

            print(f"{i}. {name} | {price_text}")

            if href:
                full_url = f"https://www.target.com{href}" if href.startswith("/") else href
                product_page = open_product_page(context, full_url)

                if product_page:
                    # klik semua varian di product page dan ambil data tiap varian
                    variant_results = click_and_extract_variants(product_page)
                    # tampilkan ringkasan minimal
                    for vr in variant_results:
                        print(f"    • [{vr['variant_index']}] {vr['variant_label']} | {vr['price']} | {vr['availability']}")
                    # selesai -> tutup tab produk
                    product_page.close()
                else:
                    print("   ❌ Skip varian karena halaman produk gagal dibuka")

        except Exception as e:
            print(f"   ⚠️ Gagal membaca item {i}: {e}")

def go_through_pagination(page, context, max_pages=None):
    """Loop through pages clicking 'next' until last or max_pages reached."""
    page_num = 1
    while True:
        # print(f"\n📄 Sedang di halaman {page_num}")
        # auto_scroll_to_bottom(page)
        # inspect_product_cards(page, context)

        print(f"\n📄 Sedang di halaman {page_num}")

        # ✅ Tunggu hingga produk benar-benar muncul
        wait_for_product_cards(page)

        # ✅ Scroll untuk load semua item
        auto_scroll_to_bottom(page)

        # ✅ Baru ambil datanya
        inspect_product_cards(page, context)


        # optional stopping
        if max_pages and page_num >= max_pages:
            print("🔒 max_pages reached, stop.")
            break

        next_button = page.query_selector('button[data-test="next"]')
        if not next_button:
            print("❌ Tombol next tidak ditemukan. Selesai.")
            break
        if next_button.get_attribute("disabled") is not None:
            print("✅ Sudah di halaman terakhir.")
            break

        try:
            print("➡️ Klik tombol next...")
            next_button.click()
            # wait DOMContentLoaded-like; networkidle often never happens on heavy pages
            page.wait_for_timeout(1800)
            page_num += 1
        except Exception as e:
            print("⚠️ Gagal klik next:", e)
            break

# ---------- MAIN ----------
def main():
    print("🚀 Starting Playwright (headful)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, args=["--no-sandbox"], proxy=PROXY)
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US",
            viewport={"width": 1366, "height": 900},
            timezone_id="America/New_York"
        )
        context.add_init_script(INJECT_SCRIPT)

        page = context.new_page()
        page.set_extra_http_headers({"Accept-Language": ACCEPT_LANGS})

        try:
            print(f"🌐 Navigating to {URL} ...")
            page.goto(URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            print("⚠️ Timeout: halaman masih loading tapi akan dilanjutkan.")
        except Exception as e:
            print("❌ Navigation error:", e)
            browser.close()
            return

        # otomatis scroll & jalankan pagination
        go_through_pagination(page, context)

        print("\n✅ Semua proses selesai. Browser dibiarkan terbuka untuk inspeksi manual.")
        print("Tutup browser secara manual jika sudah selesai.")
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nMenutup browser...")
            browser.close()


if __name__ == "__main__":
    main()
