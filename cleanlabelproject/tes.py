from __future__ import annotations

import csv
import os
import re
import time
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


START_URL = "https://cleanlabelproject.org/certified-products/"
OUTPUT_DIR = Path("output_cleanlabel")
CSV_PATH = OUTPUT_DIR / "cleanlabel_products.csv"
JSON_PATH = OUTPUT_DIR / "cleanlabel_products.json"
CERTS_DIR = OUTPUT_DIR / "cleanlabelproject-pdf"


# ============================================================
# UTILITIES
# ============================================================

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"[\\/:*?\"<>|]+", "_", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or "unknown"


def clean_href(href: Optional[str]) -> Optional[str]:
    href = (href or "").strip()
    if href in {"", "#", "javascript:void(0);", "javascript:void(0)"}:
        return None
    return href


def filename_from_url(url: str, default: str = "certificate.pdf") -> str:
    path = urlparse(url).path
    name = os.path.basename(path).strip()

    if not name:
        return default

    name = unquote(name)
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    return name or default


# ============================================================
# SELENIUM SETUP
# ============================================================

def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    return driver


# ============================================================
# PARSER
# ============================================================

def parse_page(html: str, base_url: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    for brand_item in soup.select("div.brand-list-item"):
        brand_name = brand_item.select_one(".title-icon h2")
        brand_name = brand_name.get_text(strip=True) if brand_name else None

        for product_item in brand_item.select(".brand-product-list-item"):
            title_link = product_item.select_one("h3.title a")
            cert_link = product_item.select_one(".product-popup a[href]")

            product_name = title_link.get_text(strip=True) if title_link else None
            product_url = clean_href(title_link.get("href")) if title_link else None
            certificate_url = clean_href(cert_link.get("href")) if cert_link else None

            if product_url:
                product_url = urljoin(base_url, product_url)
            if certificate_url:
                certificate_url = urljoin(base_url, certificate_url)

            rows.append({
                "brand": brand_name,
                "product": product_name,
                "product_url": product_url,
                "certificate_url": certificate_url,
            })

    return rows


# ============================================================
# PAGINATION
# ============================================================

def click_all_if_possible(driver):
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='All']"))
        )
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)
        return True
    except:
        return False


def click_next(driver):
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "#pagination #next")
        classes = next_btn.get_attribute("class")

        if "disabled" in classes:
            return False

        old = driver.find_elements(By.CSS_SELECTOR, ".brand-list-item h2")[0].text

        driver.execute_script("arguments[0].click();", next_btn)

        WebDriverWait(driver, 50).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, ".brand-list-item h2")[0].text != old
        )

        time.sleep(2)
        return True
    except:
        return False


def scrape_all(driver):
    driver.get(START_URL)
    WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".brand-list-item"))
    )

    all_rows = []
    seen = set()

    if click_all_if_possible(driver):
        rows = parse_page(driver.page_source, START_URL)
        for r in rows:
            key = (r["brand"], r["product"], r["certificate_url"])
            if key not in seen:
                seen.add(key)
                all_rows.append(r)
        return all_rows

    # fallback pagination
    while True:
        rows = parse_page(driver.page_source, START_URL)

        for r in rows:
            key = (r["brand"], r["product"], r["certificate_url"])
            if key not in seen:
                seen.add(key)
                all_rows.append(r)

        if not click_next(driver):
            break

    return all_rows


# ============================================================
# DOWNLOAD CERTIFICATE (FIXED NAME)
# ============================================================

# def download_certificates(rows):
#     ensure_dir(CERTS_DIR)

#     session = requests.Session()
#     session.headers.update({
#         "User-Agent": "Mozilla/5.0"
#     })

#     cache = {}

#     for i, row in enumerate(rows, 1):
#         brand = sanitize_filename(row["brand"] or "unknown")
#         cert_url = row["certificate_url"]

#         row["certificate_local_path"] = ""
#         row["certificate_downloaded"] = False

#         if not cert_url:
#             continue

#         # reuse kalau sudah pernah download
#         if cert_url in cache:
#             row["certificate_local_path"] = cache[cert_url]
#             row["certificate_downloaded"] = True
#             continue

#         brand_dir = CERTS_DIR / brand
#         ensure_dir(brand_dir)

#         # 🔥 FIX DI SINI: pakai nama asli dari URL
#         filename = filename_from_url(cert_url)
#         path = brand_dir / filename

#         print(f"[DOWNLOAD] {i}/{len(rows)} - {brand} - {filename}")

#         try:
#             r = session.get(cert_url, stream=True, timeout=60)
#             r.raise_for_status()

#             with open(path, "wb") as f:
#                 for chunk in r.iter_content(1024 * 128):
#                     if chunk:
#                         f.write(chunk)

#             local_path = str(path.as_posix())
#             cache[cert_url] = local_path

#             row["certificate_local_path"] = local_path
#             row["certificate_downloaded"] = True

#         except Exception as e:
#             print("ERROR:", e)

#     return rows

def download_certificates(rows):
    ensure_dir(CERTS_DIR)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    cache = {}

    for i, row in enumerate(rows, 1):
        brand = sanitize_filename(row["brand"] or "unknown")
        cert_url = row["certificate_url"]

        row["certificate_local_path"] = ""
        row["certificate_downloaded"] = False

        if not cert_url:
            continue

        # reuse kalau sudah pernah download
        if cert_url in cache:
            row["certificate_local_path"] = cache[cert_url]
            row["certificate_downloaded"] = True
            continue

        brand_dir = CERTS_DIR / brand
        ensure_dir(brand_dir)

        filename = filename_from_url(cert_url)
        path = brand_dir / filename

        print(f"[DOWNLOAD] {i}/{len(rows)} - {brand} - {filename}")

        try:
            r = session.get(cert_url, stream=True, timeout=60)
            r.raise_for_status()

            with open(path, "wb") as f:
                for chunk in r.iter_content(1024 * 128):
                    if chunk:
                        f.write(chunk)

            # ✅ SIMPAN HANYA NAMA FILE
            cache[cert_url] = filename

            row["certificate_local_path"] = filename
            row["certificate_downloaded"] = True

        except Exception as e:
            print("ERROR:", e)

    return rows

# ============================================================
# SAVE
# ============================================================

def save_csv(rows):
    ensure_dir(OUTPUT_DIR)

    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def save_json(rows):
    ensure_dir(OUTPUT_DIR)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


# ============================================================
# MAIN
# ============================================================

def main():
    ensure_dir(OUTPUT_DIR)

    driver = build_driver()

    try:
        rows = scrape_all(driver)
    finally:
        driver.quit()

    print("Total data:", len(rows))

    rows = download_certificates(rows)

    save_csv(rows)
    save_json(rows)

    print("DONE ✅")


if __name__ == "__main__":
    main()