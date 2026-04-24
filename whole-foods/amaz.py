# # # # # import requests
# # # # # from bs4 import BeautifulSoup
# # # # # import json
# # # # # import html

# # # # # url = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=6506977011&ref_=WF19425_1&pf_rd_r=4FPH29EG8PG5DB5CZG4B&pf_rd_p=f21d6a0a-60ce-41bc-b730-53f6a145dbea&pf_rd_m=A2R2RITDJNW1Q6&pf_rd_s=zone-7-slot-7_2&pf_rd_t=&pf_rd_i=WAYSTOSHOP"

# # # # # headers = {
# # # # #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
# # # # #     "Accept-Language": "en-US,en;q=0.9",
# # # # #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# # # # #     "Connection": "keep-alive",
# # # # #     "Referer": "https://www.amazon.com/",
# # # # #     "Upgrade-Insecure-Requests": "1"
# # # # # }

# # # # # res = requests.get(url, headers=headers, timeout=30)
# # # # # soup = BeautifulSoup(res.text, "html.parser")


# # # # # # =========================================
# # # # # # FUNCTION: GET ALL CAROUSEL ASINS
# # # # # # =========================================
# # # # # def get_carousel_asins(soup):

# # # # #     all_asins = set()

# # # # #     # cari semua element yang punya attribute ini
# # # # #     carousels = soup.select('[data-a-carousel-options]')

# # # # #     for carousel in carousels:

# # # # #         raw = carousel.get("data-a-carousel-options")
# # # # #         if not raw:
# # # # #             continue

# # # # #         try:
# # # # #             # decode &quot; → "
# # # # #             decoded = html.unescape(raw)

# # # # #             # parse JSON utama
# # # # #             data = json.loads(decoded)

# # # # #             # cek struktur ajax
# # # # #             ajax = data.get("ajax", {})

# # # # #             # id_list berisi JSON string lagi
# # # # #             id_list = ajax.get("id_list", [])

# # # # #             for item in id_list:
# # # # #                 try:
# # # # #                     obj = json.loads(item)
# # # # #                     asin = obj.get("id")
# # # # #                     if asin:
# # # # #                         all_asins.add(asin)
# # # # #                 except:
# # # # #                     pass

# # # # #         except:
# # # # #             pass

# # # # #     return list(all_asins)


# # # # # # =========================================
# # # # # # RUN
# # # # # # =========================================
# # # # # # asins = get_carousel_asins(soup)

# # # # # # print("\nFOUND ASINS:")
# # # # # # for a in asins:
# # # # # #     print(a)

# # # # # asins = get_carousel_asins(soup)

# # # # # urls = [f"https://www.amazon.com/dp/{a}" for a in asins]

# # # # # print("Total URLs ditemukan:", len(urls))

# # # # # for i, u in enumerate(urls, 1):
# # # # #     print(f"{i}. {u}")




# # # # import requests
# # # # from bs4 import BeautifulSoup
# # # # import csv

# # # # # =========================
# # # # # CONFIG
# # # # # =========================
# # # # URL = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=6506977011&ref_=WF19425_1&pf_rd_r=4FPH29EG8PG5DB5CZG4B&pf_rd_p=f21d6a0a-60ce-41bc-b730-53f6a145dbea&pf_rd_m=A2R2RITDJNW1Q6&pf_rd_s=zone-7-slot-7_2&pf_rd_t=&pf_rd_i=WAYSTOSHOP"

# # # # headers = {
# # # #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
# # # #     "Accept-Language": "en-US,en;q=0.9",
# # # #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# # # #     "Connection": "keep-alive",
# # # #     "Referer": "https://www.amazon.com/",
# # # #     "Upgrade-Insecure-Requests": "1"
# # # # }
# # # # # =========================
# # # # # REQUEST PAGE
# # # # # =========================
# # # # response = requests.get(URL, headers=headers)
# # # # soup = BeautifulSoup(response.text, "html.parser")


# # # # # =========================
# # # # # FUNCTION AMBIL CAROUSEL
# # # # # =========================
# # # # def get_carousel_categories_and_urls(soup):

# # # #     data = []

# # # #     # semua carousel Amazon
# # # #     carousels = soup.select("div.a-carousel-container")

