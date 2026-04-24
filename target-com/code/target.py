import requests
import re
import csv
import time
from urllib.parse import urlparse, quote_plus

# ============================================================
#                     KONFIGURASI
# ============================================================

PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Accept": "application/json",
    "Referer": "https://www.target.com/",
}

NUM_PRODUCTS_TO_FETCH = 2213
REQUEST_TIMEOUT = 15
SLEEP_BETWEEN = 0.6
CSV_FILE = "Makeup Deals---.csv"


# ============================================================
#                     UTILITAS
# ============================================================

def build_proxies(cfg):
    parsed = urlparse(cfg["server"])
    scheme = parsed.scheme
    hostport = parsed.netloc

    auth = f"{quote_plus(cfg['username'])}:{quote_plus(cfg['password'])}"
    proxy_url = f"{scheme}://{auth}@{hostport}"

    return {"http": proxy_url, "https": proxy_url}


def extract_tcin(buy_url: str):
    match = re.search(r"/A-(\d+)", buy_url or "")
    return match.group(1) if match else None


# ============================================================
#                   SESSION REQUESTS
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)
session.proxies.update(build_proxies(PROXY))


# ============================================================
#               PANGGIL PLP (LISTING PAGE)
# ============================================================
# https://redsky.target.com/redsky_aggregations/v1/web/general_recommendations_placement_v1?category_id=mpo32&channel=WEB&include_sponsored_recommendations=true&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&keyword=&page=%2Fc%2Fmpo32&placement_id=plp&pricing_store_id=3991&purchasable_store_ids=&visitor_id=019A5E13904B02019657CA5992C340A5&platform=desktop

# https://redsky.target.com/redsky_aggregations/v1/web/general_recommendations_placement_v1?category_id=mpo32&channel=WEB&include_sponsored_recommendations=true&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&keyword=&page=%2Fc%2Fmpo32&placement_id=plp&pricing_store_id=3991&purchasable_store_ids=&visitor_id=019A5E13904B02019657CA5992C340A5&platform=desktop



# https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2
# ?category=mpo32&count=24&default_purchasability_filter=false&include_sponsored=true&include_review_summarization=true&offset=0 &page=%2Fc%2Fmpo32&platform=desktop &pricing_store_id=3991&spellcheck=true&visitor_id=019A5E13904B02019657CA5992C340A5 &zip=23362&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB&include_dmc_dmr=false&useragent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%3B+rv%3A144.0%29+Gecko%2F20100101+Firefox%2F144.0


# https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?category=mpo32&count=24&default_purchasability_filter=false&include_sponsored=true&include_review_summarization=true&offset=1176&page=%2Fc%2Fmpo32&platform=desktop&pricing_store_id=3991&spellcheck=true&visitor_id=019A4EE3D5E0020187C5F0E95D462CE4&zip=23362&key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB&include_dmc_dmr=false&useragent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F142.0.0.0+Safari%2F537.36+Edg%2F142.0.0.0


def fetch_plp(offset, visitor_id):
    url = (
        "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
        "?category=6n69n&count=24&default_purchasability_filter=false"
        "&include_sponsored=true&include_review_summarization=true"
        f"&offset={offset}&page=%2Fc%2Fmpo32&platform=desktop"
        "&pricing_store_id=3991&spellcheck=true"
        f"&visitor_id={visitor_id}&zip=23362"
        "&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
        "&channel=WEB&include_dmc_dmr=false"
    )
    # url = (
    #     "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
    #     "?category=6n69n&count=24&default_purchasability_filter=false"
    #     "&include_sponsored=true&include_review_summarization=true"
    #     f"&offset={offset}&page=%2Fc%2F6n69n&platform=desktop"
    #     "&pricing_store_id=3991&spellcheck=true"
    #     f"&visitor_id={visitor_id}&zip=23362"
    #     "&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
    #     "&channel=WEB&include_dmc_dmr=false"
    # )
    r = session.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


# ============================================================
#                     AMBIL DETAIL PRODUK
# ============================================================

def fetch_pdp(tcin):
    url = (
        "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
        f"?tcin={tcin}&is_bot=false&pricing_store_id=3991&has_pricing_store_id=true"
        "&has_financing_options=true&include_obsolete=true&skip_personalized=true"
        "&skip_variation_hierarchy=true&channel=WEB"
        "&key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
    )
    r = session.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


# ============================================================
#                   SIMPAN CSV
# ============================================================

