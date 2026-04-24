import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


BASE_URL = "https://cleanlabelproject.org/certified-products/?search="


def clean_href(href: str | None) -> str | None:
    href = (href or "").strip()
    if not href or href in {"#", "javascript:void(0);", "javascript:void(0)"}:
        return None
    return href


def parse_cleanlabel_products(url: str) -> list[dict]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results: list[dict] = []

    for brand_item in soup.select("div.brand-list-item"):
        # brand
        brand_name_tag = brand_item.select_one(".brand-details-top .title-icon h2")
        brand_name = brand_name_tag.get_text(" ", strip=True) if brand_name_tag else None

        # logo
        brand_logo_tag = brand_item.select_one(".brand-logo img.brand-feature-image")
        brand_logo = brand_logo_tag.get("src", "").strip() if brand_logo_tag else None

        # show all brand page
        show_all_tag = brand_item.select_one(".award-btn a.show-all-btn")
        show_all_url = clean_href(show_all_tag.get("href")) if show_all_tag else None
        if show_all_url:
            show_all_url = urljoin(url, show_all_url)

        # products under this brand
        for product_item in brand_item.select(".brand-product-list .brand-product-list-item"):
            img_tag = product_item.select_one("img")
            title_link = product_item.select_one(".brand-product-list-head h3.title a")
            cert_link = product_item.select_one(".product-popup a[href]")

            product_name = title_link.get_text(" ", strip=True) if title_link else None
            product_url = clean_href(title_link.get("href")) if title_link else None
            certificate_url = clean_href(cert_link.get("href")) if cert_link else None

            if product_url:
                product_url = urljoin(url, product_url)
            if certificate_url:
                certificate_url = urljoin(url, certificate_url)

            image_url = img_tag.get("src", "").strip() if img_tag else None
            image_alt = img_tag.get("alt", "").strip() if img_tag else None

            results.append({
                "brand": brand_name,
                "brand_logo": brand_logo,
                "brand_page_url": show_all_url,
                "product": product_name,
                "product_url": product_url,
                "certificate_url": certificate_url,
                "image_url": image_url,
                "image_alt": image_alt,
            })

    return results


if __name__ == "__main__":
    data = parse_cleanlabel_products(BASE_URL)

    print(f"Total rows: {len(data)}")
    print(json.dumps(data[:10], indent=2, ensure_ascii=False))

    with open("cleanlabel_products.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)