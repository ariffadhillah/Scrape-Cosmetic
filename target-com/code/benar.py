# open_target_auto_full_variants_full.py
"""
Full, modular, sync-playwright script for Target product pages.
Features:
- Keeps your existing sync_playwright style (no async changes)
- Modular "accordion" reader (open_and_extract_accordion)
- Solid waiting for content (Description, Specifications, Label Info / Ingredients)
- Clicks each variant, extracts title/price/image/sku, then reads Description/Specs/Label Info
- Ensures all extraction for each variant completes before moving to next variant or next product
- Defensive selectors with fallbacks

Requirements:
- playwright python installed and browsers: `pip install playwright` then `playwright install`

Usage:
    python open_target_auto_full_variants_full.py

Adapt the CONFIG section to your proxy, headless, URL, timeouts, etc.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import re

# ----------------- CONFIG -----------------
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
DEFAULT_WAIT_MS = 1200
# ------------------------------------------

INJECT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
"""

# ----------- Helper utilities --------------

def safe_inner_text(el):
    try:
        return el.inner_text().strip() if el else None
    except:
        return None


def wait_for_visible_text(page, selector, timeout=8000, poll=300):
    """
    Wait until selector exists and has non-empty inner_text.
    Returns the text or None on timeout.
    """
    waited = 0
    while waited < timeout:
        try:
            el = page.query_selector(selector)
            if el:
                txt = safe_inner_text(el)
                if txt and len(txt) > 0:
                    return txt
        except:
            pass
        page.wait_for_timeout(poll)
        waited += poll
    return None


def open_and_ensure(page, button_selector, content_wait_selector=None, open_timeout=8000):
    """
    Generic: find accordion button (button_selector), click to open if closed
    then optionally wait for content selector to have text.

    Returns boolean (True if content visible / ready, False otherwise).
    """
    try:
        btn = page.query_selector(button_selector)
        if not btn:
            return False

        # check aria state and click if collapsed
        try:
            aria = btn.get_attribute("aria-expanded")
        except:
            aria = None

        if aria is None or aria.lower() != "true":
            try:
                btn.click()
            except:
                try:
                    page.evaluate("(el) => el.click()", btn)
                except:
                    pass
            # small pause for animation
            page.wait_for_timeout(350)

        # if caller wants content to be present, wait
        if content_wait_selector:
            # use wait_for_visible_text to ensure non-empty text
            txt = wait_for_visible_text(page, content_wait_selector, timeout=open_timeout)
            return True if txt else False

        return True
    except Exception as e:
        print("   ⚠️ open_and_ensure error:", e)
        return False


# ---------- Specific extractors -------------

def extract_description(page):
    """
    Opens Details accordion if needed and extracts Highlights (list) + Description text.
    Returns dict {"highlights": [], "description": str}
    """
    print("   🔎 extract_description")

    # robust button selectors
    btn_selectors = [
        'button:has(h3:text("Details"))',
        'button:has-text("Details")',
        '[data-test="ProductDetailCollapsible-ProductDetailsAndHighlights"] button',
        'button[href="#ProductDetailsAndHighlights-accordion-scroll-id"]'
    ]

    btn = None
    for sel in btn_selectors:
        try:
            el = page.query_selector(sel)
            if el:
                btn = el
                break
        except:
            continue

    if not btn:
        print("      ⚠️ Details accordion button not found")
        # still try to read description directly
    else:
        try:
            aria = btn.get_attribute("aria-expanded")
        except:
            aria = None
        if aria is None or aria.lower() != "true":
            try:
                btn.click()
            except:
                try:
                    page.evaluate("(el)=>el.click()", btn)
                except:
                    pass
            page.wait_for_timeout(450)

    # Highlights
    highlights = []
    try:
        li_sel = '[data-test="@web/ProductDetailPageHighlights"] li'
        lis = page.query_selector_all(li_sel)
        for li in lis:
            txt = safe_inner_text(li)
            if txt:
                highlights.append(txt)
    except:
        pass

    # Description
    desc = wait_for_visible_text(page, '[data-test="item-details-description"]', timeout=6000)

    if desc:
        print("      ✅ description found (len={} chars)".format(len(desc)))
    else:
        print("      ⚠️ description not found")

    return {"highlights": highlights, "description": desc}


