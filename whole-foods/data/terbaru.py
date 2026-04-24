import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import csv
import os

# =========================
# KONFIGURASI
# =========================
BASE_URL = "https://www.amazon.com/dp/"
OUTPUT_CSV = "products-Whole-Foods-Market-1.csv"

FIELDNAMES = [
    "Main Category","Sub Category","Product Name","Product_url","Item Model Number","Package Dimensions","UPC","ASIN","Manufacturer","Units","Brand","Size","Flavor",
    "Item Weight","Specialty","Unit Count","Weight","Number of Items","Volume","Item Form","Allergen Information",
    "Cuisine","Variety","Temperature Condition","Number of Pieces","Package Information",
    "Produce sold as","Region of Origin",
    "Nutrition information Serving Size","Calories",
    "Total Fat","Saturated Fat","Trans Fat","Monounsaturated Fat","Polyunsaturated Fat","Cholesterol","Sodium",
    "Total Carbohydrate","Dietary Fiber","Soluble Fiber","Insoluble Fiber","Sugars","Added Sugars",
    "Starch","Other Carbohydrate","Sugar Alcohol","Protein","Vitamin A","Vitamin C","Calcium","Iron","Potassium",
    "Ingredients","Legal Disclaimer","Disclaimer","Product Description","Image Url","Reviews","Stars"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]
def write_row_safe(writer, row: dict):
    safe = {}
    for k in FIELDNAMES:
        v = row.get(k, "")
        if isinstance(v, str):
            v = v.replace("\r", " ").replace("\n", " ").strip()
        safe[k] = v
    writer.writerow(safe)
def load_asins_from_csv(path: str, asin_column: str = "ASIN") -> list[str]:
    if not os.path.exists(path):
        print(f"[!] File tidak ditemukan: {path}")
        return []

    asins = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        # Kalau file tidak punya header, DictReader akan gagal (fieldnames None)
        if reader.fieldnames is None:
            f.seek(0)
            raw = f.read()
            found = re.findall(r"\b[A-Z0-9]{10}\b", raw.upper())
            return list(dict.fromkeys(found))  # dedupe, keep order

        fieldnames_norm = [c.strip().lower() for c in reader.fieldnames if c]

        for row in reader:
            # 1) Prioritas: kolom ASIN jika ada
            asin_val = None
            if asin_column and asin_column.strip().lower() in fieldnames_norm:
                # cari key asli yang cocok (case-insensitive)
                for k in row.keys():
                    if k and k.strip().lower() == asin_column.strip().lower():
                        asin_val = row.get(k)
                        break

            # 2) Kalau tidak ada / kosong: scan seluruh value dalam row
            if asin_val and str(asin_val).strip():
                m = re.search(r"\b([A-Z0-9]{10})\b", str(asin_val).upper())
                if m:
                    asins.append(m.group(1))
                    continue

            for v in row.values():
                if not v:
                    continue
                m = re.search(r"\b([A-Z0-9]{10})\b", str(v).upper())
                if m:
                    asins.append(m.group(1))
                    break

    # dedupe preserve order
    return list(dict.fromkeys(asins))

# =========================
# SMALL UTILS
# =========================
def safe_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""

