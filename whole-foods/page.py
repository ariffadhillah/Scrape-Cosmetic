import requests
from bs4 import BeautifulSoup
import json
import html
import re
import time
import random

# --- KONFIGURASI TESTING ---
# Masukkan ASIN yang ingin di-test di sini
# TARGET_ASIN = "B0787W3GP9" 
# TARGET_ASIN = "B074H6F7GG" 
# TARGET_ASIN = "B0DPN5NL66" 
# TARGET_ASIN = "B07C45R6G9" 
# TARGET_ASIN = "B09DS5J8F9" 
TARGET_ASIN = "B07887CXXC" 
# TARGET_ASIN = "B074H6X5HF" 
# TARGET_ASIN = "B074H6S8D8" 
test_url = f"https://www.amazon.com/dp/{TARGET_ASIN}"

headers_base = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Upgrade-Insecure-Requests": "1"
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

session = requests.Session()
session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

# ==========================================
# FUNGSI-FUNGSI EKSTRAKSI (Tetap Sama)
# ==========================================



def _clean_label(s: str) -> str:
    if not s: return ""
    s = s.replace("\u200e", " ").replace("\u200f", " ").replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"\s*:\s*$", "", s)
    return s

def _clean_value(s: str) -> str:
    if not s: return ""
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_amazon_attributes(soup) -> dict:
    attrs = {}

    def put(k, v):
        k = _clean_label(k)
        v = _clean_value(v)
        if k and v and k not in attrs:
            attrs[k] = v

    # A) th/td tables (product details / tech spec / general keyvalue)
    for row in soup.select("table tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            put(th.get_text(" ", strip=True), td.get_text(" ", strip=True))

    # B) old td/td table
    for row in soup.select("table.a-normal.a-spacing-micro tr"):
        tds = row.find_all("td")
        if len(tds) >= 2:
            put(tds[0].get_text(" ", strip=True), tds[1].get_text(" ", strip=True))

    # C) detail bullets (span.a-text-bold + value)
    for li in soup.select("#detailBullets_feature_div li"):
        b = li.select_one("span.a-text-bold")
        if b:
            key = b.get_text(" ", strip=True)
            b.extract()
            val = li.get_text(" ", strip=True).lstrip(":").strip()
            put(key, val)
        else:
            txt = li.get_text(" ", strip=True)
            if ":" in txt:
                k, v = txt.split(":", 1)
                put(k, v)

    # D) productOverview_feature_div (kadang Amazon pakai ini)
    for row in soup.select("#productOverview_feature_div tr"):
        tds = row.find_all(["td", "th"])
        if len(tds) >= 2:
            put(tds[0].get_text(" ", strip=True), tds[1].get_text(" ", strip=True))

    return attrs

def get_product_value_universal(soup, label):
    attrs = extract_amazon_attributes(soup)

    # synonyms biar "Weight" ketemu walau labelnya beda
    key = _clean_label(label)
    synonyms = {
        "weight": ["weight", "item weight", "package weight", "shipping weight", "net weight", "product weight"],
        "volume": ["volume", "item volume", "package volume"],
        "ingredient type": ["ingredient type", "ingredients", "ingredient", "special ingredients"],
        "cuisine": ["cuisine", "cuisine type"],
        "specialty": ["specialty", "speciality", "diet type", "dietary information"],
    }

    candidates = synonyms.get(key, [key])

    # exact lookup dulu
    for c in candidates:
        c = _clean_label(c)
        if c in attrs:
            return attrs[c]

    # fallback: contains match
    for k, v in attrs.items():
        for c in candidates:
            c = _clean_label(c)
            if c in k or k in c:
                return v

    return None





def get_soup(url):
    headers = headers_base.copy()
    headers["User-Agent"] = random.choice(user_agents)
    try:
        res = session.get(url, headers=headers, timeout=40)
        if res.status_code == 200:
            return BeautifulSoup(res.text, "html.parser")
        else:
            print(f"  Gagal! Status Code: {res.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    return None

# ==========================================
# PROSES TESTING SINGLE ASIN
# ==========================================

print(f"--- TESTING SINGLE ASIN: {TARGET_ASIN} ---")
print(f"URL: {test_url}\n")

soup = get_soup(test_url)

if soup:
    title_tag = soup.select_one("#productTitle") or soup.select_one(".qa-title-text")
    
    if title_tag:
        print("Cuisine:", get_product_value_universal(soup, "Cuisine"))
        print("Specialty:", get_product_value_universal(soup, "Specialty"))
        print("Weight:", get_product_value_universal(soup, "Weight"))
        print("Volume:", get_product_value_universal(soup, "Volume"))
        print("Package Information:", get_product_value_universal(soup, "Package Information"))
        print("Allergen Information:", get_product_value_universal(soup, "Allergen Information"))
        print("Item Form:", get_product_value_universal(soup, "Item Form"))
        print("Brand:", get_product_value_universal(soup, "Brand"))
        print(":", get_product_value_universal(soup, "Item Weight"))
        print(":", get_product_value_universal(soup, "Number of Items"))
        print(":", get_product_value_universal(soup, "Unit Count"))
        print("Ingredient Type:", get_product_value_universal(soup, "Ingredient Type"))

        print("RESULT:")
        print("-" * 30)
        print("Product Name        :", title_tag.get_text(strip=True))

        print()

        print("-" * 30)
    else:
        # Cek apakah terkena Bot Check/Captcha
        if "api-services-support@amazon.com" in soup.text or "captcha" in soup.text.lower():
            print("Gagal: Terdeteksi CAPTCHA oleh Amazon. Coba ganti koneksi atau gunakan Proxy.")
        else:
            print("Gagal: Judul tidak ditemukan. Struktur halaman mungkin berbeda.")
else:
    print("Gagal memuat halaman.")