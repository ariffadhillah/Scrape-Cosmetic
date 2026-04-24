# open_target_auto.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
from datetime import datetime
from pathlib import Path

# ---------- CONFIG ----------
URL = "https://www.target.com/c/new-in-makeup/-/N-6n69n"
HEADLESS = False  # False agar kamu bisa lihat browser
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

def auto_scroll_to_bottom(page, step=1000, max_wait=40):
    print("\n🌀 Scrolling ke bawah untuk memuat semua produk...")
    last_height = 0
    same_height_count = 0
    start_time = time.time()

    while True:
        page.evaluate(f"window.scrollBy(0, {step});")
        time.sleep(1.5)  # beri waktu JS load item baru
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

# def extract_variants(page):
#     print("🎨 Mencari varian produk...")

#     try:
#         selector = page.query_selector('div[data-module-type="ProductDetailVariationSelector"]')
#         if not selector:
#             print("❌ Tidak menemukan ProductDetailVariationSelector.")
#             return []

#         # Cari semua <a> dalam carousel
#         links = selector.query_selector_all("ul li a")
#         variants = []

#         for a in links:
#             href = a.get_attribute("href")
#             aria = a.get_attribute("aria-label") or ""
#             selected = "selected" in aria.lower()
#             text = aria.replace("Color, ", "").split(",")[0].strip()

#             # pastikan URL lengkap
#             if href and not href.startswith("http"):
#                 href = f"https://www.target.com{href}"

#             variants.append({
#                 "name": text,
#                 "href": href,
#                 "selected": selected
#             })

#         print(f"✅ Ditemukan {len(variants)} varian.")
#         return variants

#     except Exception as e:
#         print("⚠️ Error membaca varian:", e)
#         return []


# def click_all_variants(page):
#     print("\n🔍 Mencari Variation Selector...")

#     selectors = page.query_selector_all(
#         'div[data-module-type="ProductDetailVariationSelector"]'
#     )

#     if not selectors:
#         print("❌ Tidak ada Variation Selector.")
#         return

#     print(f"✅ Menemukan {len(selectors)} variation section")

#     for idx, selector in enumerate(selectors, start=1):
#         print(f"\n--- Variation Section #{idx} ---")

#         links = selector.query_selector_all("ul li a")

#         if not links:
#             print("⚠️ Section ini tidak punya varian (skip).")
#             continue

#         print(f"✅ Menemukan {len(links)} varian.")

#         for i, a in enumerate(links, start=1):
#             href = a.get_attribute("href")
#             label = a.get_attribute("aria-label")

#             print(f"➡️ Klik varian #{i} → {label} ({href})")

#             try:
#                 a.click()
#                 page.wait_for_load_state("networkidle")
#                 page.wait_for_timeout(1500)

#                 print("   ✅ Berhasil klik varian")

#             except Exception as e:
#                 print(f"   ❌ Gagal klik varian: {e}")
#                 continue


def click_all_variants(page):
    if not page:
        print("❌ Tidak bisa klik varian karena halaman produk gagal dibuka.")
        return

    print("\n🎨 Mencari Variation Selector...")

    selectors = page.query_selector_all('div[data-module-type="ProductDetailVariationSelector"]')

    if not selectors:
        print("❌ Tidak ada Variation Selector di halaman ini.")
        return

    print(f"✅ Menemukan {len(selectors)} section varian")

    for idx, selector in enumerate(selectors, start=1):
        print(f"\n--- Variation Section #{idx} ---")

        links = selector.query_selector_all("ul li a")
        if not links:
            print("⚠️ Tidak ada pilihan varian pada section ini.")
            continue

        print(f"✅ {len(links)} varian ditemukan")

        for i, a in enumerate(links, start=1):
            label = a.get_attribute("aria-label")
            href = a.get_attribute("href")

            print(f"➡️ Klik varian #{i}: {label}")

            try:
                a.click()
                page.wait_for_timeout(1500)
                print("   ✅ Varian diklik")

            except Exception as e:
                print(f"   ❌ Gagal klik varian: {e}")


