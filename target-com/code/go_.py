# open_target_auto_full_variants_full.py
"""
Full integrated script (sync-playwright) for Target product pages.
- Clicks each variant, extracts title/price/image/sku
- Extracts Description (highlights + description text)
- Extracts Specifications, parses into individual variables (safe names)
- Extracts Label info (Ingredients)
- Ensures full extraction for each variant before moving on
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import re
import csv
import os

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

# ---------------- Utility ------------------

def safe_inner_text(el):
    try:
        return el.inner_text().strip() if el else None
    except:
        return None

def to_safe_key(s):
    """Convert a human key to safe python dict key"""
    if not s:
        return s
    k = s.lower().strip()
    # common replacements
    k = k.replace("/", "_").replace("\\", "_")
    k = k.replace("(", "").replace(")", "")
    k = k.replace(".", "")
    k = k.replace("%", "pct")
    k = re.sub(r'[^a-z0-9_ ]', '', k)
    k = k.replace(" ", "_")
    k = re.sub(r'__+', '_', k)
    k = k.strip("_")
    return k

def wait_for_visible_text(page, selector, timeout=8000, poll=300):
    """Wait until selector exists and has non-empty inner_text. Return text or None."""
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
    Find and click accordion button if collapsed, then optionally wait for content selector.
    Returns True when content present (or button was found & clicked). False on failure.
    """
    try:
        btn = page.query_selector(button_selector)
        if not btn:
            return False
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
            page.wait_for_timeout(350)
        if content_wait_selector:
            txt = wait_for_visible_text(page, content_wait_selector, timeout=open_timeout)
            return True if txt else False
        return True
    except Exception as e:
        print("   ⚠️ open_and_ensure error:", e)
        return False

# --------- Extractors ----------

def extract_description(page):
    """
    Opens Details accordion if needed and extracts:
    - highlights: list of strings
    - description: string
    """
    print("   🔎 extract_description")
    # try robust selectors for button
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
    if btn:
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

    # highlights
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

    desc = wait_for_visible_text(page, '[data-test="item-details-description"]', timeout=6000)
    if desc:
        print(f"      ✅ description found (len={len(desc)} chars)")
    else:
        print("      ⚠️ description not found")
    return {"highlights": highlights, "description": desc}

def extract_specifications(page):
    """
    Opens Specifications accordion and returns:
    {
      "specs": {key: value, ...},   # parsed key/value
      "raw": [lines ...]            # fallback raw lines
    }
    """
    print("   🔎 extract_specifications")
    # try to open accordion; content wait selector points to container
    _ = open_and_ensure(page,
                        'button:has(h3:text("Specifications"))',
                        content_wait_selector='[data-test="item-details-specifications"]',
                        open_timeout=6000)
    specs = {}
    raw = []
    try:
        container = page.query_selector('[data-test="item-details-specifications"]')
        if not container:
            # fallback: search for block with 'TCIN' etc
            container = page.query_selector('div:has-text("TCIN")')
        if container:
            # target immediate child blocks that hold each line
            # Usually structure is <div><div><b>Key:</b> Value</div><hr/></div>...
            child_divs = container.query_selector_all("div")
            for div in child_divs:
                try:
                    text = safe_inner_text(div)
                    if not text:
                        continue
                    # skip very short separators
                    if len(text.strip()) < 2:
                        continue
                    # normalize whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                    raw.append(text)
                    # Try parse "Key: Value" or "Key: value" or "TCIN: 123"
                    if ":" in text:
                        # split only on first colon
                        k, v = [s.strip() for s in text.split(":", 1)]
                        if k:
                            specs[k] = v
                    else:
                        # sometimes <b>Key</b> and the value is in the same string without colon
                        # e.g. "<b>TCIN</b> 94741587"
                        m = re.match(r'^(?P<k>[A-Za-z0-9 _\(\)\/-]+)\s+(?P<v>.+)$', text)
                        if m:
                            k = m.group('k').strip()
                            v = m.group('v').strip()
                            specs[k] = v
                except:
                    continue
    except Exception as e:
        print("      ⚠️ specs extraction error:", e)

    print(f"      → specs parsed: {len(specs)} keys, raw lines: {len(raw)}")
    return {"specs": specs, "raw": raw}

