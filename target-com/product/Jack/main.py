import csv
import html
import random
import re
import time
from typing import Dict, Any, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


category = "Frozen Foods"
category_cub = "Frozen Bread & Dough"

INPUT_FILE = "tcin_.csv"
OUTPUT_FILE = f"detail-{category}-{category_cub}.csv"
ERROR_FILE = f"error{category}-{category_cub}.csv"

# ============================================================
# KONFIG
# ============================================================

PROXIES_LIST = [
    # "166.88.169.235:6842:arssrhsq:x1vpi09f4v1g",
    # "154.6.129.57:5527:arssrhsq:x1vpi09f4v1g",
    # "23.236.196.126:6216:arssrhsq:x1vpi09f4v1g",
    # "50.114.93.3:5987:arssrhsq:x1vpi09f4v1g",
    # "198.37.121.19:6439:arssrhsq:x1vpi09f4v1g",
    # "216.173.76.1:6628:arssrhsq:x1vpi09f4v1g",
    # "173.211.68.189:6471:arssrhsq:x1vpi09f4v1g",
    # "191.101.181.87:6840:arssrhsq:x1vpi09f4v1g",
    # "206.206.119.148:6059:arssrhsq:x1vpi09f4v1g",
    # "206.232.103.193:6350:arssrhsq:x1vpi09f4v1g",
    # "45.39.4.47:5472:arssrhsq:x1vpi09f4v1g",
    "23.236.182.223:5999:arssrhsq:x1vpi09f4v1g",
    "23.27.210.194:6564:arssrhsq:x1vpi09f4v1g",
    "82.26.238.173:6480:arssrhsq:x1vpi09f4v1g",
    "104.245.244.64:6504:arssrhsq:x1vpi09f4v1g",
    "192.3.48.45:6038:arssrhsq:x1vpi09f4v1g",
    "185.216.105.98:6675:arssrhsq:x1vpi09f4v1g",
    "45.59.161.140:5932:arssrhsq:x1vpi09f4v1g",
    "148.135.151.115:8366:arssrhsq:x1vpi09f4v1g",
    "23.229.125.93:5362:arssrhsq:x1vpi09f4v1g",
    "104.239.78.204:6149:arssrhsq:x1vpi09f4v1g",
    "192.3.48.38:6031:arssrhsq:x1vpi09f4v1g",
    "64.64.118.136:6719:arssrhsq:x1vpi09f4v1g",
    "23.236.255.5:6781:arssrhsq:x1vpi09f4v1g",
    "107.172.116.178:5634:arssrhsq:x1vpi09f4v1g",
    "179.61.245.31:6810:arssrhsq:x1vpi09f4v1g",
    "23.94.138.138:6412:arssrhsq:x1vpi09f4v1g",
    "216.173.76.95:6722:arssrhsq:x1vpi09f4v1g",
    "192.186.151.66:8567:arssrhsq:x1vpi09f4v1g",
    "45.41.169.251:6912:arssrhsq:x1vpi09f4v1g",
    "31.58.26.18:6601:arssrhsq:x1vpi09f4v1g"
]

API_URL = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

STORE_ID = "2250"
ZIP_CODE = "10001"
STATE = "NY"

REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_REQUESTS = 2.5
USE_PROXY_FALLBACK = True
TRY_DIRECT_FIRST = True

# Jika Anda punya nilai dari browser DevTools, isi di sini
VISITOR_ID = ""   # contoh: "0195f5c0-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Jika perlu cookie dari browser, isi di sini
# contoh:
# BROWSER_COOKIES = {
#     "visitorId": "....",
#     "te2": "....",
# }
BROWSER_COOKIES = {}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.target.com",
    "Referer": "https://www.target.com/",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

TARGET_NUTRIENTS = [
    "Calories", "Total Fat", "Saturated Fat", "Trans Fat", "Cholesterol",
    "Sodium", "Total Carbohydrate", "Dietary Fiber", "Sugars", "Added Sugars",
    "Protein", "Vitamin A", "Vitamin C", "Vitamin D", "Calcium", "Iron", "Potassium"
]


# ============================================================
# SESSION / REQUEST HELPERS
# ============================================================

def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)

    retry_strategy = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    if BROWSER_COOKIES:
        session.cookies.update(BROWSER_COOKIES)

    return session


def get_random_requests_proxy() -> Dict[str, str]:
    proxy_str = random.choice(PROXIES_LIST)
    ip, port, user, pw = proxy_str.split(":")
    proxy_url = f"http://{user}:{pw}@{ip}:{port}"
    return {"http": proxy_url, "https": proxy_url}


def build_params(tcin: str) -> Dict[str, Any]:
    params = {
        "tcin": tcin,
        "is_bot": "false",
        "pricing_store_id": STORE_ID,
        "store_id": STORE_ID,
        "has_pricing_store_id": "true",
        "scheduled_delivery_store_id": STORE_ID,
        "zip": ZIP_CODE,
        "state": STATE,
        "key": API_KEY,
    }

    if VISITOR_ID:
        params["visitor_id"] = VISITOR_ID

    return params