def extract_specifications(page):
    """
    Opens Specifications accordion and extracts key:value list.
    Returns dict of keys -> values (strings) and a 'raw' list fallback.
    """
    print("   🔎 extract_specifications")

    # Try to open accordion
    opened = open_and_ensure(page,
                             'button:has(h3:text("Specifications"))',
                             content_wait_selector='[data-test="item-details-specifications"]',
                             open_timeout=6000)

    if not opened:
        # some pages have it open by default, still try to find content
        pass

    specs = {}
    raw = []
    try:
        # The structure often: div[data-test="item-details-specifications"] > div > div
        container = page.query_selector('[data-test="item-details-specifications"]')
        if not container:
            # fallback broader search
            container = page.query_selector('div:has-text("TCIN")')

        if container:
            # iterate child divs that contain <b>Key</b> or text 'Key: Value'
            blocks = container.query_selector_all('div')
            for b in blocks:
                try:
                    text = safe_inner_text(b)
                    if not text:
                        continue
                    # some blocks are separators
                    if ':' in text:
                        raw.append(text)
                        # If starts with 'TCIN' or 'UPC' they may be like 'TCIN: 123'
                        parts = text.split(':', 1)
                        key = parts[0].strip().rstrip(':')
                        val = parts[1].strip() if len(parts) > 1 else ''
                        if key:
                            specs[key] = val
                    else:
                        # if it's a single word (e.g. 'Features' next block) skip
                        continue
                except:
                    continue

    except Exception as e:
        print("      ⚠️ specs extraction error:", e)

    print(f"      → specs found: {len(specs)} keys, raw lines: {len(raw)}")
    return {"specs": specs, "raw": raw}


def extract_label_info(page):
    """
    Opens Label info and reads Ingredients or Nutrition text.
    Returns string or None.
    """
    print("   🔎 extract_label_info")

    # open accordion using a few selectors
    opened = open_and_ensure(page,
                             '[data-test="@web/site-top-of-funnel/ProductDetailCollapsible-LabelInfo"] button',
                             content_wait_selector='[data-test="productDetailTabs-nutritionFactsTab"]',
                             open_timeout=8000)

    # If open_and_ensure returned False, still attempt other selectors
    if not opened:
        # try by visible heading
        try:
            btn_alt = page.query_selector('button:has(h3:text("Label info"))') or page.query_selector('button:has-text("Label info")')
            if btn_alt:
                try:
                    btn_alt.click()
                except:
                    try:
                        page.evaluate("(el)=>el.click()", btn_alt)
                    except:
                        pass
                page.wait_for_timeout(500)
        except:
            pass

    # Now try to find ingredients area
    candidates = [
        '[data-test="productDetailTabs-nutritionFactsTab"]',
        'div:has(h4:has-text("Ingredients"))',
        'div.h-text-transform-caps',
        'div:has-text("Ingredients:")'
    ]

    ing_text = None
    for sel in candidates:
        try:
            txt = wait_for_visible_text(page, sel, timeout=3000)
            if txt:
                # if the selector is a container, we may want only the ingredient paragraph
                if 'Ingredients' in txt and len(txt) < 40:
                    # maybe the header only; try sibling
                    el = page.query_selector(sel)
                    if el:
                        # find a deeper descendant with long text
                        deep = el.query_selector('div, p, span')
                        if deep:
                            maybe = safe_inner_text(deep)
                            if maybe and len(maybe) > 20:
                                ing_text = maybe
                                break
                else:
                    ing_text = txt
                    break
        except:
            continue

    if ing_text:
        # cleanup leading 'Ingredients:'
        if ing_text.lower().startswith('ingredients:'):
            ing_text = ing_text[len('ingredients:'):].strip()
        print("      ✅ label info (ingredients) found")
    else:
        print("      ⚠️ label info not found")

    return ing_text


# -------- Core variant click / extract loop ----------