def save_to_csv(rows, filename):
    header = [
        "Manufacturer","Product Name Parent", "Product Name","Category", "Product Link", "Product Image Link", "TCIN", "UPC", "Price", "Ingredients","Description" 

        # "tcin", "upc", "title", "price", "brand",
        # "breadcrumbs", "description", "ingredients",
        # "image", "product_link", "parent_title"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerow({
            k: rows[0][k] for k in header
        })
        for row in rows[1:]:
            writer.writerow(row)


# ============================================================
#                       MAIN
# ============================================================

def main():
    # visitor_id = "019A5E13904B02019657CA5992C340A5"
    visitor_id = "019A62A8EEE8020199CEE3E689734F84"
    all_rows = []
    counter = 0

    # ambil halaman pertama
    try:
        first = fetch_plp(0, visitor_id)
    except Exception as e:
        print("Gagal memuat PLP pertama:", e)
        return

    total_results = first.get("data", {}).get("search", {}).get("total_results", 2213)
    per_page = 24
    pages = (total_results + per_page - 1) // per_page

    print("Total produk:", total_results)
    print("Total halaman:", pages)

    # mulai loop per halaman
    for page in range(pages):
        if counter >= NUM_PRODUCTS_TO_FETCH:
            break

        offset = page * per_page
        print(f"\nMemuat halaman offset={offset}")

        try:
            plp = fetch_plp(offset, visitor_id)
        except Exception as e:
            print("Gagal fetch halaman:", e)
            continue

        products = plp["data"]["search"].get("products", [])

        for prod in products:
            if counter >= NUM_PRODUCTS_TO_FETCH:
                break

            buy_url = (
                prod.get("item", {}).get("enrichment", {}).get("buy_url")
                or prod.get("parent", {}).get("item", {}).get("enrichment", {}).get("buy_url")
            )
            if not buy_url:
                continue

            tcin = extract_tcin(buy_url)
            if not tcin:
                continue

            # ambil detail
            try:
                detail = fetch_pdp(tcin)
            except:
                continue

            pd = detail.get("data", {}).get("product") or {}
            item_parent = pd.get("item", {})
            enrich_parent = item_parent.get("enrichment", {})
            desc_parent = item_parent.get("product_description", {})

            parent_title = desc_parent.get("title")
            breadcrumbs = " > ".join(
                bc.get("name", "").title()
                for bc in pd.get("category", {}).get("breadcrumbs", [])
                if bc.get("name")
            )

            # jika produk punya varian
            children = pd.get("children") or []

            if children:
                for ch in children:
                    if counter >= NUM_PRODUCTS_TO_FETCH:
                        break

                    ch_item = ch.get("item", {})
                    ch_enrich = ch_item.get("enrichment", {})
                    ch_desc = ch_item.get("product_description", {})

                    row = {
                        "TCIN": ch.get("tcin"),
                        "UPC": ch_item.get("primary_barcode"),
                        "Product Name": ch_desc.get("title") or parent_title,
                        "Price": ch.get("price", {}).get("formatted_current_price"),
                        "Manufacturer": ch_item.get("primary_brand", {}).get("name"),
                        "Category": breadcrumbs,
                        "Description": ch_desc.get("downstream_description"),
                        "Ingredients": (ch_enrich.get("nutrition_facts", {}).get("ingredients") or "").lower(),
                        "Product Image Link": ch_enrich.get("image_info", {}).get("primary_image", {}).get("url"),
                        "Product Link": ch_enrich.get("buy_url") or buy_url,
                        "Product Name Parent": parent_title,
                    }

                    all_rows.append(row)
                    counter += 1
                    time.sleep(SLEEP_BETWEEN)
            else:
                row = {
                    "TCIN": tcin,
                    "UPC": item_parent.get("primary_barcode"),
                    "Product Name": parent_title,
                    "Price": pd.get("price", {}).get("formatted_current_price"),
                    "Manufacturer": item_parent.get("primary_brand", {}).get("name"),
                    "Category": breadcrumbs,
                    "Description": desc_parent.get("downstream_description"),
                    "Ingredients": (enrich_parent.get("nutrition_facts", {}).get("ingredients") or "").lower(),
                    "Product Image Link": enrich_parent.get("image_info", {}).get("primary_image", {}).get("url"),
                    "Product Link": buy_url,
                    "Product Name Parent": parent_title,
                }
                all_rows.append(row)
                counter += 1

            time.sleep(SLEEP_BETWEEN)

    # simpan CSV
    save_to_csv(all_rows, CSV_FILE)
    print("\n✅ CSV disimpan sebagai:", CSV_FILE)


if __name__ == "__main__":
    main()
