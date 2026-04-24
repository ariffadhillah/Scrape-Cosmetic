import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus

URL = "https://www.target.com/c/new-in-makeup/-/N-6n69n"

PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Accept": "text/html"
}

def build_requests_proxies(proxy_cfg):
    server = proxy_cfg["server"]
    parsed = urlparse(server)
    scheme = parsed.scheme or "http"
    hostport = parsed.netloc or parsed.path
    user = quote_plus(proxy_cfg["username"])
    pwd = quote_plus(proxy_cfg["password"])
    proxy_auth = f"{scheme}://{user}:{pwd}@{hostport}"
    return {"http": proxy_auth, "https": proxy_auth}


proxies = build_requests_proxies(PROXY)

print("Mengambil halaman...")
resp = requests.get(URL, headers=HEADERS, proxies=proxies, timeout=20)
html = resp.text

soup = BeautifulSoup(html, "html.parser")

# Cari DIV dgn data-test="lp-resultsCount"
results_div = soup.find("div", attrs={"data-module-type":"ListingPageResultsCount"})

if not results_div:
    print("⚠️ Div resultsCount tidak ditemukan!")
    print("Coba print 5000 karakter pertama HTML agar kita tahu apa yg diterima:")
    print(html)
else:
    print("✅ Ditemukan div resultsCount:")
    print(results_div.prettify())

    # Ambil teks "1,689 results"
    span = results_div.find("span")
    if span:
        text = span.get_text(strip=True)
        print("Isi span:", text)
    else:
        print("⚠️ span tidak ditemukan")
