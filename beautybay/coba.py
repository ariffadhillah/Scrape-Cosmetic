import requests
import json
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.beautybay.com/",
}

def fetch_api_data(api_url):
    r = requests.get(api_url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def get_category(data):
    """Dari header 'links' versi pertama (header API), buat listing API url lalu proses tiap kategori."""
    if "links" not in data:
        print("Tidak ada key 'links' di data root.")
        return

    for item in data["links"]:
        title = (item.get("title") or "").strip()
        link = item.get("link")
        if not link:
            continue
        if title.lower() == "view all":
            continue
        # buat URL untuk memanggil listing API (jaga agar slash tidak ter-encode)
        listing_api = "https://lister-page-api.public.prd.beautybay.com/listings?pageUrl=" + urllib.parse.quote(link, safe="/:?=&")
        get_specific_category(listing_api)

def get_specific_category(listing_api_url):
    print(f"\n🔗 Fetching: {listing_api_url}")
    try:
        r = requests.get(listing_api_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data_json = r.json()
    except Exception as e:
        print(f"❌ Error fetch category: {e}")
        return None

    # debug: tunjukkan keys root dan type header kalau ada
    print("Root keys:", list(data_json.keys()))
    header = data_json.get("header") or data_json.get("headers") or data_json.get("navigation") or data_json.get("menu")
    if header is None:
        print("Tidak menemukan 'header'/'navigation' pada JSON. Periksa struktur JSON di output sebelumnya.")
        # optional: print(json.dumps(data_json, indent=2)[:2000])
        return data_json

    print("header type:", type(header))

    # helper rekursif untuk mengekstrak tuple (title, link) dari dict/list yang beraneka bentuk
    def iter_nav_items(node):
        out = []
        if isinstance(node, dict):
            # jika dict berisi list di 'links' atau 'navigation', telusuri itu
            if "links" in node and isinstance(node["links"], list):
                for it in node["links"]:
                    out.extend(iter_nav_items(it))
            elif "navigation" in node:
                out.extend(iter_nav_items(node["navigation"]))
            else:
                # mungkin node sendiri adalah item yang mengandung title/link
                title = (node.get("title") or node.get("name") or node.get("label") or "").strip()
                link = node.get("link") or node.get("url") or ""
                if title or link:
                    out.append((title, link))
        elif isinstance(node, list):
            for item in node:
                out.extend(iter_nav_items(item))
        return out

    raw_items = iter_nav_items(header)

    # dedupe & normalize, skip "View All"
    seen = set()
    results = []
    for title, link in raw_items:
        if not title and not link:
            continue
        if title.lower() == "view all":
            continue
        # normalisasi link: buat site_url (beautybay) dan listing_api jika link relative
        site_url = link
        if link.startswith("/"):
            site_url = "https://www.beautybay.com" + link
            listing_api_for_item = "https://lister-page-api.public.prd.beautybay.com/listings?pageUrl=" + urllib.parse.quote(link, safe="/:?=&")
        elif link.startswith("http"):
            listing_api_for_item = None
        else:
            # jika bentuk lain, tetap simpan as-is
            listing_api_for_item = None

        key = (title, site_url)
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "title": title,
            "site_url": site_url,
            "listing_api": listing_api_for_item
        })

    # tampilkan hasil
    if not results:
        print("Tidak menemukan item navigation yang valid.")
    else:
        for r in results:
            print(f"{r['title']} -> {r['site_url']}  (listing_api: {r['listing_api']})")

    return results

# contoh main
def main():
    # ganti API_URL sesuai yang kamu pakai untuk header
    API_URL = "https://lister-page-api.public.prd.beautybay.com/header?pageUrl=/l/makeup/?q=&preview=false&search=&locale=en-GB&bagId=r2hasbukjo-dyjig-eylnkig9yxjgmy2l3whh639j4m7yicxg1cbw"
    data = fetch_api_data(API_URL)
    get_category(data)

if __name__ == "__main__":
    main()
