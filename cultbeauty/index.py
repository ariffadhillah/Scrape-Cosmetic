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

    products = []
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
                    products.append({
                        "id": pid,
                        "name": item.get("item_name"),
                        "brand": item.get("brand"),
                        "price": item.get("price"),
                        "url": "https://www.cultbeauty.co.uk" + item.get("url", "")
                    })
            except Exception as e:
                print("⚠️ Error parse JSON:", e)
    return products


page = 1
while True:
    print(f"\n=== 🔎 Page {page} ===")
    products = get_products(page)
    if not products:
        print("❌ Tidak ada data lagi, stop.")
        break
    
    for p in products:
        print(p["id"], p["name"], p["price"])
    
    page += 1
