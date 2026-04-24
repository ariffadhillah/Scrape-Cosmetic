"""
playwright_rotate_headful.py

Playwright headful scraper with rotating proxies for Target category pages.
- Launches Chromium (visible) with each proxy option
- Navigates to TARGET_URL, waits for JS to load products
- Auto-scroll until stable
- Detects "Sorry for the wait" or absence of product-card
- Extract product title/url/price and save to CSV + HTML

Usage:
  - pip install playwright pandas
  - python -m playwright install
  - python playwright_rotate_headful.py
"""

import time
import csv
import random
import os
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------- CONFIG ----------------
TARGET_URL = "https://www.target.com/c/beauty/-/N-55r1x"
OUTPUT_DIR = "pw_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# proxy entries: host:port:username:password  OR host:port  OR None
PROXIES = [
    # "dc.decodo.com:10001:user-scraping-country-us:Zg1wsoj_6A1hdI6orG",
    # "us-proxy.example.com:8000:user:pass",
    None  # try direct connection first (optional)
]

USER_AGENTS = [
    # a few common UA to rotate
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# How long to wait for initial product area to appear (seconds)
WAIT_FOR_PRODUCTS = 12
# Auto-scroll settings
SCROLL_PAUSE = 1.5
MAX_SCROLL_STEPS = 60

# politeness
SLEEP_BETWEEN_TRIES = 2.0

# ----------------------------------------

def parse_proxy_entry(entry):
    """Return a dict suitable for Playwright browser launch proxy param or None."""
    if not entry:
        return None
    parts = entry.split(":")
    if len(parts) == 2:
        host, port = parts
        return {"server": f"http://{host}:{port}"}
    elif len(parts) == 4:
        host, port, user, pw = parts
        return {"server": f"http://{host}:{port}", "username": user, "password": pw}
    else:
        # Accept full URL e.g. http://user:pass@host:port
        if entry.startswith("http://") or entry.startswith("https://"):
            return {"server": entry}
        raise ValueError("Proxy entry format not supported: " + str(entry))

def is_blocked_content(content: str) -> bool:
    lower = content.lower()
    if "sorry for the wait" in lower or "a little busier" in lower:
        return True
    # message patterns that indicate no product data
    if "not found" in lower and "redsky" in lower:
        return True
    return False

def auto_scroll_page(page):
    """Scroll down until the page height stops increasing or max steps reached."""
    previous_height = page.evaluate("() => document.body.scrollHeight")
    steps = 0
    while steps < MAX_SCROLL_STEPS:
        page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(SCROLL_PAUSE)
        new_height = page.evaluate("() => document.body.scrollHeight")
        if new_height == previous_height:
            steps += 1
        else:
            steps = 0
            previous_height = new_height
        # small break to allow dynamic loading
    return

def extract_items_from_page(page):
    """Extract product items using data-test attributes (title, url, price)."""
    items = []
    # wait for a short moment to ensure DOM stable
    time.sleep(0.5)
    product_cards = page.query_selector_all("div[data-test='product-card']")
    for card in product_cards:
        # title
        title_el = card.query_selector("[data-test='product-title']")
        title = title_el.inner_text().strip() if title_el else None

        # url
        a_el = card.query_selector("a[href]")
        url = None
        if a_el:
            href = a_el.get_attribute("href")
            if href:
                if href.startswith("/"):
                    url = "https://www.target.com" + href
                else:
                    url = href

        # price
        price_el = card.query_selector("[data-test='product-price']")
        price = price_el.inner_text().strip() if price_el else None

        items.append({"title": title, "url": url, "price": price})
    return items

def try_with_proxy(proxy_entry):
    """Try to open page with given proxy. Returns items list or None if failed/blocked."""
    proxy_conf = parse_proxy_entry(proxy_entry) if proxy_entry else None
    ua = random.choice(USER_AGENTS)

    with sync_playwright() as p:
        browser_args = {
            "headless": False  # headful as requested
        }
        # Launch Chromium with proxy if provided
        try:
            if proxy_conf:
                browser = p.chromium.launch(proxy=proxy_conf, headless=False, args=["--start-maximized"])
            else:
                browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        except Exception as e:
            print(f"  [ERR] Failed to launch browser with proxy {proxy_entry}: {e}")
            return None, f"launch_error:{e}"

        context = browser.new_context(user_agent=ua, viewport={"width":1366,"height":768})
        page = context.new_page()
        try:
            print(f"  -> Navigating with proxy={proxy_entry} user-agent={ua[:60]}...")
            page.goto(TARGET_URL, timeout=30000)
        except PlaywrightTimeoutError:
            print("  [WARN] Navigation timed out.")
        except Exception as e:
            print("  [WARN] Navigation error:", e)

        # give extra time for JS to run and API calls to fire
        try:
            # wait for either product grid OR some seconds if not appearing
            page.wait_for_selector("div[data-test='product-card']", timeout=WAIT_FOR_PRODUCTS*1000)
            # only proceed if selector appears
        except PlaywrightTimeoutError:
            # products didn't appear in time; capture content for inspection
            content = page.content()
            blocked = is_blocked_content(content)
            if blocked:
                print("  [INFO] Page appears blocked/queued (message detected).")
                page.close()
                context.close()
                browser.close()
                return None, "blocked"
            else:
                # maybe products load later; try scrolling and wait more
                print("  [INFO] product-card not found immediately — will attempt auto-scroll & wait.")
        except Exception as e:
            print("  [WARN] wait_for_selector error:", e)

        # attempt auto-scroll to trigger lazy-load
        try:
            auto_scroll_page(page)
        except Exception as e:
            print("  [WARN] auto-scroll error:", e)

        # snapshot content and check for block
        content = page.content()
        if is_blocked_content(content):
            print("  [INFO] After scroll: blocked/queued detected.")
            page.close()
            context.close()
            browser.close()
            return None, "blocked_after_scroll"

        # extract items
        items = extract_items_from_page(page)

        # save snapshot html for debugging
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        html_fname = os.path.join(OUTPUT_DIR, f"page_snapshot_{ts}.html")
        with open(html_fname, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [SAVED] snapshot -> {html_fname}")

        # cleanup
        page.close()
        context.close()
        browser.close()

        # return items list (may be empty)
        return items, "ok"

def save_to_csv(items, prefix="target_beauty"):
    if not items:
        print("No items to save.")
        return None
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    csv_path = os.path.join(OUTPUT_DIR, f"{prefix}_items_{ts}.csv")
    # normalize and write
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["title", "url", "price"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for it in items:
            writer.writerow({"title": it.get("title"), "url": it.get("url"), "price": it.get("price")})
    print("Saved CSV:", csv_path)
    return csv_path

def main():
    all_items = []
    print("** Starting Playwright rotating-proxy scrape (headful) **")
    for proxy_entry in PROXIES:
        print(f"\nTrying proxy: {proxy_entry}")
        items, status = try_with_proxy(proxy_entry)
        print("Result status:", status, " -> items count:", len(items) if items else 0)
        if items:
            all_items.extend(items)
            # optionally break after first successful proxy that yields items
            break
        else:
            # polite wait then try next proxy
            time.sleep(SLEEP_BETWEEN_TRIES)

    if not all_items:
        print("\nNo items collected from any proxy. Consider these troubleshooting steps:")
        print("- Use premium/residential US proxies (rotating) - many datacenter IPs are blocked.")
        print("- Increase WAIT_FOR_PRODUCTS and SCROLL_PAUSE to allow JS time.")
        print("- Try running without proxy or with a different category ID.")
        return

    # dedupe by url/title
    unique = []
    seen = set()
    for it in all_items:
        key = (it.get("url") or "") + "|" + (it.get("title") or "")
        if key not in seen:
            seen.add(key)
            unique.append(it)

    save_to_csv(unique)
    print("\nDone. Total unique items saved:", len(unique))

if __name__ == "__main__":
    main()
