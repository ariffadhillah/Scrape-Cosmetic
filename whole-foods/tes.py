# import requests
# from bs4 import BeautifulSoup
# import re

# url = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"

# headers = {
#     "User-Agent": "Mozilla/5.0",
#     "Accept-Language": "en-US,en;q=0.9"
# }

# res = requests.get(url, headers=headers)
# soup = BeautifulSoup(res.text, "html.parser")

# product_urls = set()

# for a in soup.find_all("a", href=True):
#     href = a["href"]
#     if "/dp/" in href:
#         if href.startswith("/"):
#             href = "https://www.amazon.com" + href
#         product_urls.add(href.split("?")[0])

# print("Found:", len(product_urls))
# for u in list(product_urls)[:20]:
#     print(u)



import requests
from bs4 import BeautifulSoup

url = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

# cari h2 dengan teks target
target_h2 = None
for h2 in soup.find_all("h2"):
    if "This week's best deals" in h2.get_text(strip=True):
        target_h2 = h2
        break

if not target_h2:
    print("H2 not found")
    exit()

# cari sibling setelah h2 sampai ketemu table
table = None
for sib in target_h2.find_next_siblings():
    if sib.name == "table":
        table = sib
        break

if table:
    print(table.prettify())
else:
    print("Table not found")