def inspect_product_cards(page):
    print("\n🔍 Mencari daftar produk...")
    try:
        container = page.query_selector('div[data-module-type="ListingPageProductListCards"]')
        if not container:
            print("❌ Tidak menemukan container 'ListingPageProductListCards'.")
            return
        
        items = container.query_selector_all('div[data-test="@web/ProductCard/ProductCardVariantDefault"]')
        print(f"✅ Ditemukan {len(items)} produk.\n")

        for i, item in enumerate(items, start=1):
            try:
                # Cari elemen <a data-test="product-title"> (versi baru)
                title = item.query_selector('a[data-test="product-title"]')
                if not title:
                    # fallback ke versi lama jika masih ada
                    title = item.query_selector('a[data-test="@web/ProductCard/ProductCardLink"]')

                name = title.inner_text().strip() if title else "(no title)"
                href = title.get_attribute("href") if title else None

                # Ambil harga
                price = item.query_selector('[data-test="current-price"]')
                price_text = price.inner_text().strip() if price else "(no price)"

                print(f"{i}. {name} | {price_text}")

                if href:
                    full_url = f"https://www.target.com{href}"

                    # product_page = open_product_page(page.context, full_url)

                    # click_all_variants(product_page)
                    # product_page.close()


                    # if product_page:
                    #     variant_info = click_and_extract_variants(product_page)
                    #     product_page.close()


                    product_page = open_product_page(page.context, full_url)

                    if product_page:
                        click_all_variants(product_page)
                        product_page.close()
                    else:
                        print("❌ Skip varian karena halaman produk gagal dibuka")



            except Exception as e:
                print(f"   ⚠️ Gagal membaca item {i}: {e}")

    except Exception as e:
        print("Error saat mencari produk:", e)

# def open_product_page(context, full_url):
#     print(f"\n🔍 Membuka halaman produk: {full_url}")
#     new_page = context.new_page()
#     try:
#         new_page.goto(full_url, timeout=60000, wait_until="networkidle")
#         new_page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
#         new_page.wait_for_timeout(3000)
        
#         print("✅ Halaman produk terbuka.")
#         return new_page   # <--- ini perubahan penting
#     except Exception as e:
#         print(f"   ⚠️ Gagal membuka halaman produk: {e}")
#         return None
#     finally:
#         new_page.close()


# def open_product_page(context, full_url):
#     print(f"\n🔍 Membuka halaman produk: {full_url}")
#     new_page = context.new_page()
#     try:
#         new_page.goto(full_url, timeout=60000, wait_until="networkidle")
#         new_page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
#         new_page.wait_for_timeout(3000)
        
#         print("✅ Halaman produk terbuka.")
#         return new_page

#     except Exception as e:
#         print(f"   ⚠️ Gagal membuka halaman produk: {e}")
#         new_page.close()
#         return None

def open_product_page(context, full_url):
    print(f"\n🔍 Membuka halaman produk: {full_url}")
    new_page = context.new_page()
    
    try:
        # Gunakan "domcontentloaded" agar tidak timeout
        new_page.goto(full_url, timeout=60000, wait_until="domcontentloaded")

        # scroll sedikit untuk memuat elemen lazy-load
        new_page.wait_for_timeout(1000)
        new_page.evaluate("window.scrollBy(0, 300)")
        new_page.wait_for_timeout(1500)

        print("✅ Halaman produk terbuka.")
        return new_page

    except Exception as e:
        print(f"   ❌ ERROR: gagal membuka halaman produk\n       → {e}")
        try:
            new_page.close()
        except:
            pass
        return None


def go_through_pagination(page):
    """Klik tombol next terus sampai tidak ada halaman berikutnya."""
    page_num = 1
    while True:
        print(f"\n📄 Sedang di halaman {page_num}")
        auto_scroll_to_bottom(page)
        inspect_product_cards(page)
        

        # Coba cari tombol next
        next_button = page.query_selector('button[data-test="next"]')
        if not next_button:
            print("❌ Tombol next tidak ditemukan. Selesai.")
            break

        # Periksa apakah tombolnya disabled
        disabled = next_button.get_attribute("disabled")
        if disabled is not None:
            print("✅ Sudah di halaman terakhir.")
            break

        try:
            print("➡️ Klik tombol next...")
            next_button.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)  # beri waktu JS render produk baru
            page_num += 1
        except Exception as e:
            print(f"⚠️ Gagal klik next: {e}")
            break


def main():
    print("🚀 Starting Playwright (headful)...")
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
            print(f"🌐 Navigating to {URL} ...")
            page.goto(URL, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            print("⚠️ Timeout: halaman masih loading tapi akan dilanjutkan.")
        except Exception as e:
            print("Navigation error:", e)
            browser.close()
            return

        # otomatis scroll ke bawah
        auto_scroll_to_bottom(page)

        # # tampilkan hasil produk
        # inspect_product_cards(page)
        go_through_pagination(page)

        print("\n✅ Selesai. Browser dibiarkan terbuka untuk inspeksi manual.")
        print("Tutup browser secara manual jika sudah selesai.")
        # biarkan browser tetap terbuka agar kamu bisa lihat
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nMenutup browser...")
            browser.close()

if __name__ == "__main__":
    main()
