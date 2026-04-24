import requests
from bs4 import BeautifulSoup
import json
import html
import re
import time
import random
import csv

# --- KONFIGURASI ---
url_storefront = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"
OUTPUT_CSV = "asins.csv"

headers_base = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

session = requests.Session()
session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})


def get_soup(url):
    headers = headers_base.copy()
    headers["User-Agent"] = random.choice(user_agents)
    try:
        time.sleep(random.uniform(1.5, 3.0))
        res = session.get(url, headers=headers, timeout=25)
        if res.status_code == 200:
            # deteksi sederhana bot/captcha
            low = res.text.lower()
            if "robot check" in low or "captcha" in low:
                print("  [!] CAPTCHA/Robot check terdeteksi di storefront.")
                return None
            return BeautifulSoup(res.text, "html.parser")
        print(f"  [{res.status_code}] gagal load storefront")
    except Exception as e:
        print("  Error:", e)
    return None


def extract_asin(text: str):
    if not text:
        return None
    m = re.search(r"\b([A-Z0-9]{10})\b", text.upper())
    return m.group(1) if m else None


def collect_asins_from_storefront(soup) -> list[str]:
    asins = set()

    # Sections yang kamu pakai
    sections = soup.find_all("div", attrs={"data-carouselheadingattributesstring": True})

    for sec in sections:
        # 1) ambil ASIN dari <a href="/dp/ASIN">
        for a in sec.select("a[href*='/dp/']"):
            asin = extract_asin(a.get("href", ""))
            if asin:
                asins.add(asin)

        # 2) ambil ASIN dari data-a-carousel-options -> ajax.id_list
        carousel_options = sec.get("data-a-carousel-options")
        if carousel_options:
            try:
                data = json.loads(carousel_options)
                id_list = data.get("ajax", {}).get("id_list", [])
                for item_str in id_list:
                    try:
                        asin = json.loads(item_str).get("id")
                    except Exception:
                        asin = None
                    asin = extract_asin(asin or "")
                    if asin:
                        asins.add(asin)
            except Exception:
                pass

    # fallback tambahan: kadang ada link /gp/product/ASIN juga
    for a in soup.select("a[href*='/gp/product/']"):
        asin = extract_asin(a.get("href", ""))
        if asin:
            asins.add(asin)

    return sorted(asins)


def save_asins_to_csv(asins: list[str], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ASIN"])
        for asin in asins:
            w.writerow([asin])


def main():
    print("Sedang mengambil daftar ASIN dari storefront...")
    soup = get_soup(url_storefront)
    if not soup:
        print("Gagal memuat storefront (mungkin CAPTCHA).")
        return

    asins = collect_asins_from_storefront(soup)
    print("Total ASIN ditemukan:", len(asins))

    save_asins_to_csv(asins, OUTPUT_CSV)
    print("Saved:", OUTPUT_CSV)


if __name__ == "__main__":
    main()