def norm_space(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\u200e", " ").replace("\u200f", " ").replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _clean_label(s: str) -> str:
    s = norm_space(s).lower()
    s = re.sub(r"\s*:\s*$", "", s)
    return s

def _clean_value(s: str) -> str:
    return norm_space(s)

# =========================
# TITLE (lebih aman)
# =========================
def get_title(soup: BeautifulSoup):
    selectors = [
        "#productTitle",
        "h1#title span#productTitle",
        "h1#title span",
        "h1.a-size-large.a-spacing-none",
        "#titleSection #title",
        "#centerCol #title",
        "title",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        txt = norm_space(el.get_text(" ", strip=True)) if el else ""
        if txt:
            if sel == "title":
                txt = re.sub(r"^Amazon\.com:\s*", "", txt).strip()
                txt = re.sub(r"\s*:\s*Amazon\.com\s*$", "", txt).strip()
            return txt
    return None

# =========================
# CATEGORY (lebih aman)
# =========================
def get_category_levels(soup: BeautifulSoup):
    selector_candidates = [
        "#wayfinding-breadcrumbs_feature_div a",
        "#wayfinding-breadcrumbs_container a",
        "nav[aria-label='Breadcrumb'] a",
        "div[role='navigation'] a.a-link-normal.a-color-tertiary",
    ]

    categories = []
    for sel in selector_candidates:
        anchors = soup.select(sel)
        tmp = []
        for a in anchors:
            t = norm_space(a.get_text(" ", strip=True))
            if not t or t in {"›", ">"}:
                continue
            tmp.append(t)
        if tmp:
            categories = tmp
            break

    if not categories:
        return None, None

    main_category = categories[0]
    if len(categories) >= 3:
        sub_category = categories[-2]
    elif len(categories) >= 2:
        sub_category = categories[1]
    else:
        sub_category = None

    return main_category, sub_category

# =========================
# ATTR EXTRACTION (PATCH UTAMA)
# =========================
def extract_amazon_attributes(soup: BeautifulSoup) -> dict:
    """
    Return dict {normalized_label: value} dari berbagai layout Amazon.
    """
    attrs = {}

    def put(k, v):
        k = _clean_label(k)
        v = _clean_value(v)
        if k and v and k not in attrs:
            attrs[k] = v

    # 1) Detail bullets (kanan) - umum banget
    for li in soup.select("#detailBullets_feature_div li"):
        b = li.select_one("span.a-text-bold")
        if b:
            key = safe_text(b)
            b.extract()
            val = norm_space(li.get_text(" ", strip=True)).lstrip(":").strip()
            put(key, val)
        else:
            txt = norm_space(li.get_text(" ", strip=True))
            if ":" in txt:
                k, v = txt.split(":", 1)
                put(k, v)

    # 2) Product Overview
    for row in soup.select("#productOverview_feature_div tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            put(safe_text(cells[0]), safe_text(cells[1]))

    # 3) Product Details tables (paling penting, banyak data ada di sini)
    table_selectors = [
        "#productDetails_techSpec_section_1 tr",
        "#productDetails_techSpec_section_2 tr",
        "#productDetails_detailBullets_sections1 tr",
        "#productDetails_detailBullets_sections2 tr",
        "#technicalSpecifications_section_1 tr",
        "#technicalSpecifications_section_2 tr",
        "table#productDetailsTable tr",
    ]
    for sel in table_selectors:
        for row in soup.select(sel):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                put(safe_text(th), safe_text(td))
            else:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    put(safe_text(tds[0]), safe_text(tds[1]))

    # 4) Fallback: table key/value umum (kalau layout aneh)
    # (dibuat lebih aman: hanya table yang tampak seperti key/value)
    for table in soup.select("table"):
        for row in table.select("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                k = safe_text(th)
                v = safe_text(td)
                if k and v and len(k) <= 60:
                    put(k, v)

    return attrs

def get_product_value_universal(attrs: dict, label: str):
    """
    NOTE: sekarang param-nya attrs (hasil parse sekali).
    """
    key = _clean_label(label)

    synonyms = {
        "weight": ["weight", "item weight", "package weight", "shipping weight", "net weight", "product weight"],
        "volume": ["volume", "item volume", "package volume"],
        "ingredient type": ["ingredient type", "ingredients", "ingredient", "special ingredients"],
        "cuisine": ["cuisine", "cuisine type"],
        "specialty": ["specialty", "speciality", "diet type", "dietary information"],
        "brand": ["brand"],
        "size": ["size", "item package quantity", "dimensions"],
        "flavor": ["flavor", "flavour"],
    }

    candidates = synonyms.get(key, [key])

    for c in candidates:
        c = _clean_label(c)
        if c in attrs:
            return attrs[c]

    # fuzzy contains
    for k, v in attrs.items():
        for c in candidates:
            c = _clean_label(c)
            if c in k or k in c:
                return v

    return None

# =========================
# PRODUCT DESCRIPTION
# =========================
def get_product_text(soup: BeautifulSoup):
    # productDescription (classic)
    container = soup.find("div", id="productDescription")
    txt = norm_space(container.get_text(" ", strip=True)) if container else ""
    if txt:
        return txt

    # fallback: feature-bullets
    bullets = [norm_space(li.get_text(" ", strip=True)) for li in soup.select("#feature-bullets li span.a-list-item")]
    bullets = [b for b in bullets if b and "Make sure" not in b]
    return " | ".join(bullets) if bullets else None

# =========================
# NUTRITION (lebih generik)
# =========================
def _nutrition_map(soup: BeautifulSoup) -> dict:
    out = {}

    # kandidat table yang sering dipakai
    candidates = []
    candidates += soup.select("table#nic-nutrition-facts")
    candidates += soup.select("table[id*='nutrition']")
    candidates += soup.select("table[class*='nutrition']")

    for table in candidates:
        # cari row yang terlihat seperti "Label  Amount"
        for row in table.select("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            k = _clean_label(safe_text(cells[0]))
            v = _clean_value(safe_text(cells[1]))
            if k and v:
                out[k] = v

    return out

def get_nutrition_value(nutri: dict, label: str):
    key = _clean_label(label)
    if key in nutri:
        return nutri[key]
    # fuzzy
    for k, v in nutri.items():
        if key in k or k in key:
            return v
    return None

# =========================
# REVIEWS + STARS (robust)
# =========================
def get_reviews_count(soup: BeautifulSoup):
    # common
    el = soup.select_one("#acrCustomerReviewText")
    if el:
        m = re.search(r"[\d,]+", el.get_text(strip=True))
        return int(m.group(0).replace(",", "")) if m else None

    # fallback: data-hook
    el = soup.select_one("[data-hook='total-review-count']")
    if el:
        m = re.search(r"[\d,]+", el.get_text(strip=True))
        return int(m.group(0).replace(",", "")) if m else None

    return None

def get_stars(soup: BeautifulSoup):
    # common
    el = soup.select_one("#acrPopover")
    if el:
        t = norm_space(el.get("title") or el.get_text(" ", strip=True))
        m = re.search(r"(\d+(\.\d+)?)", t)
        return m.group(1) if m else None

    # fallback
    el = soup.select_one("i[data-hook='average-star-rating'] span.a-icon-alt")
    if el:
        t = el.get_text(" ", strip=True)
        m = re.search(r"(\d+(\.\d+)?)", t)
        return m.group(1) if m else None

    return None

# =========================
# IMAGE (robust)
# =========================
def get_main_image(soup: BeautifulSoup):
    img = soup.select_one("#imgTagWrapperId img")
    if img:
        hires = img.get("data-old-hires")
        if hires and hires.strip():
            return hires.strip()

        # dynamic image json
        dyn = img.get("data-a-dynamic-image")
        if dyn:
            try:
                data = json.loads(dyn)
                # ambil resolusi paling besar (biasanya key pertama cukup, tapi kita sort)
                best = sorted(data.keys(), key=lambda u: (data[u][0] * data[u][1]), reverse=True)[0]
                return best
            except Exception:
                pass

        src = img.get("src")
        return src.strip() if src else None

    # fallback lain (kadang id beda)
    img = soup.select_one("img#landingImage")
    if img:
        src = img.get("src")
        return src.strip() if src else None

    return None

# =========================
# IMPORTANT INFO (Ingredients/Legal Disclaimer)
# =========================
def _find_important_section(soup: BeautifulSoup):
    # beberapa halaman pakai "important-information", sebagian pakai expander lain
    return soup.find("div", id="important-information") or soup.find("div", id="aplus_feature_div")

def get_ingredients(soup: BeautifulSoup):
    container = _find_important_section(soup)
    if not container:
        return None

    # header bisa span/strong/h4
    header = container.find(string=lambda s: s and "ingredients" in s.lower())
    if not header:
        return None

    # ambil paragraf setelah header
    node = header.parent
    for p in node.find_all_next(["p", "div", "span"]):
        if container not in p.parents:
            break
        txt = norm_space(p.get_text(" ", strip=True))
        # stop kalau ketemu section lain
        if txt.lower().startswith(("legal disclaimer", "disclaimer", "directions")):
            break
        if txt and len(txt) > 3:
            return txt
    return None

def get_legal_disclaimer(soup: BeautifulSoup):
    container = _find_important_section(soup)
    if not container:
        return None

    header = container.find(string=lambda s: s and "legal disclaimer" in s.lower())
    if not header:
        return None

    node = header.parent
    for p in node.find_all_next(["p", "div", "span"]):
        if container not in p.parents:
            break
        txt = norm_space(p.get_text(" ", strip=True))
        if txt and len(txt) > 3:
            return txt
    return None

def get_disclaimer(soup):
    container = soup.find("div", id="storeDisclaimer_feature_div")
    if not container:
        return None
    label = container.find("strong", string=lambda s: s and "disclaimer" in s.lower())
    if not label:
        return None
    p = label.find_parent("p")
    if not p:
        return None
    text = p.get_text(" ", strip=True)
    return text.replace("Disclaimer:", "").strip()


# =========================
# HTTP + VARIANTS
# =========================
def get_soup(url, session, max_retries=3):
    for attempt in range(1, max_retries + 1):

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.amazon.com/",
            "Connection": "keep-alive",
        }

        try:
            # delay random + backoff
            delay = random.uniform(4, 7) + (attempt * 2)
            print(f"   ⏳ Attempt {attempt} | delay {round(delay,1)}s")
            time.sleep(delay)

            res = session.get(url, headers=headers, timeout=30)

            if res.status_code != 200:
                print(f"   ❌ Status {res.status_code}")
                continue

            low = res.text.lower()

            # CAPTCHA / BLOCK
            if "robot check" in low or "captcha" in low or "/errors/validatecaptcha" in low:
                print("   🚫 CAPTCHA detected")

                # kalau masih ada retry → ganti session
                if attempt < max_retries:
                    session = requests.Session()
                    session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
                    continue
                else:
                    return "CAPTCHA"

            # halaman aneh / bukan product
            if "dp/" in url and ("producttitle" not in low and "nav-bb-logo" not in low):
                print("   ⚠️ Not a valid product page")

                if attempt < max_retries:
                    continue
                else:
                    return None

            # SUCCESS
            return BeautifulSoup(res.text, "html.parser")

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

            if attempt == max_retries:
                return None

    return None

def get_all_variant_asins(soup):
    asins = set()
    scripts = soup.find_all("script", type="text/javascript")
    for script in scripts:
        content = script.string
        if content and "colorToAsin" in content:
            match = re.search(r"jQuery\.parseJSON\('(.+?)'\)", content)
            if match:
                try:
                    raw_json = match.group(1).replace("\\'", "'").encode().decode("unicode_escape")
                    data = json.loads(raw_json)
                    for key in data.get("colorToAsin", {}):
                        v_asin = data["colorToAsin"][key].get("asin")
                        if v_asin:
                            asins.add(v_asin)
                except Exception:
                    pass
    return list(asins)
# =========================
# PROCESS 1 SEED ASIN
# =========================

def process_seed_asin(seed_asin: str, writer, processed_asins: set):
    # session = requests.Session()
    # session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

    session = requests.Session()
    session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
    session.headers.update({"Connection": "keep-alive"})


    print(f"\n=== SEED ASIN: {seed_asin} ===")
    first_soup = get_soup(f"{BASE_URL}{seed_asin}", session)
    if first_soup == "CAPTCHA":
        print("Kena Block/Captcha di seed. Skip.")
        return
    if not first_soup:
        print("Gagal ambil halaman seed. Skip.")
        return

    variant_list = get_all_variant_asins(first_soup)
    if not variant_list:
        variant_list = [seed_asin]
        print("Tidak ada varian, ASIN tunggal.")
    else:
        if seed_asin not in variant_list:
            variant_list.insert(0, seed_asin)
        print(f"Varian ditemukan: {len(variant_list)}")

    seed_main, seed_sub = get_category_levels(first_soup)
    seed_main = (seed_main or "").strip()
    seed_sub  = (seed_sub or "").strip()

    for i, v_asin in enumerate(variant_list):
        if v_asin in processed_asins:
            print(f"SKIP (sudah diproses): {v_asin}")
            continue

        if i > 0 and i % 2 == 0:
            session = requests.Session()
            session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

        v_url = f"{BASE_URL}{v_asin}"
        print(f"-> [{i+1}/{len(variant_list)}] {v_asin}")

        # v_soup = get_soup(v_url, session)
        # if v_soup == "CAPTCHA":
        #     print(f"   [!] CAPTCHA: {v_asin} (skip)")
        #     continue
        # if not v_soup:
        #     print(f"   [!] Gagal load: {v_asin} (skip)")
        #     continue

        v_soup = get_soup(v_url, session)

        if v_soup == "CAPTCHA":
            print(f"   [!] CAPTCHA keras: {v_asin} (skip)")
            continue

        if not v_soup:
            print(f"   [!] Gagal setelah retry: {v_asin} (skip)")
            continue

        product_name = get_title(v_soup)
        if not product_name:
            print(f"   [!] Title tidak ketemu: {v_asin} | len_html={len(str(v_soup))}")
            page_text = v_soup.get_text(" ", strip=True)
            if "Sorry! We couldn't find that page" in page_text:
                print("      -> kemungkinan halaman 404/Not Found")
            if "Enter the characters you see below" in page_text:
                print("      -> kemungkinan CAPTCHA (tidak terdeteksi string)")
            if "Dogs of Amazon" in page_text:
                print("      -> kemungkinan 404/Dog page Amazon")
            continue

        main_category, sub_category = get_category_levels(v_soup)
        main_category = (main_category or "").strip() or seed_main
        sub_category  = (sub_category or "").strip() or seed_sub

        # parse sekali
        attrs = extract_amazon_attributes(v_soup)
        nutri = _nutrition_map(v_soup)

        row = {
            "Main Category": main_category,
            "Sub Category": sub_category,

            "Brand": get_product_value_universal(attrs, "Brand"),
            "Product Name": product_name,
            "Product_url": v_url,

            "Package Dimensions": get_product_value_universal(attrs, "Package Dimensions"),
            "Item Model Number": get_product_value_universal(attrs, "Item model number"),
            "UPC": get_product_value_universal(attrs, "UPC"),
            "Manufacturer": get_product_value_universal(attrs, "Manufacturer"),
            "ASIN": get_product_value_universal(attrs, "ASIN") or v_asin,
            "Units": get_product_value_universal(attrs, "Units"),
            "Item Form": get_product_value_universal(attrs, "Item Form"),

            "Nutrition information Serving Size": get_nutrition_value(nutri, "Serving Size"),
            "Calories": get_nutrition_value(nutri, "Calories"),

            "Total Fat": get_nutrition_value(nutri, "Total Fat"),
            "Saturated Fat": get_nutrition_value(nutri, "Saturated Fat"),
            "Trans Fat": get_nutrition_value(nutri, "Trans Fat"),
            "Monounsaturated Fat": get_nutrition_value(nutri, "Monounsaturated Fat"),
            "Polyunsaturated Fat": get_nutrition_value(nutri, "Polyunsaturated Fat"),
            "Cholesterol": get_nutrition_value(nutri, "Cholesterol"),
            "Sodium": get_nutrition_value(nutri, "Sodium"),
            "Total Carbohydrate": get_nutrition_value(nutri, "Total Carbohydrate"),
            "Dietary Fiber": get_nutrition_value(nutri, "Dietary Fiber"),
            "Soluble Fiber": get_nutrition_value(nutri, "Soluble Fiber"),
            "Insoluble Fiber": get_nutrition_value(nutri, "Insoluble Fiber"),
            "Sugars": get_nutrition_value(nutri, "Sugars"),
            "Added Sugars": get_nutrition_value(nutri, "Added Sugars"),
            "Starch": get_nutrition_value(nutri, "Starch"),
            "Other Carbohydrate": get_nutrition_value(nutri, "Other Carbohydrate"),
            "Sugar Alcohol": get_nutrition_value(nutri, "Sugar Alcohol"),
            "Protein": get_nutrition_value(nutri, "Protein"),
            "Vitamin A": get_nutrition_value(nutri, "Vitamin A"),
            "Vitamin C": get_nutrition_value(nutri, "Vitamin C"),
            "Calcium": get_nutrition_value(nutri, "Calcium"),
            "Iron": get_nutrition_value(nutri, "Iron"),
            "Potassium": get_nutrition_value(nutri, "Potassium"),

            "Item Weight": get_product_value_universal(attrs, "Item Weight"),
            "Specialty": get_product_value_universal(attrs, "Specialty"),
            "Unit Count": get_product_value_universal(attrs, "Unit Count"),
            "Weight": get_product_value_universal(attrs, "Weight"),
            "Number of Items": get_product_value_universal(attrs, "Number of Items"),
            "Volume": get_product_value_universal(attrs, "Volume"),
            "Allergen Information": get_product_value_universal(attrs, "Allergen Information"),
            "Cuisine": get_product_value_universal(attrs, "Cuisine"),
            "Variety": get_product_value_universal(attrs, "Variety"),
            "Temperature Condition": get_product_value_universal(attrs, "Temperature Condition"),
            "Number of Pieces": get_product_value_universal(attrs, "Number of Pieces"),
            "Package Information": get_product_value_universal(attrs, "Package Information"),
            "Produce sold as": get_product_value_universal(attrs, "Produce sold as"),
            "Region of Origin": get_product_value_universal(attrs, "Region of Origin"),
            "Size": get_product_value_universal(attrs, "Size"),
            "Flavor": get_product_value_universal(attrs, "Flavor"),

            "Ingredients": get_ingredients(v_soup),
            "Legal Disclaimer": get_legal_disclaimer(v_soup),
            "Disclaimer": get_disclaimer(v_soup),
            "Product Description": get_product_text(v_soup),
            "Image Url": get_main_image(v_soup),
            "Reviews": get_reviews_count(v_soup),
            "Stars": get_stars(v_soup),
        }

        write_row_safe(writer, row)
        processed_asins.add(v_asin)
        print(f"   ✅ Saved: {v_asin}")

def main():
    # Ambil ASIN dari CSV
    seed_asins = load_asins_from_csv("daftar_asin.csv", asin_column="ASIN")

    if not seed_asins:
        print("Tidak ada ASIN ditemukan di daftar_asin.csv")
        return

    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    processed_asins = set()

    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()

        for idx, asin in enumerate(seed_asins, start=1):
            asin = asin.strip().upper()
            if not asin:
                continue

            print("\n############################")
            print(f"BULK [{idx}/{len(seed_asins)}] -> {asin}")
            print("############################")

            process_seed_asin(asin, writer, processed_asins)

    print("\nDONE. Output:", OUTPUT_CSV)

if __name__ == "__main__":
    main()