# # # #     for carousel in carousels:

# # # #         # ======================
# # # #         # CATEGORY TITLE
# # # #         # ======================
# # # #         title_tag = carousel.select_one("h2 span")

# # # #         if not title_tag:
# # # #             continue

# # # #         category = title_tag.get_text(strip=True)

# # # #         # ======================
# # # #         # PRODUCT LINKS
# # # #         # ======================
# # # #         links = carousel.select("a.a-link-normal[href*='/dp/']")

# # # #         urls = []

# # # #         for a in links:

# # # #             href = a.get("href")
# # # #             if not href:
# # # #                 continue

# # # #             # hapus parameter tracking Amazon
# # # #             clean = href.split("?")[0]

# # # #             # jadikan absolute URL
# # # #             if not clean.startswith("http"):
# # # #                 clean = "https://www.amazon.com" + clean

# # # #             # hindari duplikat
# # # #             if clean not in urls:
# # # #                 urls.append(clean)

# # # #         if urls:
# # # #             data.append({
# # # #                 "category": category,
# # # #                 "urls": urls,
# # # #                 "total": len(urls)
# # # #             })

# # # #     return data


# # # # # =========================
# # # # # RUN SCRAPER
# # # # # =========================
# # # # carousels = get_carousel_categories_and_urls(soup)

# # # # # =========================
# # # # # PRINT RESULT
# # # # # =========================
# # # # total_all = 0

# # # # for c in carousels:
# # # #     print("\n==========================")
# # # #     print("CATEGORY :", c["category"])
# # # #     print("TOTAL URL:", c["total"])

# # # #     total_all += c["total"]

# # # #     for u in c["urls"]:
# # # #         print(u)

# # # # print("\nTOTAL SEMUA URL:", total_all)


# # # # # =========================
# # # # # SAVE CSV
# # # # # # =========================
# # # # # with open("amazon_urls.csv", "w", newline="", encoding="utf-8") as f:
# # # # #     writer = csv.writer(f)
# # # # #     writer.writerow(["Category", "URL"])

# # # # #     for c in carousels:
# # # # #         for u in c["urls"]:
# # # # #             writer.writerow([c["category"], u])

# # # # # print("\nCSV berhasil dibuat: amazon_urls.csv")




# # # import requests
# # # from bs4 import BeautifulSoup
# # # import json
# # # import html
# # # import re

# # # url = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=6506977011&ref_=WF19425_1&pf_rd_r=4FPH29EG8PG5DB5CZG4B&pf_rd_p=f21d6a0a-60ce-41bc-b730-53f6a145dbea&pf_rd_m=A2R2RITDJNW1Q6&pf_rd_s=zone-7-slot-7_2&pf_rd_t=&pf_rd_i=WAYSTOSHOP"

# # # headers = {
# # #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# # #     "Accept-Language": "en-US,en;q=0.9",
# # #     "Referer": "https://www.google.com/"
# # # }

# # # session = requests.Session()
# # # session.headers.update(headers)
# # # session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

# # # res = session.get(url, timeout=30)
# # # soup = BeautifulSoup(res.text, "html.parser")

# # # data = []

# # # # Cari semua div yang merupakan container carousel
# # # sections = soup.find_all("div", attrs={"data-carouselheadingattributesstring": True})

# # # for sec in sections:
# # #     # 1. Ambil Nama Kategori
# # #     try:
# # #         heading_info = json.loads(html.unescape(sec["data-carouselheadingattributesstring"]))
# # #         title = heading_info.get("headingText", "Unknown Category")
# # #     except:
# # #         title = "Unknown Category"

# # #     product_urls = []

# # #     # 2. Ambil produk yang SUDAH ADA di HTML (Hardcoded)
# # #     for a in sec.select("a[href*='/dp/']"):
# # #         href = a.get("href")
# # #         if href:
# # #             clean_url = "https://www.amazon.com" + href.split("?")[0] if not href.startswith("http") else href.split("?")[0]
# # #             if clean_url not in product_urls:
# # #                 product_urls.append(clean_url)