def summarize_response(resp: requests.Response) -> str:
    text = (resp.text or "").strip()
    if len(text) > 350:
        text = text[:350] + "..."
    return text.replace("\n", " ").replace("\r", " ")


def fetch_product_json(
    session: requests.Session,
    tcin: str,
) -> Dict[str, Any]:
    params = build_params(tcin)

    # 1) Coba direct dulu
    attempts: List[Dict[str, Any]] = []
    if TRY_DIRECT_FIRST:
        attempts.append({"name": "direct", "proxies": None})

    # 2) Kalau gagal, baru coba proxy
    if USE_PROXY_FALLBACK and PROXIES_LIST:
        for _ in range(3):
            attempts.append({"name": "proxy", "proxies": get_random_requests_proxy()})

    last_error = None

    for idx, attempt in enumerate(attempts, start=1):
        try:
            label = attempt["name"]
            proxies = attempt["proxies"]

            if proxies:
                print(f"   ↳ Attempt {idx}: pakai proxy {proxies['http'].split('@')[-1]}")
            else:
                print(f"   ↳ Attempt {idx}: direct tanpa proxy")

            response = session.get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
                proxies=proxies,
            )

            status = response.status_code
            print(f"   ↳ HTTP {status}")

            if status == 200:
                data = response.json()
                if data.get("data", {}).get("product"):
                    return data
                else:
                    last_error = f"200 OK tetapi product node kosong | body={summarize_response(response)}"
                    continue

            if status in (403, 429):
                last_error = f"{status} blocked/rate-limited | body={summarize_response(response)}"
                time.sleep(2.0)
                continue

            if status == 404:
                last_error = f"404 not found/soft-block | body={summarize_response(response)}"
                time.sleep(1.5)
                continue

            last_error = f"{status} error | body={summarize_response(response)}"

        except requests.RequestException as e:
            last_error = f"RequestException: {e}"
            time.sleep(1.5)

    raise RuntimeError(last_error or "Unknown request error")


# ============================================================
# DATA EXTRACTION
# ============================================================

def get_rating_data(node: Dict[str, Any]):
    rr = node.get("ratings_and_reviews", {}).get("statistics", {})
    raw_rating = rr.get("rating", {}).get("average")
    count = rr.get("rating", {}).get("count", "")
    return raw_rating, count


def extract_nutrients(nutrition_node: Dict[str, Any]) -> Dict[str, Any]:
    nut_dict = {
        "Serving Size": "",
        "Serving Size Unit": "",
        "Servings Per Container": ""
    }

    for name in TARGET_NUTRIENTS:
        nut_dict[f"{name} quantity"] = ""
        nut_dict[f"{name} unit"] = ""
        nut_dict[f"{name} percentage"] = ""

    prepared_list = nutrition_node.get("value_prepared_list", [])
    if prepared_list:
        p_node = prepared_list[0]

        raw_ss = p_node.get("serving_size", "")
        if raw_ss:
            try:
                if str(raw_ss).replace(".", "", 1).isdigit():
                    nut_dict["Serving Size"] = f"{float(raw_ss):g}"
                else:
                    nut_dict["Serving Size"] = raw_ss
            except Exception:
                nut_dict["Serving Size"] = raw_ss

        nut_dict["Serving Size Unit"] = p_node.get("serving_size_unit_of_measurement", "")
        nut_dict["Servings Per Container"] = p_node.get("servings_per_container", "")

        nutrients = p_node.get("nutrients", [])
        for n in nutrients:
            name = n.get("name")
            if name in TARGET_NUTRIENTS:
                raw_qty = n.get("quantity")
                if raw_qty is not None and raw_qty != "":
                    try:
                        nut_dict[f"{name} quantity"] = f"{float(raw_qty):g}"
                    except Exception:
                        nut_dict[f"{name} quantity"] = raw_qty

                nut_dict[f"{name} unit"] = n.get("unit_of_measurement", "")

                raw_pct = n.get("percentage")
                if raw_pct is not None and raw_pct != "":
                    try:
                        clean_pct = f"{float(raw_pct):g}"
                        nut_dict[f"{name} percentage"] = f"{clean_pct}%"
                    except Exception:
                        nut_dict[f"{name} percentage"] = f"{raw_pct}%"

    return nut_dict


