# import requests
# import re
# import json
# import time
# import csv
# import math
# from bs4 import BeautifulSoup



# BASE_URL = "https://www.harrods.com/en-us/make-up"
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Referer": BASE_URL,
#     "Origin": BASE_URL,
#     "Connection": "keep-alive"
# }


# def get_soup(url):
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()
#         return BeautifulSoup(response.text, "html.parser")
#     except requests.RequestException as e:
#         print(f"❌ Error mengambil URL: {e}")
#         return None


# def proses_menu_url(soup):
#     full_menu = soup.find("div", id="filter-category-body")
#     if not full_menu:
#         print("Menu utama tidak ditemukan")
#         return []

#     ul_ = full_menu.find("ul")
#     li_items = ul_.find_all("li", recursive=False)
#     for list_menu in li_items:
#         a_tag = list_menu.find("a")
#         if a_tag and a_tag.get("href"):
#             url_menu = "https://www.harrods.com" + a_tag["href"]
#             text_menu = a_tag.get_text(strip=True)

#             # Pisahkan nama kategori dan jumlah item
#             if "(" in text_menu and ")" in text_menu:
#                 name_kategori, jumlah_items = text_menu.rsplit("(", 1)
#                 name_kategori = name_kategori.strip()
#                 jumlah_items = jumlah_items.strip(")")
#             else:
#                 name_kategori = text_menu.strip()
#                 jumlah_items = "0"

#             print(f"name kategori = {name_kategori}")
#             print(f"jumlah items = {jumlah_items}")
#             print(f"url = {url_menu}\n")





# def main():
#     soup = get_soup(BASE_URL)
#     if not soup:
#         return
#     proses_menu_url(soup) 

# if __name__ == "__main__":
#     main()




import requests
import re
import json
import time
import csv
import math
from bs4 import BeautifulSoup


BASE_URL = "https://www.harrods.com/en-us/make-up"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Connection": "keep-alive"
}

# === Fungsi Proxy ===
# def get_proxies():
#     username = "spju19f0x2"
#     password = "tr4ZxZo6OY4d8i_uml"
#     proxy = f"http://{username}:{password}@dc.decodo.com:10001"
#     return {
#         "http": proxy,
#         "https": proxy
#     }


# def get_soup(url):
#     try:
#         response = requests.get(
#             url,
#             headers=headers,
#             proxies=get_proxies(),  # pakai proxy di sini
#             timeout=20
#         )
#         response.raise_for_status()
#         return BeautifulSoup(response.text, "html.parser")
#     except requests.RequestException as e:
#         print(f"❌ Error mengambil URL: {e}")
#         return None

def get_soup(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"❌ Error mengambil URL: {e}")
        return None


def proses_menu_url(soup):
    full_menu = soup.find("div", id="filter-category-body")
    if not full_menu:
        print("Menu utama tidak ditemukan")
        return []

    ul_ = full_menu.find("ul")
    li_items = ul_.find_all("li", recursive=False)
    for list_menu in li_items:
        a_tag = list_menu.find("a")
        if a_tag and a_tag.get("href"):
            url_menu = "https://www.harrods.com" + a_tag["href"]
            # proses_kategory(url_menu)
            text_menu = a_tag.get_text(strip=True)

            # Pisahkan nama kategori dan jumlah item
            if "(" in text_menu and ")" in text_menu:
                name_kategori, jumlah_items = text_menu.rsplit("(", 1)
                name_kategori = name_kategori.strip()
                jumlah_items = jumlah_items.strip(")")
            else:
                name_kategori = text_menu.strip()
                jumlah_items = "0"

            print(f"name kategori = {name_kategori}")
            print(f"jumlah items = {jumlah_items}")
            print(f"url = {url_menu}\n")
            proses_kategory(url_menu)



def proses_kategory(url_menu):
    soup = get_soup(url_menu)   # ambil halaman kategori
    if not soup:
        return []

    full_kategory = soup.find("div", id="filter-category-body")
    if not full_kategory:
        print("Menu kategori tidak ditemukan")
        return []

    ul_kategory = full_kategory.find("ul")
    li_items = ul_kategory.find_all("li", recursive=False)
    for list_menu in li_items:
        a_tag = list_menu.find("a")
        if a_tag and a_tag.get("href"):
            sub_url = "https://www.harrods.com" + a_tag["href"]
            text_menu = a_tag.get_text(strip=True)

            # Pisahkan nama kategori dan jumlah item
            if "(" in text_menu and ")" in text_menu:
                name_kategori, jumlah_items = text_menu.rsplit("(", 1)
                name_kategori = name_kategori.strip()
                jumlah_items = jumlah_items.strip(")")
            else:
                name_kategori = text_menu.strip()
                jumlah_items = "0"

            print(f"name kategori items = {name_kategori}")
            print(f"jumlah items = {jumlah_items}")
            print(f"url = {sub_url}\n")


def main():
    soup = get_soup(BASE_URL)
    if not soup:
        return
    proses_menu_url(soup)


if __name__ == "__main__":
    main()
