
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


# ================================================================
#     NEW FUNCTIONS: description + specifications + label info
# ================================================================

def wait_until_visible(page, selector, timeout=8000):
    """Menunggu selector sampai text muncul (bukan hanya element)."""
    try:
        page.wait_for_selector(selector, timeout=timeout, state="visible")
        el = page.query_selector(selector)
        if el:
            text = el.inner_text().strip()
            if text:
                return text
    except:
        pass
    return None


def extract_description(product_page):
    """Klik tab Details -> Description"""
    print("   🔎 Extracting Description...")

    try:
        # Klik Details (accordion)
        btn = product_page.query_selector('button:has-text("Details")')
        if btn:
            expanded = btn.get_attribute("aria-expanded")
            if expanded == "false":
                btn.click()
                product_page.wait_for_timeout(500)
    except:
        pass

    # Ambil text description
    desc = wait_until_visible(product_page, '[data-test="item-details-description"]')

    if desc:
        print("      ✅ Description OK")
    else:
        print("      ⚠️ Description kosong")

    return desc


def extract_specifications(product_page):
    """Klik tab Specifications lalu ambil tabelnya"""
    print("   🔎 Extracting Specifications...")

    try:
        btn = product_page.query_selector('button:has-text("Specifications")')
        if btn:
            expanded = btn.get_attribute("aria-expanded")
            if expanded == "false":
                btn.click()
                product_page.wait_for_timeout(500)
    except:
        pass

    specs = []
    try:
        rows = product_page.query_selector_all('[data-test="item-details-specifications"] li')
        for r in rows:
            txt = r.inner_text().strip()
            if txt:
                specs.append(txt)
    except:
        pass

    print(f"      ✅ {len(specs)} specifications ditemukan" if specs else "      ⚠️ specs kosong")
    return specs


def extract_label_info(product_page):
    """Klik tab Label Info lalu tunggu sampai text benar-benar muncul"""
    print("   🔎 Extracting Label Info...")

    try:
        btn = product_page.query_selector('button:has-text("Label info")')
        if btn:
            expanded = btn.get_attribute("aria-expanded")
            if expanded == "false":
                btn.click()
                product_page.wait_for_timeout(600)
    except:
        pass

    # Tunggu text muncul
    label_text = wait_until_visible(
        product_page,
        '[data-test="item-details-labelinfo"]'
    )

    if label_text:
        print("      ✅ Label info OK")
    else:
        print("      ⚠️ Label info kosong / tidak muncul")

    return label_text


# ================================================================
#        MODIFIED FINAL VERSION: click_and_extract_variants()
# ================================================================

def click_and_extract_variants(product_page):
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

        links = selector.query_selector_all("ul li a")
        if not links:
            print("⚠️ Section ini tidak memiliki ul>li>a (skip).")
            continue

        print(f"✅ {len(links)} varian ditemukan — mulai proses satu-per-satu...")

        for i in range(len(links)):
            selector = product_page.query_selector_all('div[data-module-type="ProductDetailVariationSelector"]')[s_idx-1]
            links = selector.query_selector_all("ul li a")

            if i >= len(links):
                break

            a = links[i]
            label = a.get_attribute("aria-label") or ""
            href = a.get_attribute("href") or ""

            print(f"\n➡️ Klik varian #{i+1} → {label}")

            # klik varian
            try:
                a.click()
            except:
                product_page.evaluate("(el)=>el.click()", a)

            product_page.wait_for_timeout(1200)

            # ------------------------------
            # Ambil data dasar dari varian
            # ------------------------------
            try:
                t = product_page.query_selector('h1')
                title = t.inner_text().strip()
            except:
                title = None

            try:
                p = product_page.query_selector('[data-test="current-price"]')
                price = p.inner_text().strip() if p else None
            except:
                price = None

            # -------------------------------------------
            # ✅ Extract Description, Specifications, Label Info
            # -------------------------------------------
            description = extract_description(product_page)
            specifications = extract_specifications(product_page)
            label_info = extract_label_info(product_page)

            variant_data = {
                "variant_label": label,
                "variant_href": href,
                "title": title,
                "price": price,
                "description": description,
                "specifications": specifications,
                "label_info": label_info,
                "url": product_page.url,
                "section": s_idx,
                "index": i + 1
            }

            results.append(variant_data)

            print("✅ Completed varian", i+1)

    print("\n🎉 Selesai klik + ekstrak semua varian termasuk Description, Specs, Label Info.")
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
