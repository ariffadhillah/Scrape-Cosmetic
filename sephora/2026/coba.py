import requests
import json
from bs4 import BeautifulSoup

slug = "foundation-makeup"

base_url = (
    f"https://www.sephora.com/api/v2/catalog/"
    f"categories/{slug}/seo"
)

params = {
    "targetSearchEngine": "NLP",
    "currentPage": 1,
    "pageSize": 1,
    "content": "true",
    "includeRegionsMap": "true",
    "pickupRampup": "true",
    "sddRampup": "true",
    "includeEDD": "true",
    "loc": "en-US",
    "ch": "rwd",
}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,image/webp,"
        "*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.sephora.com/",
    "Connection": "keep-alive",
}


session = requests.Session()
session.headers.update(headers)


# ============================================================
# 1. CATEGORY API
# ============================================================

print("📥 Mengambil category API...")

response = session.get(
    base_url,
    params=params,
    timeout=60,
)

print("Category status:", response.status_code)

print(
    "Category URL:",
    response.url
)

if response.status_code != 200:
    print(response.text[:1000])
    raise SystemExit


data = response.json()

products = data.get("products", [])

print(
    f"Products ditemukan: {len(products)}"
)


# ============================================================
# 2. PRODUCT
# ============================================================

for product in products:

    product_url = product.get("targetUrl")

    if not product_url:
        continue

    detail_url = (
        "https://www.sephora.com"
        + product_url
    )

    print()
    print("=" * 70)
    print("🔗 PRODUCT")
    print(detail_url)
    print("=" * 70)

    try:

        res = session.get(
            detail_url,
            timeout=60,
            allow_redirects=True,
        )

        print(
            "Product status:",
            res.status_code
        )

        print(
            "Final URL:",
            res.url
        )

        print(
            "Content-Type:",
            res.headers.get("content-type")
        )

        print(
            "Response length:",
            len(res.content)
        )

        print(
            "Server:",
            res.headers.get("server")
        )

        print(
            "CF-Ray:",
            res.headers.get("cf-ray")
        )

        print(
            "Location:",
            res.headers.get("location")
        )

        # ----------------------------------------------------
        # Save response untuk debugging
        # ----------------------------------------------------

        with open(
            "product_response.html",
            "wb"
        ) as f:
            f.write(res.content)

        print(
            "💾 Response disimpan ke "
            "'product_response.html'"
        )

        # ----------------------------------------------------
        # Parse HTML
        # ----------------------------------------------------

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        script_tag = soup.find(
            "script",
            {
                "id": "linkStore",
                "type": "text/json"
            }
        )

        if script_tag:

            print(
                "✅ #linkStore ditemukan!"
            )

            if script_tag.string:

                data_json = json.loads(
                    script_tag.string
                )

                with open(
                    "sample_product.json",
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        data_json,
                        f,
                        indent=4,
                        ensure_ascii=False
                    )

                print(
                    "✅ JSON disimpan ke "
                    "'sample_product.json'"
                )

        else:

            print(
                "❌ #linkStore tidak ditemukan."
            )

            print(
                "\nResponse awal:"
            )

            print(
                res.text[:2000]
            )

    except Exception as e:

        print(
            "❌ ERROR:",
            repr(e)
        )