def click_and_extract_variants(product_page):
    results = []

    print("\n🎨 Mencari variation selector di page produk...")
    selectors = product_page.query_selector_all('div[data-module-type="ProductDetailVariationSelector"]')

    if not selectors:
        print("⚠️ Tidak menemukan ProductDetailVariationSelector di halaman ini.")
        return results

    print(f"✅ Ditemukan {len(selectors)} variation section(s).")

    for s_idx, selector in enumerate(selectors, start=1):
        print(f"\n--- Section #{s_idx} ---")

        # collect links initially
        links = selector.query_selector_all('ul li a')
        if not links:
            print("⚠️ Section ini tidak memiliki ul>li>a (skip).")
            continue

        count_links = len(links)
        print(f"✅ {count_links} varian ditemukan — mulai proses satu-per-satu...")

        # iterate by index, re-query each time
        for i in range(count_links):
            # re-query to avoid stale handles
            selector = product_page.query_selector_all('div[data-module-type="ProductDetailVariationSelector"]')[s_idx-1]
            links = selector.query_selector_all('ul li a')
            if i >= len(links):
                print("   ⚠️ Index out of range after requery — breaking")
                break

            a = links[i]
            label = a.get_attribute('aria-label') or safe_inner_text(a) or ''
            href = a.get_attribute('href') or ''

            print(f"\n➡️ Klik varian #{i+1} → {label}")

            # click and wait for UI update
            try:
                a.click()
            except:
                try:
                    product_page.evaluate('(el)=>el.click()', a)
                except:
                    pass

            # wait small time so page details update in-place
            product_page.wait_for_timeout(DEFAULT_WAIT_MS)

            # basic fields
            title = None
            price = None
            availability = None
            image_url = None
            sku = None

            try:
                t = product_page.query_selector('h1') or product_page.query_selector('[data-test="product-title"]')
                title = safe_inner_text(t)
            except:
                title = None

            try:
                p = product_page.query_selector('[data-test="current-price"]') or product_page.query_selector('[data-test="product-price"]')
                price = safe_inner_text(p)
            except:
                price = None

            try:
                sold = product_page.query_selector('text=Out of stock') or product_page.query_selector('text=Out of Stock')
                if sold:
                    availability = 'Out of stock'
                else:
                    add_btn = product_page.query_selector('button[data-test="add-to-cart-button"]') or product_page.query_selector('button[aria-label*="Add to cart"]')
                    if add_btn:
                        disabled = add_btn.get_attribute('disabled')
                        if disabled is not None:
                            availability = 'Out of stock'
                        else:
                            availability = safe_inner_text(add_btn) or 'Available'
                    else:
                        availability = 'Unknown'
            except:
                availability = 'Unknown'

            try:
                img = product_page.query_selector('img[data-test="image-gallery-item-0"]') or product_page.query_selector('img[src*="target.scene7.com"]')
                if img:
                    image_url = img.get_attribute('src') or img.get_attribute('data-src')
            except:
                image_url = None

            # try sku/TCIN
            try:
                m = product_page.query_selector('meta[itemprop="sku"]') or product_page.query_selector('meta[name="sku"]')
                if m:
                    sku = m.get_attribute('content')
            except:
                sku = None

            if not sku:
                try:
                    # try reading TCIN block
                    tcin_el = product_page.query_selector('div:has-text("TCIN")')
                    if tcin_el:
                        txt = safe_inner_text(tcin_el)
                        if txt:
                            # normalize
                            sku = re.search(r'(TCIN[:]?\s*\d+)', txt)
                            if sku:
                                sku = sku.group(1)
                            else:
                                sku = txt.strip()
                except:
                    sku = sku

            # ------------------
            # Extract deep sections
            # ------------------
            desc_obj = extract_description(product_page)
            specs_obj = extract_specifications(product_page)
            label_obj = extract_label_info(product_page)

            variant_data = {
                'section_index': s_idx,
                'variant_index': i+1,
                'variant_label': label,
                'variant_href': href,
                'title': title,
                'price': price,
                'availability': availability,
                'image': image_url,
                'sku': sku,
                'description': desc_obj,
                'specifications': specs_obj,
                'label_info': label_obj,
                'product_page_url': product_page.url
            }

            results.append(variant_data)

            # print diagnostic summary
            print("   → title:", title)
            print("   → price:", price)
            print("   → availability:", availability)
            print("   → image:", image_url)
            print("   → sku:", sku)
            print("   → description (len):", (len(desc_obj['description']) if desc_obj['description'] else 0))
            print("   → specs keys:", list(specs_obj['specs'].keys())[:6])
            print("   → ingredients present:", bool(label_obj))

            # ensure we don't start next product until this variant done (we already don't, because loop is synchronous)
            # small throttle to be kind
            product_page.wait_for_timeout(250)

    print("\n🎉 Finished variants for this product page.")
    return results


