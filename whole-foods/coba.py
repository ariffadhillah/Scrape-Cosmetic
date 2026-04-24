import requests
from bs4 import BeautifulSoup
import json
import html

url = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.amazon.com/",
    "Upgrade-Insecure-Requests": "1"
}





session = requests.Session()
session.headers.update(headers)

# ⭐ paksa US locale + USD currency
session.cookies.update({
    "i18n-prefs": "USD",
    "lc-main": "en_US"
})

res = session.get(url, timeout=30)

print("STATUS:", res.status_code)

soup = BeautifulSoup(res.text, "lxml")

# 1️⃣ cari carousel dengan heading target
target_div = None

for div in soup.find_all("div", attrs={"data-carouselheadingattributesstring": True}):
    heading_json = html.unescape(div["data-carouselheadingattributesstring"])
    heading = json.loads(heading_json)

    if heading.get("headingText") == "Lunar New Year favorites":
        target_div = div
        break

if not target_div:
    print("Target section not found")
    exit()

# 2️⃣ ambil carousel options
raw = html.unescape(target_div["data-a-carousel-options"])
carousel = json.loads(raw)

# 3️⃣ ambil id_list
id_list = carousel.get("ajax", {}).get("id_list", [])

asins = []

for item in id_list:
    # item adalah STRING JSON → parse lagi
    obj = json.loads(item)
    asins.append(obj["id"])

# 4️⃣ convert ke URL
urls = [f"https://www.amazon.com/dp/{a}" for a in asins]

print("Found:", len(urls))
for u in urls:
    print(u)