# # #     # 3. AMBIL DATA DARI CAROUSEL JSON (Ini kuncinya!)
# # #     # Kita cari atribut 'data-a-carousel-options' yang berisi daftar ASIN tersembunyi
# # #     carousel_options = sec.get("data-a-carousel-options")
# # #     if carousel_options:
# # #         try:
# # #             # Unescape dan muat JSON
# # #             js_data = json.loads(carousel_options)
# # #             ajax_ids = js_data.get("ajax", {}).get("id_list", [])
            
# # #             for item_str in ajax_ids:
# # #                 # item_str biasanya berupa string JSON lagi di dalam list
# # #                 item_data = json.loads(item_str)
# # #                 asin = item_data.get("id")
# # #                 if asin:
# # #                     # Buat URL manual berdasarkan ASIN
# # #                     full_url = f"https://www.amazon.com/dp/{asin}"
# # #                     if full_url not in product_urls:
# # #                         product_urls.append(full_url)
# # #         except Exception as e:
# # #             pass # Skip jika gagal parsing JSON tertentu

# # #     if product_urls:
# # #         data.append({
# # #             "category": title,
# # #             "urls": product_urls,
# # #             "total": len(product_urls)
# # #         })

# # # # =========================
# # # # PRINT HASIL
# # # # =========================
# # # grand_total = 0
# # # for d in data:
# # #     print(f"\nCATEGORY : {d['category']}")
# # #     print(f"TOTAL URL: {d['total']}")
# # #     grand_total += d['total']
# # #     for u in d['urls']:
# # #         print(u)

# # # print(f"\nGRAND TOTAL SEMUA URL: {grand_total}")


# # import requests
# # from bs4 import BeautifulSoup
# # import json
# # import html
# # import re

# # url = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=6506977011&ref_=WF19425_1&pf_rd_r=4FPH29EG8PG5DB5CZG4B&pf_rd_p=f21d6a0a-60ce-41bc-b730-53f6a145dbea&pf_rd_m=A2R2RITDJNW1Q6&pf_rd_s=zone-7-slot-7_2&pf_rd_t=&pf_rd_i=WAYSTOSHOP"

# # headers = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #     "Accept-Language": "en-US,en;q=0.9",
# #     "Referer": "https://www.google.com/"
# # }

# # session = requests.Session()
# # session.headers.update(headers)
# # session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

# # res = session.get(url, timeout=30)
# # soup = BeautifulSoup(res.text, "html.parser")

# # data = []

# # # Cari semua div yang merupakan container carousel
# # sections = soup.find_all("div", attrs={"data-carouselheadingattributesstring": True})

# # for sec in sections:
# #     # 1. Ambil Nama Kategori
# #     try:
# #         heading_info = json.loads(html.unescape(sec["data-carouselheadingattributesstring"]))
# #         title = heading_info.get("headingText", "Unknown Category")
# #     except:
# #         title = "Unknown Category"

# #     product_urls = []

# #     # 2. Ambil produk yang SUDAH ADA di HTML (Hardcoded)
# #     for a in sec.select("a[href*='/dp/']"):
# #         href = a.get("href")
# #         if href:
# #             clean_url = "https://www.amazon.com" + href.split("?")[0] if not href.startswith("http") else href.split("?")[0]
# #             if clean_url not in product_urls:
# #                 product_urls.append(clean_url)

# #     # 3. AMBIL DATA DARI CAROUSEL JSON (Ini kuncinya!)
# #     # Kita cari atribut 'data-a-carousel-options' yang berisi daftar ASIN tersembunyi
# #     carousel_options = sec.get("data-a-carousel-options")
# #     if carousel_options:
# #         try:
# #             # Unescape dan muat JSON
# #             js_data = json.loads(carousel_options)
# #             ajax_ids = js_data.get("ajax", {}).get("id_list", [])
            
# #             for item_str in ajax_ids:
# #                 # item_str biasanya berupa string JSON lagi di dalam list
# #                 item_data = json.loads(item_str)
# #                 asin = item_data.get("id")
# #                 if asin:
# #                     # Buat URL manual berdasarkan ASIN
# #                     full_url = f"https://www.amazon.com/dp/{asin}"
# #                     if full_url not in product_urls:
# #                         product_urls.append(full_url)
# #         except Exception as e:
# #             pass # Skip jika gagal parsing JSON tertentu

