import requests
from bs4 import BeautifulSoup
import json
import html
import re
import time
import random

# --- KONFIGURASI ---
url_storefront = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"

headers_base = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Upgrade-Insecure-Requests": "1"
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

session = requests.Session()
session.cookies.update({
    "i18n-prefs": "USD",
    "lc-main": "en_US"
})

# ==========================================
# HELPER
# ==========================================

def get_soup(url):
    headers = headers_base.copy()
    headers["User-Agent"] = random.choice(user_agents)

    try:
        res = session.get(url, headers=headers, timeout=40)

        if res.status_code == 200:
            return BeautifulSoup(res.text, "html.parser")

        elif res.status_code == 503:
            print("  [503] Bot detected, wait 15s...")
            time.sleep(15)

    except Exception as e:
        print("Request error:", e)

    return None


def extract_asin(text):
    match = re.search(r"([A-Z0-9]{10})", text or "")
    return match.group(1) if match else None


# ==========================================
# CORE FUNCTION (INI YANG NANTI DIPAKAI MAIN)
# ==========================================

def get_category_products():

    print("Mengambil daftar produk dari storefront...")

    soup_main = get_soup(url_storefront)

    if not soup_main:
        print("Gagal memuat halaman utama.")
        return []

    all_data = []

    sections = soup_main.find_all(
        "div",
        attrs={"data-carouselheadingattributesstring": True}
    )

    for sec in sections:

        try:
            heading_json = html.unescape(sec["data-carouselheadingattributesstring"])
            title_cat = json.loads(heading_json).get("headingText", "Unknown").strip()
        except:
            title_cat = "Unknown"

        seen_asins = set()
        urls_in_section = []

        # ---- LINK NORMAL ----
        for a in sec.select("a[href*='/dp/']"):
            asin = extract_asin(a.get("href"))

            if asin and asin not in seen_asins:
                seen_asins.add(asin)
                urls_in_section.append(f"https://www.amazon.com/dp/{asin}")

        # ---- LINK AJAX CAROUSEL ----
        carousel_options = sec.get("data-a-carousel-options")

        if carousel_options:
            try:
                ajax_ids = json.loads(carousel_options).get("ajax", {}).get("id_list", [])

                for item_str in ajax_ids:
                    asin = json.loads(item_str).get("id")

                    if asin and asin not in seen_asins:
                        seen_asins.add(asin)
                        urls_in_section.append(f"https://www.amazon.com/dp/{asin}")

            except:
                pass

        if urls_in_section:
            all_data.append({
                "category": title_cat,
                "urls": urls_in_section
            })

    print(f"Total kategori ditemukan: {len(all_data)}")

    return all_data


# def get_all_asins_from_category():

#     soup_main = get_soup(url_storefront)
#     if not soup_main:
#         print("Gagal memuat halaman utama.")
#         return []

#     all_asins = []
#     sections = soup_main.find_all("div", attrs={"data-carouselheadingattributesstring": True})

#     for sec in sections:

#         seen_asins = set()

#         # dari link HTML
#         for a in sec.select("a[href*='/dp/']"):
#             asin = extract_asin(a.get("href"))
#             if asin and asin not in seen_asins:
#                 seen_asins.add(asin)
#                 all_asins.append(asin)

#         # dari ajax carousel
#         carousel_options = sec.get("data-a-carousel-options")
#         if carousel_options:
#             try:
#                 ajax_ids = json.loads(carousel_options).get("ajax", {}).get("id_list", [])
#                 for item_str in ajax_ids:
#                     asin = json.loads(item_str).get("id")
#                     if asin and asin not in seen_asins:
#                         seen_asins.add(asin)
#                         all_asins.append(asin)
#             except:
#                 pass

#     return all_asins


def get_all_asins_from_category():

    soup_main = get_soup(url_storefront)
    if not soup_main:
        print("Gagal memuat halaman utama.")
        return []

    results = []
    sections = soup_main.find_all("div", attrs={"data-carouselheadingattributesstring": True})

    for sec in sections:

        # ambil nama kategori
        try:
            heading_json = html.unescape(sec["data-carouselheadingattributesstring"])
            title_cat = json.loads(heading_json).get("headingText", "Unknown").strip()
        except:
            title_cat = "Unknown"

        seen_asins = set()

        # dari HTML link
        for a in sec.select("a[href*='/dp/']"):
            asin = extract_asin(a.get("href"))
            if asin and asin not in seen_asins:
                seen_asins.add(asin)
                results.append((title_cat, asin))

        # dari ajax carousel
        carousel_options = sec.get("data-a-carousel-options")
        if carousel_options:
            try:
                ajax_ids = json.loads(carousel_options).get("ajax", {}).get("id_list", [])
                for item_str in ajax_ids:
                    asin = json.loads(item_str).get("id")
                    if asin and asin not in seen_asins:
                        seen_asins.add(asin)
                        results.append((title_cat, asin))
            except:
                pass

    return results

# ==========================================
# OPTIONAL: RUN STANDALONE (MASIH BISA TEST)
# ==========================================

if __name__ == "__main__":

    data = get_category_products()

    for item in data:
        print("\nCATEGORY:", item["category"])

        for url in item["urls"]:
            print(url)


