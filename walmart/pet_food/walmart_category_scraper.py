# walmart_category_scraper.py

import requests
import json
from bs4 import BeautifulSoup
import time
import csv



HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/143.0.0.0 Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;'
        'q=0.9,image/webp,image/apng,*/*;q=0.8'
    ),
    'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
}


def ambil_semua_url_produk_kategori(category_url):
    """
    Mengambil daftar URL produk dari JSON-LD (ItemList) di halaman kategori Walmart
    """
    print(f"\n🔎 Memindai halaman kategori:")
    print(category_url)

    try:
        response = requests.get(category_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        product_urls = set()

        # Cari semua JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)

                # Kadang berupa list
                if isinstance(data, list):
                    for item in data:
                        _extract_itemlist(item, product_urls)
                else:
                    _extract_itemlist(data, product_urls)

            except (json.JSONDecodeError, TypeError):
                continue

        print(f"\n✅ Total URL produk ditemukan: {len(product_urls)}")
        return list(product_urls)

    except Exception as e:
        print(f"❌ Error saat scanning kategori: {e}")
        return []


def _extract_itemlist(data, product_urls):
    """
    Helper internal untuk ekstrak ItemList
    """
    if not isinstance(data, dict):
        return

    # Format umum Walmart
    main_entity = data.get('mainEntity')
    if not isinstance(main_entity, dict):
        return

    item_list = main_entity.get('itemListElement')
    if not isinstance(item_list, list):
        return

    for item in item_list:
        url = item.get('url')
        if url:
            clean_url = url.split('?')[0]
            # print(clean_url)
            product_urls.add(clean_url)

save_file = 'Url-Perfume for Women.csv'

if __name__ == "__main__":
    # URL Dasar (Base URL) tanpa parameter page
    BASE_URL = "https://www.walmart.com/browse/beauty/perfume-for-women/1085666_133225_4659649"
    # https://www.walmart.com/browse/beauty/perfume-for-women/1085666_133225_4659649?povid=Beauty_NUPs_WomensFragranceByBrand_Shopallfragrance&seo=beauty&seo=perfume-for-women&seo=1085666_133225_4659649&page=2&affinityOverride=default
    PARAMS = "povid=Beauty_NUPs_WomensFragranceByBrand_Shopallfragrance&seo=beauty&seo=perfume-for-women&seo=1085666_133225_4659649"
    
    semua_produk = set()
    MAX_PAGES = 13

    for page_num in range(1, MAX_PAGES + 1):
        # Membuat URL dinamis untuk setiap halaman
        # Halaman 1 biasanya bisa diakses dengan page=1
        page_url = f"{BASE_URL}?{PARAMS}&page={page_num}"
        


    # BASE_URL = "https://www.walmart.com/search"
    # PARAMS = "q=pet+food&affinityOverride=store_led"


    for page_num in range(3, MAX_PAGES + 1):
        page_url = f"{BASE_URL}?{PARAMS}&page={page_num}"



        print(f"\n🚀 MEMPROSES HALAMAN {page_num} DARI {MAX_PAGES}")
        
        # Panggil fungsi scraper yang sudah Anda buat berhasil tadi
        urls = ambil_semua_url_produk_kategori(page_url)

        if not urls:
            print(f"⚠️ Peringatan: Tidak ditemukan produk di halaman {page_num}. Berhenti atau lanjut?")
            # Jika ingin berhenti saat halaman kosong, aktifkan 'break'
            # break 
        
        semua_produk.update(urls)

        # Jeda waktu agar tidak diblokir (Sangat disarankan minimal 5-10 detik)
        print(f"⏳ Jeda keamanan... (Total terkumpul: {len(semua_produk)} URL)")
        time.sleep(10)

    print(f"\n🏁 SELESAI!")
    print(f"TOTAL SELURUH PRODUK UNIK DARI {MAX_PAGES} HALAMAN: {len(semua_produk)}")

    # Simpan hasil ke file teks agar tidak hilang
    with open(save_file, "w") as f:
        for url in semua_produk:
            f.write(url + "\n")
    print(f"💾 Semua URL telah disimpan ke '{save_file}'")






# import requests
# import json
# from bs4 import BeautifulSoup
# import time

# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
#     ),
#     "Accept-Language": "en-US,en;q=0.9",
#     "Referer": "https://www.walmart.com/",
#     "Connection": "keep-alive"
# }


# # ===============================
# # JSON-LD parser (browse category)
# # ===============================
# def ekstrak_jsonld(soup):
#     urls = set()

#     for script in soup.find_all("script", type="application/ld+json"):
#         try:
#             data = json.loads(script.string)

#             if isinstance(data, list):
#                 iterable = data
#             else:
#                 iterable = [data]

#             for item in iterable:
#                 main = item.get("mainEntity", {})
#                 items = main.get("itemListElement", [])

#                 for x in items:
#                     url = x.get("url")
#                     if url:
#                         urls.add(url.split("?")[0])

#         except Exception:
#             pass

#     return urls


# # ===============================
# # NEXT_DATA parser (search page)
# # ===============================
# def ekstrak_nextdata(soup):
#     urls = set()

#     script = soup.find("script", id="__NEXT_DATA__")
#     if not script:
#         return urls

#     try:
#         data = json.loads(script.string)

#         stacks = (
#             data["props"]["pageProps"]
#             ["initialData"]["searchResult"]
#             ["itemStacks"]
#         )

#         for stack in stacks:
#             for item in stack.get("items", []):

#                 url = item.get("canonicalUrl")

#                 if url:
#                     urls.add("https://www.walmart.com" + url)

#     except Exception:
#         pass

#     return urls


# # ===============================
# # MAIN SCRAPER PER PAGE
# # ===============================
# def ambil_semua_url_produk_kategori(url):
#     print("\n🔎 Memindai halaman:")
#     print(url)

#     try:
#         r = requests.get(url, headers=HEADERS, timeout=30)
#         r.raise_for_status()

#         html_size = len(r.text)
#         print(f"📦 HTML size: {html_size}")

#         soup = BeautifulSoup(r.text, "html.parser")

#         # 1️⃣ coba JSON-LD dulu
#         urls = ekstrak_jsonld(soup)

#         # 2️⃣ kalau kosong → coba NEXT_DATA
#         if not urls:
#             print("ℹ️ JSON-LD kosong, mencoba NEXT_DATA...")
#             urls = ekstrak_nextdata(soup)

#         print(f"✅ Total URL produk ditemukan: {len(urls)}")

#         return urls

#     except Exception as e:
#         print("❌ ERROR:", e)
#         return set()


# # ===============================
# # RUN
# # ===============================
# if __name__ == "__main__":

#     # SEARCH TARGET
#     BASE_URL = "https://www.walmart.com/search"
#     QUERY = "pet food"

#     MAX_PAGES = 13
#     semua_produk = set()

#     for page in range(3, MAX_PAGES + 13):

#         params = {
#             "q": QUERY,
#             "page": page,
#             "affinityOverride": "store_led"
#         }

#         url = requests.Request("GET", BASE_URL, params=params).prepare().url

#         print(f"\n🚀 MEMPROSES HALAMAN {page}/{MAX_PAGES}")

#         urls = ambil_semua_url_produk_kategori(url)

#         if not urls:
#             print("⚠️ Tidak ada produk ditemukan di halaman ini")

#         semua_produk.update(urls)

#         print(f"📊 TOTAL TERKUMPUL: {len(semua_produk)}")

#         time.sleep(5)

#     # ===============================
#     # SAVE FILE
#     # ===============================
#     save_file = "walmart_pet_food_urls-2.txt"

#     with open(save_file, "w", encoding="utf-8") as f:
#         for u in semua_produk:
#             f.write(u + "\n")

#     print("\n🏁 SELESAI")
#     print("💾 Disimpan ke:", save_file)
#     print("TOTAL PRODUK:", len(semua_produk))
