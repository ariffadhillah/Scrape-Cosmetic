# # open_target_auto_full_variants.py
# from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# import time
# import re
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ---------- CONFIG ----------
# URL = "https://www.target.com/c/new-in-makeup/-/N-6n69n"
# HEADLESS = False
# PROXY = {
#     "server": "http://dc.decodo.com:10000",
#     "username": "user-spdv8itjmq-country-us",
#     "password": "0uHrpir4~kH9Ipb6Wg"
# }
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

import requests
import time
import json
import random
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------- CONFIG PROXY TERBARU ----------
# Menggunakan daftar proxy yang Anda berikan sebelumnya
PROXIES_LIST = [
    "191.96.254.80:6127:arssrhsq:x1vpi09f4v1g",
    "45.61.122.149:6441:arssrhsq:x1vpi09f4v1g",
    "45.61.124.153:6482:arssrhsq:x1vpi09f4v1g",
    "64.64.110.63:6586:arssrhsq:x1vpi09f4v1g",
    "145.223.58.21:6290:arssrhsq:x1vpi09f4v1g",
    "82.23.206.96:5902:arssrhsq:x1vpi09f4v1g",
    "38.154.233.46:5456:arssrhsq:x1vpi09f4v1g",
    "45.61.118.128:5825:arssrhsq:x1vpi09f4v1g",
    "191.96.202.229:6275:arssrhsq:x1vpi09f4v1g",
    "23.27.196.145:6514:arssrhsq:x1vpi09f4v1g",
    "154.6.126.37:6008:arssrhsq:x1vpi09f4v1g",
    "89.249.195.211:6966:arssrhsq:x1vpi09f4v1g",
    "147.124.198.69:5928:arssrhsq:x1vpi09f4v1g",
    "82.24.238.65:6872:arssrhsq:x1vpi09f4v1g",
    "38.154.217.34:7225:arssrhsq:x1vpi09f4v1g",
    "174.140.200.142:6422:arssrhsq:x1vpi09f4v1g",
    "46.202.224.238:5790:arssrhsq:x1vpi09f4v1g",
    "31.57.87.145:5830:arssrhsq:x1vpi09f4v1g",
    "38.154.233.181:5591:arssrhsq:x1vpi09f4v1g",
    "198.46.241.143:6678:arssrhsq:x1vpi09f4v1g",
    "23.27.203.134:6869:arssrhsq:x1vpi09f4v1g",
    "104.168.118.219:6175:arssrhsq:x1vpi09f4v1g",
    "152.232.14.43:7174:arssrhsq:x1vpi09f4v1g",
    "82.26.238.68:6375:arssrhsq:x1vpi09f4v1g",
    "89.249.194.231:6630:arssrhsq:x1vpi09f4v1g",
    "104.232.211.0:5613:arssrhsq:x1vpi09f4v1g",
    "38.154.217.123:7314:arssrhsq:x1vpi09f4v1g",
    "67.227.14.204:6796:arssrhsq:x1vpi09f4v1g"
]

def get_random_proxy_config():
    """Mengambil proxy acak dan memformatnya untuk Playwright."""
    proxy_str = random.choice(PROXIES_LIST)
    ip, port, user, pw = proxy_str.split(':')
    return {
        "server": f"http://{ip}:{port}",
        "username": user,
        "password": pw
    }

# ---------- TARGET CONFIG ----------
URL = "https://www.target.com/c/frozen-foods-grocery/-/N-5xszd"
HEADLESS = False
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

ACCEPT_LANGS = "en-US,en;q=0.9"
NAV_TIMEOUT_MS = 90000
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

