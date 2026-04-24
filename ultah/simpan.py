import requests
import json

url = "https://www.ulta.com/dxl/graphql"

payload = {
    "operationName": "Page",
    "query": """
        query Page($url: JSON, $moduleParams: JSON) {
          Page(url: $url, moduleParams: $moduleParams) {
            content
            customResponseAttributes
            meta
            __typename
          }
        }
    """,
    "variables": {
        "url": {
            "path": "https://www.ulta.com/shop/makeup/lips?page=2"
        },
        "moduleParams": {}
    }
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "x-ulta-dxl-query-id": "Page",
    "x-ulta-client-locale": "en-US",
    "x-ulta-client-country": "US",
    "x-ulta-client-channel": "web",
    "x_ulta_site": "CA",
}

response = requests.post(url, headers=headers, json=payload)

print("Status:", response.status_code)

# --- ⬇️ SIMPAN JSON DI SINI ⬇️ ---
if response.status_code == 200:
    data = response.json()

    with open("lis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("JSON berhasil disimpan ke ulta_page.json")
else:
    print("Gagal mengambil data")
    print(response.text)