# #     if product_urls:
# #         data.append({
# #             "category": title,
# #             "urls": product_urls,
# #             "total": len(product_urls)
# #         })

# # # =========================
# # # PRINT HASIL
# # # =========================
# # grand_total = 0
# # for d in data:
# #     print(f"\nCATEGORY : {d['category']}")
# #     print(f"TOTAL URL: {d['total']}")
# #     grand_total += d['total']
# #     for u in d['urls']:
# #         print(u)

# # print(f"\nGRAND TOTAL SEMUA URL: {grand_total}")

# import requests
# from bs4 import BeautifulSoup
# import json
# import html
# import re

# url = "https://www.amazon.com/alm/category/?almBrandId=VUZHIFdob2xlIEZvb2Rz&node=6506977011&ref_=WF19425_1&pf_rd_r=4FPH29EG8PG5DB5CZG4B&pf_rd_p=f21d6a0a-60ce-41bc-b730-53f6a145dbea&pf_rd_m=A2R2RITDJNW1Q6&pf_rd_s=zone-7-slot-7_2&pf_rd_t=&pf_rd_i=WAYSTOSHOP"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Accept-Language": "en-US,en;q=0.9"
# }

# session = requests.Session()
# session.headers.update(headers)
# session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})

# res = session.get(url, timeout=30)
# soup = BeautifulSoup(res.text, "html.parser")

# data = []



# def get_reviews_count(soup):
#     el = soup.select_one("#acrCustomerReviewText")
#     if not el:
#         return None

#     text = el.get_text(strip=True)

#     # ambil angka saja
#     num = re.search(r'[\d,]+', text)
#     if not num:
#         return None

#     count = num.group(0).replace(",", "")
#     return int(count)   # return angka murni


# def get_main_image(soup):

#     img = soup.select_one("#imgTagWrapperId img")

#     if not img:
#         return None

#     # prioritas gambar resolusi tinggi
#     hires = img.get("data-old-hires")
#     if hires and hires.strip():
#         return hires.strip()

#     # fallback ke src
#     src = img.get("src")
#     if src:
#         return src.strip()

#     return None


# def get_ingredients(soup):

#     # 1️⃣ masuk ke container penting dulu
#     container = soup.find("div", id="important-information")
#     if not container:
#         return None

#     # 2️⃣ cari label Ingredients di dalam container saja
#     header = container.find(
#         "span",
#         string=lambda s: s and "ingredients" in s.lower()
#     )

#     if not header:
#         return None

#     # 3️⃣ ambil semua <p> setelah header
#     for p in header.find_all_next("p"):

#         # stop kalau sudah keluar dari container
#         if container not in p.parents:
#             break

#         text = p.get_text(strip=True)

#         # skip kosong
#         if text:
#             return text

#     return None

# def get_Legal_Disclaimer(soup):

#     # 1️⃣ masuk ke container penting dulu
#     container = soup.find("div", id="important-information")
#     if not container:
#         return None

#     # 2️⃣ cari label Ingredients di dalam container saja
#     header = container.find(
#         "span",
#         string=lambda s: s and "legal disclaimer" in s.lower()
#     )

#     if not header:
#         return None

#     # 3️⃣ ambil semua <p> setelah header
#     for p in header.find_all_next("p"):

#         # stop kalau sudah keluar dari container
#         if container not in p.parents:
#             break

#         text = p.get_text(strip=True)

#         # skip kosong
#         if text:
#             return text

#     return None

# def get_disclaimer(soup):

#     container = soup.find("div", id="storeDisclaimer_feature_div")
#     if not container:
#         return None

#     label = container.find(
#         "strong",
#         string=lambda s: s and "disclaimer" in s.lower()
#     )

#     if not label:
#         return None

#     # teks ada di parent <p>
#     p = label.find_parent("p")
#     if not p:
#         return None

#     text = p.get_text(" ", strip=True)

#     # buang kata "Disclaimer:"
#     text = text.replace("Disclaimer:", "").strip()

#     return text



# def get_detail_by_label(soup, label_text):
#     labels = soup.select("#detailBullets_feature_div .a-text-bold")

#     for lab in labels:
#         text = lab.get_text(strip=True)

