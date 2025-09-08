import requests, re, json
from bs4 import BeautifulSoup

BASE_URL = "https://www.cultbeauty.co.uk/c/make-up/complexion/?pageNumber={}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

def get_products(page):
    url = BASE_URL.format(page)
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    scripts = soup.find_all("script", string=re.compile("trackingObj"))

    # products = []
    for script in scripts:
        text = script.string
        if not text:
            continue
        match = re.search(r'const\s+trackingObj\s*=\s*(\{.*?\})\s*;', text, re.S)
        if match:
            raw_json = match.group(1)
            try:
                data = json.loads(raw_json)
                for pid, item in data.items():
                    url_items = item.get("url", "")
                    print(url_items)
                    # products.append({
                    #     "id": pid,
                    #     "name": item.get("item_name"),
                    #     "brand": item.get("brand"),
                    #     "price": item.get("price"),
                    #     "url": "https://www.cultbeauty.co.uk" + item.get("url", "")
                    # })
            except Exception as e:
                print("⚠️ Error parse JSON:", e)
    # return products


# ✅ Test hanya untuk 1 halaman
page = 1
products = get_products(page)
print(f"=== 🔎 Page {page} | Total produk: {len(products)} ===")
for p in products:
    print(p["url"])