def parse_item_data(
    node: Dict[str, Any],
    breadcrumb_path: str,
    is_variant: str = "No",
    inherited_rating=None,
    inherited_count=None
) -> Dict[str, Any]:
    item = node.get("item", {})
    enrichment = item.get("enrichment", {})
    desc = item.get("product_description", {})

    bullets_enrich = enrichment.get("product_description", {}).get("bullet_descriptions", [])
    bullets_item = desc.get("bullet_descriptions", [])
    all_bullets = bullets_enrich if bullets_enrich else bullets_item

    bullet_map = {}
    for b in all_bullets:
        clean_text = re.sub(r"<[^>]+>", "", b)
        if ":" in clean_text:
            key, val = clean_text.split(":", 1)
            bullet_map[key.strip().lower()] = val.strip()

    origin_from_handling = item.get("handling", {}).get("import_designation_description", "")
    final_origin = origin_from_handling if origin_from_handling else bullet_map.get("origin", "")

    raw_title = desc.get("title", "")
    clean_title = html.unescape(raw_title) if raw_title else ""

    raw_upc = item.get("primary_barcode", "")
    upc_formatted = f"'{raw_upc}" if raw_upc else ""

    node_rating, node_count = get_rating_data(node)
    final_rating = node_rating if node_rating else inherited_rating
    final_count = node_count if node_count else inherited_count
    rounded_rating = round(float(final_rating), 1) if final_rating not in (None, "") else ""

    base_data = {
        "Category": category,
        "Sub Category": category_cub,
        "Title": clean_title,
        "TCIN": node.get("tcin"),
        "UPC": upc_formatted,
        "DPCI": item.get("dpci"),
        "Primary Brand": item.get("primary_brand", {}).get("name"),
        "Rating": rounded_rating,
        "Total Review Count": final_count,
        "Features": bullet_map.get("features", ""),
        "Form": bullet_map.get("form", ""),
        "State of Readiness": bullet_map.get("state of readiness", ""),
        "Package Quantity": bullet_map.get("package quantity", ""),
        "Pre-package preparation": bullet_map.get("pre-package preparation", ""),
        "Net weight": bullet_map.get("net weight", ""),
        "Country of Origin": bullet_map.get("country of origin", ""),
        "Origin": final_origin,
        "Ingredients": enrichment.get("nutrition_facts", {}).get("ingredients"),
        "Allergens & Warnings": enrichment.get("nutrition_facts", {}).get("warning"),
        "Product Link": enrichment.get("buy_url"),
        "Product Image Link": enrichment.get("image_info", {}).get("primary_image", {}).get("url"),
        "Price": node.get("price", {}).get("formatted_current_price") or node.get("price", {}).get("current_retail"),
        "Breadcrumbs": breadcrumb_path,
        "Is Variant": is_variant,
    }

    nutrition_data = extract_nutrients(enrichment.get("nutrition_facts", {}))
    return {**base_data, **nutrition_data}


# ============================================================
# CSV HELPERS
# ============================================================

def read_tcin_list(input_file: str) -> List[str]:
    tcin_list = []
    with open(input_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tcin = (row.get("tcin") or "").strip()
            if tcin:
                tcin_list.append(tcin)
    return tcin_list


def write_csv(rows: List[Dict[str, Any]], output_file: str) -> None:
    if not rows:
        return

    keys = list(rows[0].keys())
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_error_csv(rows: List[Dict[str, str]], output_file: str) -> None:
    if not rows:
        return

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["tcin", "error"])
        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# MAIN
# ============================================================

def main():
    products_data: List[Dict[str, Any]] = []
    failed_tcins: List[Dict[str, str]] = []

    try:
        tcin_list = read_tcin_list(INPUT_FILE)
    except FileNotFoundError:
        print(f"❌ File {INPUT_FILE} tidak ditemukan!")
        return

    if not tcin_list:
        print("⚠️ Tidak ada TCIN yang ditemukan di file input.")
        return

    print(f"🚀 Memproses {len(tcin_list)} TCIN...")

    session = build_session()

    for i, tcin in enumerate(tcin_list, start=1):
        print(f"\n[{i}/{len(tcin_list)}] Memproses TCIN: {tcin}")

        try:
            data = fetch_product_json(session, tcin)
            product_node = data.get("data", {}).get("product")

            if not product_node:
                failed_tcins.append({"tcin": tcin, "error": "Empty product node"})
                print(f"⚠️ Data produk kosong untuk TCIN: {tcin}")
                continue

            breadcrumbs = product_node.get("category", {}).get("breadcrumbs", [])
            breadcrumb_path = " > ".join([bc.get("name", "").title() for bc in breadcrumbs])

            p_rating, p_count = get_rating_data(product_node)

            parent_info = parse_item_data(product_node, breadcrumb_path, "No", p_rating, p_count)
            products_data.append(parent_info)

            children = product_node.get("children", [])
            for child in children:
                child_info = parse_item_data(child, breadcrumb_path, "Yes", p_rating, p_count)
                products_data.append(child_info)

            print(f"✅ Berhasil: {tcin} | variants={len(children)}")
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gagal memproses {tcin}: {error_msg}")
            failed_tcins.append({"tcin": tcin, "error": error_msg})
            continue

    if products_data:
        write_csv(products_data, OUTPUT_FILE)
        print(f"\n✅ SELESAI! {len(products_data)} baris data disimpan di: {OUTPUT_FILE}")
    else:
        print("\n❌ Tidak ada data produk yang berhasil diambil.")

    if failed_tcins:
        write_error_csv(failed_tcins, ERROR_FILE)
        print(f"⚠️ {len(failed_tcins)} TCIN bermasalah dicatat di: {ERROR_FILE}")


if __name__ == "__main__":
    main()