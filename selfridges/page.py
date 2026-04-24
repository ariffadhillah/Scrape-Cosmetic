import requests
import re
import json
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = "https://display.powerreviews.com/m/65920584/l/en_GB/product/SDBP_810638/reviews?apikey=6abe2327-ad69-4158-93e0-a46222507896&_noconfig=true"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Connection": "keep-alive"
}


def get_soup(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"❌ Error mengambil URL: {e}")
        return None

def proses_menu_url(soup):
    """Cari kategori menu lalu proses setiap produk"""
    full_menu = soup.find("section", {"data-description": "test"})
    print(full_menu)

def main():
    soup = get_soup(BASE_URL)
    if soup:
        proses_menu_url(soup)

if __name__ == "__main__":
    main()
