import requests

API_URL = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1"
PARAMS = {
    "tcin": "94646053",
    "is_bot": "false",
    "pricing_store_id": "3991",
    "has_pricing_store_id": "true",
    "has_financing_options": "true",
    "include_obsolete": "true",
    "skip_personalized": "true",
    "skip_variation_hierarchy": "true",
    "channel": "WEB",
    "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96"
}

PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}

# Format proxy auth untuk requests
proxy_url = f"http://{PROXY['username']}:{PROXY['password']}@{PROXY['server'].replace('http://','')}"

proxies = {
    "http": proxy_url,
    "https": proxy_url
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(API_URL, params=PARAMS, headers=headers, proxies=proxies, timeout=20)

# Cek status
print("Status:", response.status_code)

# Parse JSON
data = response.json()

print("Title:", data.get("data", {}).get("product", {}).get("item", {}).get("product_description", {}).get("title"))