# --------- Listing / pagination / orchestration ---------

def inspect_product_cards(page, context):
    """Scan listing page, open each product, extract per-variant data."""
    print("\n🔍 inspect_product_cards")

    container = page.query_selector('div[data-module-type="ListingPageProductListCards"]')
    if not container:
        print("   ⚠️ Listing container not found")
        return

    items = container.query_selector_all('div[data-test="@web/ProductCard/ProductCardVariantDefault"]')
    print(f"   ✅ Found {len(items)} items on current listing page.")

    for idx, item in enumerate(items, start=1):
        try:
            title_el = item.query_selector('a[data-test="product-title"]') or item.query_selector('a[data-test="@web/ProductCard/ProductCardLink"]')
            name = safe_inner_text(title_el) or '(no title)'
            href = title_el.get_attribute('href') if title_el else None
            price_el = item.query_selector('[data-test="current-price"]') or item.query_selector('[data-test="product-price"]')
            price_text = safe_inner_text(price_el) or '(no price)'

            print(f"\n{idx}. {name} | {price_text}")

            if not href:
                print("   ⚠️ no href for this product — skip")
                continue

            full_url = f"https://www.target.com{href}" if href.startswith('/') else href

            # open product in new tab (page) and do variant extraction
            product_page = context.new_page()
            try:
                product_page.goto(full_url, timeout=NAV_TIMEOUT_MS, wait_until='domcontentloaded')
                product_page.wait_for_timeout(900)
                product_page.evaluate('window.scrollBy(0,300)')
                product_page.wait_for_timeout(900)

                print("   ✅ Product page opened")
                variant_results = click_and_extract_variants(product_page)

                # summary printing
                for vr in variant_results:
                    print(f"    • [{vr['variant_index']}] {vr['variant_label']} | {vr['price']} | {vr['availability']}")

            except Exception as e:
                print("   ❌ failed to open product page:", e)
            finally:
                try:
                    product_page.close()
                except:
                    pass

        except Exception as e:
            print("   ⚠️ Error reading listing item:", e)


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


def go_through_pagination(page, context, max_pages=None):
    page_num = 1
    while True:
        print(f"\n📄 On listing page {page_num}")

        # wait for product cards
        try:
            page.wait_for_selector('div[data-module-type="ListingPageProductListCards"]', timeout=15000)
            page.wait_for_selector('div[data-test="@web/ProductCard/ProductCardVariantDefault"]', timeout=15000)
        except:
            print("   ⚠️ listing product cards didn't appear in time")

        auto_scroll_to_bottom(page)
        inspect_product_cards(page, context)

        if max_pages and page_num >= max_pages:
            print('   🔒 reached max_pages -> stop')
            break

        # next button
        try:
            next_btn = page.query_selector('button[data-test="next"]')
            if not next_btn:
                print('   ✅ next button not found -> finished')
                break
            if next_btn.get_attribute('disabled') is not None:
                print('   ✅ already last page')
                break
            print('   ➡️ clicking next...')
            next_btn.click()
            page.wait_for_timeout(1800)
            page_num += 1
        except Exception as e:
            print('   ⚠️ error clicking next:', e)
            break


# -------------------- MAIN --------------------

def main():
    print('🚀 starting playwright (sync)')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, args=['--no-sandbox'], proxy=PROXY)
        context = browser.new_context(user_agent=USER_AGENT, locale='en-US', viewport={'width':1366,'height':900}, timezone_id='America/New_York')
        context.add_init_script(INJECT_SCRIPT)

        page = context.new_page()
        page.set_extra_http_headers({'Accept-Language': ACCEPT_LANGS})

        try:
            print(f"🌐 navigating to {URL} ...")
            page.goto(URL, wait_until='domcontentloaded', timeout=NAV_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            print('   ⚠️ nav timeout, continuing')
        except Exception as e:
            print('   ❌ nav error:', e)
            try:
                browser.close()
            except:
                pass
            return

        # run the pagination/inspection
        go_through_pagination(page, context)

        print('\n✅ All done — browser kept open for inspection (close manually or ctrl+c)')
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            print('\nclosing browser...')
            browser.close()


if __name__ == '__main__':
    main()
