import requests
from bs4 import BeautifulSoup

base_url = "https://www.contentbeautywellbeing.com/collections/natural-and-organic-skincare?page="

for page in range(1, 5):  # 1-4 sesuai jumlah halaman
    url = f"{base_url}{page}"
    print(f"Scraping: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Contoh ambil semua link produk
    products = soup.select(".product-card a")
    for p in products:
        print(p.get("href"))