def extract_specifications(product_page):
    """
    Menggunakan Playwright Page (product_page).
    - Buka accordion "Specifications" bila perlu
    - Ambil semua baris di data-test="item-details-specifications"
    - Kembalikan dict yang berisi keys yang kita inginkan (bisa None)
    """
    specs_data = {}

    try:
        # 1) cari tombol accordion Specifications (beberapa halaman pakai href selector)
        btn = product_page.query_selector('button[href="#Specifications-accordion-scroll-id"]') \
              or product_page.query_selector('button:has-text("Specifications")') \
              or product_page.query_selector('button:has(h3:text("Specifications"))')

        if btn:
            try:
                aria = btn.get_attribute("aria-expanded")
            except:
                aria = None
            if aria is not None and aria.lower() == "false":
                try:
                    btn.click()
                except:
                    # fallback ke JS click
                    try:
                        product_page.evaluate("(el) => el.click()", btn)
                    except:
                        pass
                # beri waktu animasi / render konten
                product_page.wait_for_timeout(800)
        else:
            # jika tombol tidak ditemukan, mungkin accordion sudah inline / terbuka
            pass

        # 2) ambil container specs
        specs_div = product_page.query_selector('div[data-test="item-details-specifications"]')
        if not specs_div:
            # kadang ada wrapper lain; coba query yang lebih luas
            specs_div = product_page.query_selector('[data-test="item-details-specifications"], div[itemprop="specification"], div:has-text("TCIN")')

        if not specs_div:
            # tidak ada specifications
            return {
                "Suggested Age": None,
                "Health Facts": None,
                "Color Finish": None,
                "Color Palette": None,
                "Product Form": None,
                "Sustainability Claims": None,
                "Beauty Purpose": None,
                "Net weight": None,
                "Features": None,
                "TCIN": None,
                "UPC": None,
                "Item Number (DPCI)": None,
                "Origin": None,
            }

        # 3) ambil semua blok <div> di dalamnya yang terlihat seperti "Key: Value"
        # gunakan query yang cukup fleksibel: cari semua direct children yang berisi <b> atau ":" text
        rows = specs_div.query_selector_all("div > div") or specs_div.query_selector_all("div")

        # iterasi rows, cari <b> jika ada, kalau tidak coba split by ":" pada inner_text
        for row in rows:
            try:
                b = row.query_selector("b")
                if b:
                    key = b.inner_text().strip().rstrip(":")
                    # value: ambil seluruh text row lalu hapus bagian <b>
                    text = row.inner_text().strip()
                    # split on first ":" to be safer
                    parts = text.split(":", 1)
                    if len(parts) > 1:
                        value = parts[1].strip()
                    else:
                        # jika nextSibling ada, coba dapatkan
                        try:
                            ns = product_page.evaluate("(el) => (el.querySelector('b') && el.querySelector('b').nextSibling) ? el.querySelector('b').nextSibling.textContent : ''", row)
                            value = (ns or "").strip()
                        except:
                            value = ""
                    if key:
                        specs_data[key] = value
                else:
                    # fallback: parse "Key: Value" dari plain text
                    txt = row.inner_text().strip()
                    if ":" in txt:
                        k, v = [s.strip() for s in txt.split(":", 1)]
                        if k:
                            specs_data[k] = v
            except Exception:
                continue

        # 4) normalisasi / ambil keys penting (jika tidak ada -> None)
        cleaned = {
            "Suggested Age": specs_data.get("Suggested Age") or specs_data.get("Suggested age") or specs_data.get("SuggestedAge"),
            "Health Facts": specs_data.get("Health Facts") or specs_data.get("Health facts"),
            "Color Finish": specs_data.get("Color Finish") or specs_data.get("Color finish"),
            "Color Palette": specs_data.get("Color Palette") or specs_data.get("Color palette"),
            "Product Form": specs_data.get("Product Form") or specs_data.get("Product form"),
            "Sustainability Claims": specs_data.get("Sustainability Claims") or specs_data.get("Sustainability claims"),
            "Beauty Purpose": specs_data.get("Beauty Purpose") or specs_data.get("Beauty purpose"),
            "Net weight": specs_data.get("Net weight") or specs_data.get("Net Weight") or specs_data.get("Net weight (oz)"),
            "Features": specs_data.get("Features"),
            "TCIN": specs_data.get("TCIN") or specs_data.get("Tcin"),
            "UPC": specs_data.get("UPC"),
            "Item Number (DPCI)": specs_data.get("Item Number (DPCI)") or specs_data.get("Item Number (DPCI)"),
            "Origin": specs_data.get("Origin"),
        }

        return cleaned

    except Exception as e:
        print("❌ Error reading specs:", e)
        # fallback: kembalikan keys kosong agar caller tidak crash
        return {
            "Suggested Age": None,
            "Health Facts": None,
            "Color Finish": None,
            "Color Palette": None,
            "Product Form": None,
            "Sustainability Claims": None,
            "Beauty Purpose": None,
            "Net weight": None,
            "Features": None,
            "TCIN": None,
            "UPC": None,
            "Item Number (DPCI)": None,
            "Origin": None,
        }

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