def extract_label_info(page):
    """
    Open Label Info accordion and extract Ingredients / nutrition text.
    Returns cleaned ingredients string or None.
    """
    print("   🔎 extract_label_info")
    opened = open_and_ensure(page,
                             '[data-test="@web/site-top-of-funnel/ProductDetailCollapsible-LabelInfo"] button',
                             content_wait_selector='[data-test="productDetailTabs-nutritionFactsTab"]',
                             open_timeout=8000)
    if not opened:
        # alternate click attempt
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
                # if selector yields header only, search deeper
                if 'Ingredients' in txt and len(txt) < 40:
                    el = page.query_selector(sel)
                    if el:
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
        if ing_text.lower().startswith('ingredients:'):
            ing_text = ing_text[len('ingredients:'):].strip()
        print("      ✅ ingredients found")
    else:
        print("      ⚠️ ingredients not found")
    return ing_text

# --------------- Core variant loop ----------------

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

            # click and wait UI update
            try:
                a.click()
            except:
                try:
                    product_page.evaluate('(el)=>el.click()', a)
                except:
                    pass

            product_page.wait_for_timeout(DEFAULT_WAIT_MS)

            # basic fields
            title = safe_inner_text(product_page.query_selector('h1') or product_page.query_selector('[data-test="product-title"]'))
            price = safe_inner_text(product_page.query_selector('[data-test="current-price"]') or product_page.query_selector('[data-test="product-price"]'))
            image_url = None
            try:
                img = product_page.query_selector('img[data-test="image-gallery-item-0"]') or product_page.query_selector('img[src*="target.scene7.com"]')
                if img:
                    image_url = img.get_attribute('src') or img.get_attribute('data-src')
            except:
                image_url = None

            availability = None
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

            sku = None
            try:
                m = product_page.query_selector('meta[itemprop="sku"]') or product_page.query_selector('meta[name="sku"]')
                if m:
                    sku = m.get_attribute('content')
            except:
                sku = None
            if not sku:
                try:
                    tcin_el = product_page.query_selector('div:has-text("TCIN")')
                    if tcin_el:
                        txt = safe_inner_text(tcin_el)
                        if txt:
                            found = re.search(r'(\d{5,})', txt)
                            sku = found.group(1) if found else txt.strip()
                except:
                    sku = sku

            # ---------------- extract deep content ----------------
            desc_obj = extract_description(product_page)
            specs_obj = extract_specifications(product_page)
            label_obj = extract_label_info(product_page)

            # parse specs into safe variable names
            # specs_map = specs_obj.get('specs', {}) if specs_obj else {}
            # spec_variables = {}
            # for k, v in specs_map.items():
            #     safe_k = to_safe_key(k)
            #     # handle duplicates: if safe_k exists, append numeric suffix
            #     if safe_k in spec_variables:
            #         idx = 1
            #         while f"{safe_k}_{idx}" in spec_variables:
            #             idx += 1
            #         safe_k = f"{safe_k}_{idx}"
            #     spec_variables[safe_k] = v

            # # Normalize some common names (example: item number -> item_number_dpci)
            # # (Optional) you can add more mapping rules here if desired
            # if 'item_number' in spec_variables and 'dpci' in spec_variables['item_number'].lower() is False:
            #     # keep as is
            #     specs_dict = dict(spec_variables)
            #     # 2. Ambil satu per satu sesuai nama variabel
            #     suggested_age = specs_dict.get("suggested_age")
            #     health_facts = specs_dict.get("health_facts")
            #     color_finish = specs_dict.get("color_finish")
            #     color_palette = specs_dict.get("color_palette")
            #     product_form = specs_dict.get("product_form")
            #     sustainability_claims = specs_dict.get("sustainability_claims")
            #     beauty_purpose = specs_dict.get("beauty_purpose")
            #     net_weight = specs_dict.get("net_weight")
            #     tcin = specs_dict.get("tcin")
            #     upc = specs_dict.get("upc")
            #     item_number_dpci = specs_dict.get("item_number_dpci")
            #     origin = specs_dict.get("origin")
            #     pass
            
            # variant_data = {
            #     'section_index': s_idx,
            #     'variant_index': i+1,
            #     'variant_label': label,
            #     'variant_href': href,
            #     'title': title,
            #     'price': price,
            #     'availability': availability,
            #     'image': image_url,
            #     'sku': sku,
            #     'description': desc_obj,
            #     'specifications_raw': specs_obj,
            #     'label_info': label_obj,
            #     'product_page_url': product_page.url,
            #     # inject spec variables directly
            #     **spec_variables
            # }

            # results.append(variant_data)

            # # Diagnostic printing
            # print("   → title:", title)
            # print("   → price:", price)
            # print("   → availability:", availability)
            # print("   → image:", image_url)
            # print("   → sku:", sku)
            # print("   → description (len):", (len(desc_obj['description']) if desc_obj and desc_obj.get('description') else 0))
            # print("   → specs keys:", list(specs_map.keys())[:10])
            # print("   → mapped spec vars:", list(spec_variables.items())[:12])
            # print("   → ingredients present:", bool(label_obj))
            # # 3. Tinggal print seperti title/price tadi
            # print("→ suggested_age:", suggested_age)
            # print("→ health_facts:", health_facts)
            # print("→ color_finish:", color_finish)
            # print("→ color_palette:", color_palette)
            # print("→ product_form:", product_form)
            # print("→ sustainability_claims:", sustainability_claims)
            # print("→ beauty_purpose:", beauty_purpose)
            # print("→ net_weight:", net_weight)
            # print("→ tcin:", tcin)
            # print("→ upc:", upc)
            # print("→ item_number_dpci:", item_number_dpci)
            # print("→ origin:", origin)


            # parse specs into safe variable names
            specs_map = specs_obj.get('specs', {}) if specs_obj else {}
            spec_variables = {}
            for k, v in specs_map.items():
                safe_k = to_safe_key(k)
                # handle duplicates: if safe_k exists, append numeric suffix
                if safe_k in spec_variables:
                    idx = 1
                    while f"{safe_k}_{idx}" in spec_variables:
                        idx += 1
                    safe_k = f"{safe_k}_{idx}"
                spec_variables[safe_k] = v

            # ALWAYS make a dict copy we can safely .get() from
            specs_dict = dict(spec_variables)

            # 2. Ambil satu per satu sesuai nama variabel (diagnostic variables)
            suggested_age = specs_dict.get("suggested_age")
            health_facts = specs_dict.get("health_facts")
            color_finish = specs_dict.get("color_finish")
            color_palette = specs_dict.get("color_palette")
            product_form = specs_dict.get("product_form")
            sustainability_claims = specs_dict.get("sustainability_claims")
            beauty_purpose = specs_dict.get("beauty_purpose")
            net_weight = specs_dict.get("net_weight")
            tcin = specs_dict.get("tcin")
            upc = specs_dict.get("upc")
            item_number_dpci = specs_dict.get("item_number_dpci") or specs_dict.get("item_number")
            origin = specs_dict.get("origin")

            # (Optional) normalize a couple of common alias keys:
            # sometimes DPCI appears as 'item_number' or 'item_number_dpci'; fallback already above.

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
                'specifications_raw': specs_obj,
                'label_info': label_obj,
                'product_page_url': product_page.url,
                # inject spec variables directly
                **spec_variables
            }

            results.append(variant_data)

            # Diagnostic printing
            print("   → title:", title)
            print("   → price:", price)
            print("   → availability:", availability)
            print("   → image:", image_url)
            print("   → sku:", sku)
            print("   → description (len):", (len(desc_obj['description']) if desc_obj and desc_obj.get('description') else 0))
            print("   → specs keys:", list(specs_map.keys())[:10])
            print("   → mapped spec vars:", list(spec_variables.items())[:12])
            print("   → ingredients present:", bool(label_obj))

            # 3. Diagnostic: print each spec variable individually (safe even if missing)
            print("→ suggested_age:", suggested_age)
            print("→ health_facts:", health_facts)
            print("→ color_finish:", color_finish)
            print("→ color_palette:", color_palette)
            print("→ product_form:", product_form)
            print("→ sustainability_claims:", sustainability_claims)
            print("→ beauty_purpose:", beauty_purpose)
            print("→ net_weight:", net_weight)
            print("→ tcin:", tcin)
            print("→ upc:", upc)
            print("→ item_number_dpci:", item_number_dpci)
            print("→ origin:", origin)


            # small throttle
            product_page.wait_for_timeout(250)

    print("\n🎉 Finished variants for this product page.")
    return results

# -------- Listing / pagination / orchestration --------

def inspect_product_cards(page, context):
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

            # open product page
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
                    # print basic row summary
                    print(f"    • [{vr['variant_index']}] {vr['variant_label']} | {vr.get('price')} | {vr.get('availability')}")
                    # example access to parsed specs:
                    # print("      suggested_age =", vr.get('suggested_age'))
                # optional: save/append results anywhere here

            except Exception as e:
                print("   ❌ failed to open product page:", e)
            finally:
                try:
                    product_page.close()
                except:
                    pass

        except Exception as e:
            print("   ⚠️ Error reading listing item:", e)

def auto_scroll_to_bottom(page, step=1000, max_wait=40):
    print("\n🌀 Scrolling to bottom")
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
            print("✅ reached bottom")
            break
        if time.time() - start_time > max_wait:
            print("⚠️ scroll timeout")
            break

def go_through_pagination(page, context, max_pages=None):
    page_num = 1
    while True:
        print(f"\n📄 On listing page {page_num}")
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