#         if label_text.lower() in text.lower():

#             # ambil parent span a-list-item
#             parent = lab.find_parent("span", class_="a-list-item")

#             if parent:
#                 spans = parent.find_all("span")

#                 # value biasanya span terakhir
#                 if len(spans) >= 2:
#                     value = spans[-1].get_text(strip=True)
#                     return value

#     return None

# def get_nutrition_value(soup, label):

#     table = soup.find("table", id="nic-nutrition-facts")
#     if not table:
#         return None

#     # cari semua span yang mengandung text label
#     spans = table.find_all("span")

#     for sp in spans:
#         text = sp.get_text(strip=True)

#         # cocokkan label (exact atau contains)
#         if text.lower() == label.lower():

#             # cari sibling berikutnya yang berisi amount
#             parent = sp.find_parent("td")

#             if parent:
#                 amount = parent.find(
#                     "span",
#                     class_=lambda c: c and "nutrientAmountText" in c
#                 )

#                 if amount:
#                     return amount.get_text(strip=True)

#     return None

# def get_value_from_row_by_text(soup, row_id, label_text):
#     row = soup.find("tr", id=row_id)
#     if not row:
#         return None

#     label = row.find("span", string=lambda x: x and label_text in x)
#     if not label:
#         return None

#     value_td = label.find_parent("td").find_next_sibling("td")
#     if not value_td:
#         return None

#     return value_td.get_text(strip=True)



# def get_price(soup):

#     selectors = [
#         "#corePriceDisplay_desktop_feature_div span.a-price span.a-offscreen",
#         "#corePrice_feature_div span.a-price span.a-offscreen",
#         "#apex_desktop span.a-price span.a-offscreen",
#         "span.a-price span.a-offscreen"
#     ]

#     for sel in selectors:
#         el = soup.select_one(sel)
#         if el:
#             return el.get_text(strip=True)

#     return None



# def get_product_table_value(soup, label):

#     tables = soup.find_all("table", class_="a-normal a-spacing-micro")

#     for table in tables:
#         for row in table.find_all("tr"):

#             cells = row.find_all("td")
#             if len(cells) < 2:
#                 continue

#             name = cells[0].get_text(strip=True)
#             value = cells[1].get_text(strip=True)

#             if name.lower() == label.lower():
#                 return value

#     return None




# # Fungsi bantuan untuk mengambil ASIN dari URL atau string
# def extract_asin(text):
#     match = re.search(r"/[dp|gp/product]+ text-bold/([A-Z0-9]{10})", text)
#     if not match:
#         # Jika bukan URL, mungkin langsung ASIN (dari JSON)
#         match = re.search(r"([A-Z0-9]{10})", text)
#     return match.group(1) if match else None

# sections = soup.find_all("div", attrs={"data-carouselheadingattributesstring": True})

# for sec in sections:
#     try:
#         heading_json = html.unescape(sec["data-carouselheadingattributesstring"])
#         title = json.loads(heading_json).get("headingText", "").strip()
#     except:
#         title = "Unknown"

#     # Gunakan set untuk menyimpan ASIN unik di tiap section
#     seen_asins = set()
#     unique_urls = []

#     # 1. Cek dari tag <a> (HTML yang sudah ada)
#     for a in sec.select("a[href*='/dp/']"):
#         href = a.get("href")
#         asin = extract_asin(href)
#         if asin and asin not in seen_asins:
#             seen_asins.add(asin)
#             unique_urls.append(f"https://www.amazon.com/dp/{asin}")

#     # 2. Cek dari data carousel JSON (Hidden data)
#     carousel_options = sec.get("data-a-carousel-options")
#     if carousel_options:
#         try:
#             js_data = json.loads(carousel_options)
#             ajax_ids = js_data.get("ajax", {}).get("id_list", [])
#             for item_str in ajax_ids:
#                 item_data = json.loads(item_str)
#                 asin = item_data.get("id")
#                 if asin and asin not in seen_asins:
#                     seen_asins.add(asin)
#                     unique_urls.append(f"https://www.amazon.com/dp/{asin}")
#         except:
#             pass

#     if unique_urls:
#         data.append({
#             "category": title,
#             "urls": unique_urls,
#             "total": len(unique_urls)
#         })