def click_and_extract_Label_info(product_page):
    """
    Klik accordion Label info dan ambil Ingredients atau Nutrition facts.
    SUPER STABIL: dengan fallback multi-selector.
    """

    print("🟦 Mencari accordion 'Label info'...")

    # Cari tombol Label info (varian layout baru)
    label_btn = product_page.query_selector(
        '[data-test="@web/site-top-of-funnel/ProductDetailCollapsible-LabelInfo"] button'
    )

    if not label_btn:
        # fallback alternatif
        label_btn = product_page.query_selector('button:has-text("Label info")')

    if not label_btn:
        print("   ⚠️ Accordion Label info tidak ditemukan.")
        return {"ingredients": None}

    # Klik jika belum terbuka
    aria = label_btn.get_attribute("aria-expanded")
    if aria == "false":
        print("➡️ Membuka accordion Label info...")
        try:
            label_btn.click()
        except:
            product_page.evaluate("(el)=>el.click()", label_btn)
        product_page.wait_for_timeout(600)

    # ================================
    # ✅ Mencari blok Ingredients
    # ================================

    selectors = [
        'div:has(h4:has-text("Ingredients"))',
        'div[data-test="ingredients"]',
        'div:has-text("Ingredients")'
    ]

    ing_block = None

    for sel in selectors:
        try:
            ing_block = product_page.query_selector(sel)
            if ing_block:
                break
        except:
            pass

    if not ing_block:
        print("   ⚠️ Ingredients block tidak ditemukan.")
        return {"ingredients": None}

    # Ambil text ingredients
    try:
        ing_text = ing_block.inner_text().strip()
    except:
        ing_text = ""

    # Cleanup
    if ing_text.lower().startswith("ingredients:"):
        ing_text = ing_text[len("ingredients:"):].strip()

    # Final check
    if len(ing_text) < 5:
        print("   ⚠️ Ingredients kosong atau tidak valid.")
        return {"ingredients": None}

    print("   ✅ Ingredients ditemukan!")

    return {"ingredients": ing_text}



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

            # ✅ Tambahkan DETAIL dari accordion
            details = click_and_extract_details(product_page)

            label_info = click_and_extract_Label_info(product_page)
            ingredients = label_info.get("ingredients", None)

            specs = extract_specifications(product_page)
            variant_info["specifications"] = specs


            results.append(variant_info)

            # print summary for this variant
            print("   → title:", title)
            print("   → price:", price)
            print("   → availability:", availability)
            print("   → image:", image_url)
            print("   → sku:", sku)
            print("   → description:", (details['description'][:60] + "...") if details["description"] else None)
            print("   → Ingredients:", ingredients["Ingredients"])
            print("      Suggested Age =", specs.get("Suggested Age"))
            print("      Health Facts =", specs.get("Health Facts"))            
            print("      TCIN =", specs.get("TCIN"))
            print("      UPC =", specs.get("UPC"))
            print("      Item Number (DPCI) =", specs.get("Item Number (DPCI)"))
            print("      Origin =", specs.get("Origin"))
            # print("Ingredients:", label_info["Ingredients"])



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
            title_el = item.query_selector('a[data-test="@web/ProductCard/title"]') or item.query_selector('a[data-test="@web/ProductCard/ProductCardLink"]')
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
    print("🚀 Starting Playwright dengan Rotasi Proxy Terbaru...")
    
    with sync_playwright() as p:
        # Ambil konfigurasi proxy secara acak
        proxy_config = get_random_proxy_config()
        print(f"📡 Menggunakan Proxy: {proxy_config['server']}")

        browser = p.chromium.launch(
            headless=HEADLESS, 
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"], 
            proxy=proxy_config
        )
        
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US",
            viewport={"width": 1366, "height": 900},
        )
        
        # Inject script untuk menyembunyikan bot
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = context.new_page()

        try:
            print(f"🌐 Navigating to {URL} ...")
            # Gunakan timeout yang cukup lama karena proxy terkadang lambat
            page.goto(URL, wait_until="domcontentloaded", timeout=90000)
            
            # Jalankan logika scraping Anda
            go_through_pagination(page, context)

        except PlaywrightTimeoutError:
            print("⚠️ Timeout: Koneksi proxy lambat, mencoba melanjutkan...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("\n✅ Proses selesai.")
            # Biarkan browser terbuka untuk inspeksi jika tidak headless
            if not HEADLESS:
                time.sleep(100) 
            browser.close()

if __name__ == "__main__":
    main()