# # =========================
# # PRINT RESULT
# # =========================
# grand_total = 0
# for d in data:
#     print("\n" + "="*30)
#     print(f"CATEGORY : {d['category']}")
#     print(f"TOTAL URL: {d['total']} (Unik)")
#     print("="*30)
    
#     grand_total += d['total']
#     for u in d['urls']:
#         print(u)

# print(f"\nTOTAL SEMUA URL UNIK: {grand_total}")



import requests
from bs4 import BeautifulSoup
import json
import html
import re
import time
import random

# --- KONFIGURASI ---
url_storefront = "https://www.amazon.com/alm/storefront?almBrandId=VUZHIFdob2xlIEZvb2Rz&ref=nav_cs_dsk_grfl_stfr_wf"
headers_base = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# List User-Agent agar tidak terlihat seperti satu bot yang sama
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

session = requests.Session()
session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})


def get_soup(url):
    """Fungsi pembantu untuk mengambil HTML soup dengan User-Agent acak"""
    headers = headers_base.copy()
    headers["User-Agent"] = random.choice(user_agents)
    try:
        res = session.get(url, headers=headers, timeout=20)
        if res.status_code == 200:
            return BeautifulSoup(res.text, "html.parser")
        elif res.status_code == 404:
            print(f"  [404] Product not found: {url}")
        elif res.status_code == 503:
            print("  [503] Terdeteksi Bot oleh Amazon! Berhenti sejenak...")
            time.sleep(10)
    except Exception as e:
        print(f"  Error accessing {url}: {e}")
    return None

def extract_asin(text):
    match = re.search(r"([A-Z0-9]{10})", text)
    return match.group(1) if match else None

# ==========================================
# STEP 1: AMBIL SEMUA URL UNIK TERLEBIH DAHULU
# ==========================================
print("Sedang mengambil daftar produk dari storefront...")
soup_main = get_soup(url_storefront)
if not soup_main:
    print("Gagal memuat halaman utama.")
    exit()

all_data = []
sections = soup_main.find_all("div", attrs={"data-carouselheadingattributesstring": True})

for sec in sections:
    try:
        heading_json = html.unescape(sec["data-carouselheadingattributesstring"])
        title_cat = json.loads(heading_json).get("headingText", "Unknown").strip()
    except:
        title_cat = "Unknown"

    seen_asins = set()
    urls_in_section = []

    # Ambil dari link <a>
    for a in sec.select("a[href*='/dp/']"):
        asin = extract_asin(a.get("href"))
        if asin and asin not in seen_asins:
            seen_asins.add(asin)
            urls_in_section.append(f"https://www.amazon.com/dp/{asin}")

    # Ambil dari Carousel JSON
    carousel_options = sec.get("data-a-carousel-options")
    if carousel_options:
        try:
            ajax_ids = json.loads(carousel_options).get("ajax", {}).get("id_list", [])
            for item_str in ajax_ids:
                asin = json.loads(item_str).get("id")
                if asin and asin not in seen_asins:
                    seen_asins.add(asin)
                    urls_in_section.append(f"https://www.amazon.com/dp/{asin}")
        except: pass

    if urls_in_section:
        all_data.append({"category": title_cat, "urls": urls_in_section})

# ==========================================
# STEP 2: KUNJUNGI SETIAP URL DAN AMBIL TITLE
# ==========================================
print(f"\nTotal kategori ditemukan: {len(all_data)}")
print("Memulai proses pengambilan judul produk...\n")

for item in all_data:
    print(f"\n--- CATEGORY: {item['category']} ---")
    
    for product_url in item['urls']:
        # JEDA AGAR TIDAK DIBLOKIR (1-3 detik secara acak)
        time.sleep(random.uniform(1, 3))
        
        product_soup = get_soup(product_url)
        if product_soup:
            title_tag = product_soup.select_one("#productTitle")
            if title_tag:
                product_name = title_tag.get_text(strip=True)
                print(f"TITLE: {product_name}")
                print(f"LINK : {product_url}\n")
            else:
                print(f"TITLE: Not Found (Mungkin CAPTCHA/Out of Stock)")
                print(f"LINK : {product_url}\n")