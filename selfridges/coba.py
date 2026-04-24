# # # # from playwright.sync_api import sync_playwright
# # # # from bs4 import BeautifulSoup

# # # # URL = "https://www.selfridges.com/GB/en/product/chanel-strongles-beiges-water-fresh-complexion-touchstrong-even-illuminate-hydrate-20ml_R04459609/#colour=Bo73"

# # # # def get_page():
# # # #     with sync_playwright() as p:
# # # #         browser = p.chromium.launch(headless=False)  # headless=True kalau mau tanpa UI
# # # #         context = browser.new_context(
# # # #             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
# # # #         )
# # # #         page = context.new_page()
# # # #         page.goto(URL, timeout=60000)
# # # #         page.wait_for_timeout(3000)  # tunggu 3 detik
# # # #         html = page.content()
# # # #         browser.close()
# # # #         return html

# # # # def main():
# # # #     html = get_page()
# # # #     soup = BeautifulSoup(html, "html.parser")

# # # #     title = soup.find("h1")
# # # #     if title:
# # # #         print("✅ Produk:", title.get_text(strip=True))
# # # #     else:
# # # #         print("❌ Produk tidak ditemukan")

# # # # if __name__ == "__main__":
# # # #     main()



# # # import json
# # # from playwright.sync_api import sync_playwright
# # # from bs4 import BeautifulSoup

# # # URL = "https://www.selfridges.com/GB/en/product/chanel-strongles-beiges-water-fresh-complexion-touchstrong-even-illuminate-hydrate-20ml_R04459609/#colour=Bo73"

# # # def get_page():
# # #     with sync_playwright() as p:
# # #         browser = p.chromium.launch(headless=False)
# # #         context = browser.new_context(
# # #             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
# # #         )
# # #         page = context.new_page()
# # #         page.goto(URL, timeout=90000)
# # #         page.wait_for_timeout(9000)
# # #         html = page.content()
# # #         browser.close()
# # #         return html

# # # def extract_product_data(html):
# # #     soup = BeautifulSoup(html, "html.parser")
# # #     scripts = soup.find_all("script")

# # #     for script in scripts:
# # #         if script.string and "self.__next_f.push" in script.string:
# # #             text = script.string
# # #             print(text)
# # #             # cari bagian {"productResponse": ... }
# # #             if '"productResponse":' in text:
# # #                 try:
# # #                     json_part = text.split('"productResponse":', 1)[1]
                    
# # #                     # potong di akhir objek JSON
# # #                     balance = 1
# # #                     json_str = "{"
# # #                     for ch in json_part:
# # #                         json_str += ch
# # #                         if ch == "{":
# # #                             balance += 1
# # #                         elif ch == "}":
# # #                             balance -= 1
# # #                             if balance == 0:
# # #                                 break
# # #                     data = json.loads(json_str)
# # #                     return data
# # #                 except Exception as e:
# # #                     print("❌ Gagal parsing JSON:", e)
# # #     return None

# # # def main():
# # #     html = get_page()
# # #     data = extract_product_data(html)
# # #     print(data)

# # #     # if data:
# # #     #     print("✅ Produk:", data.get("productName"))
# # #     #     print("💰 Harga:", data.get("price", {}).get("current"), data.get("price", {}).get("currency"))
# # #     #     print("🏷️ Brand:", data.get("brand", {}).get("name"))
# # #     #     print("📌 Ukuran:", data.get("sizes"))
# # #     #     print("🎨 Warna:", [c["name"] for c in data.get("colours", [])])
# # #     # else:
# # #     #     print("❌ Data produk tidak ditemukan")

# # # if __name__ == "__main__":
# # #     main()



# # import json
# # from playwright.sync_api import sync_playwright
# # from bs4 import BeautifulSoup
# # import re

# # URL = "https://www.selfridges.com/GB/en/product/chanel-strongles-beiges-water-fresh-complexion-touchstrong-even-illuminate-hydrate-20ml_R04459609/#colour=Bo73"

# # def get_page():
# #     with sync_playwright() as p:
# #         browser = p.chromium.launch(headless=False)
# #         context = browser.new_context(
# #             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
# #         )
# #         page = context.new_page()
# #         page.goto(URL, timeout=90000)
# #         page.wait_for_timeout(9000)
# #         html = page.content()
# #         browser.close()
# #         return html

# # def extract_product_data(html):
# #     soup = BeautifulSoup(html, "html.parser")
# #     scripts = soup.find_all("script")

# #     for script in scripts:
# #         if script.string and "self.__next_f.push" in script.string:
# #             # ambil teks JSON di dalam push(...)
# #             match = re.search(r"self\.__next_f\.push\(\[\d+,(.+)\]\)", script.string)
# #             if match:
# #                 raw_json = match.group(1)

# #                 # kadang perlu replace untuk jadi JSON valid
# #                 try:
# #                     data = json.loads(raw_json)
# #                     print(json.dumps(data, indent=2)[:2000])  # print potongan
# #                 except Exception as e:
# #                     print("❌ Gagal parse JSON:", e)

# # def main():
# #     html = get_page()
# #     extract_product_data(html)

# # if __name__ == "__main__":
# #     main()




# import json
# import re
# from playwright.sync_api import sync_playwright
# from bs4 import BeautifulSoup

# URL = "https://www.selfridges.com/GB/en/product/malin-goetz-essentials-kit_R03744276/"

# def get_page():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
#         )
#         page = context.new_page()
#         page.goto(URL, timeout=90000)
#         page.wait_for_timeout(9000)
#         html = page.content()
#         browser.close()
#         return html

# def extract_product_data(html):
#     soup = BeautifulSoup(html, "html.parser")
#     scripts = soup.find_all("script")

#     for script in scripts:
#         if script.string and "self.__next_f.push" in script.string and "productResponse" in script.string:
#             raw_text = script.string
#             print(raw_text)

#             # cari bagian {"productResponse": ... }
#             # match = re.search(r'(\{\\?"productResponse".*?\})\]\]\}', raw_text)
#             # # print(match)
#             # if match:
#             #     json_str = match.group(1)

#             #     # unescape string
#             #     json_str = json_str.replace('\\"', '"')

#             #     try:
#             #         data = json.loads(json_str)
#             #         product = data["productResponse"]
#             #         print("✅ Nama produk:", product.get("productName"))
#             #         print("✅ Brand:", product.get("brand", {}).get("name"))
#             #         print("✅ Harga:", product.get("price", {}).get("current"))
#             #         print("✅ Mata Uang:", product.get("price", {}).get("currency"))
#             #         print("✅ Ukuran:", product.get("sizes"))
#             #         print("✅ Warna:", [c["name"] for c in product.get("colours", [])])
#             #         return product
#             #     except Exception as e:
#             #         print("Gagal parse JSON:", e)

# html = get_page()
# extract_product_data(html)




# import re
# import json
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright

# URL = "https://www.selfridges.com/GB/en/product/chanel-strongles-beiges-water-fresh-complexion-touchstrong-even-illuminate-hydrate-20ml_R04459609/#colour=Bo73"

# def get_page():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
#         page = context.new_page()
#         page.goto(URL, timeout=90000)
#         page.wait_for_timeout(6000)
#         html = page.content()
#         browser.close()
#         return html

# def find_balanced_object_containing_key(text: str, key: str):
#     """Cari posisi key, lalu cari '{' terdekat sebelum key dan ambil object yang seimbang dari sana."""
#     pos = text.find(key)
#     if pos == -1:
#         return None
#     # cari '{' terdekat sebelum posisi key
#     start = text.rfind('{', 0, pos)
#     if start == -1:
#         start = text.find('{', pos)
#         if start == -1:
#             return None

#     depth = 0
#     for i in range(start, len(text)):
#         ch = text[i]
#         if ch == '{':
#             depth += 1
#         elif ch == '}':
#             depth -= 1
#             if depth == 0:
#                 return text[start:i+1]
#     return None

# def try_parse_json(js_text: str):
#     """Coba beberapa langkah cleaning dan parse JSON dari potongan JS/Next data."""
#     attempts = []

#     # 1) langsung coba (kemungkinan gagal karena escape)
#     attempts.append(js_text)

#     # 2) unescape unicode & backslash sequences
#     try:
#         unescaped = js_text.encode('utf-8').decode('unicode_escape')
#         attempts.append(unescaped)
#     except Exception:
#         unescaped = js_text

#     # 3) replace some JS-ish tokens (undefined) and remove trailing commas
#     cleaned = unescaped
#     cleaned = re.sub(r'\bundefined\b', 'null', cleaned)          # undefined -> null
#     cleaned = re.sub(r',\s*}', '}', cleaned)                     # trailing comma before }
#     cleaned = re.sub(r',\s*]', ']', cleaned)                     # trailing comma before ]
#     # sometimes there are "\/" sequences
#     cleaned = cleaned.replace(r'\/', '/')
#     attempts.append(cleaned)

#     last_err = None
#     for txt in attempts:
#         try:
#             return json.loads(txt)
#         except Exception as e:
#             last_err = e
#             # coba next attempt
#             continue
#     # kalau semua gagal, kembalikan error dan sample (potongan) untuk debugging
#     raise ValueError(f"JSON parse failed: {last_err}\nSample (start 200 chars):\n{js_text[:200]}")

# def extract_product_from_html(html: str):
#     soup = BeautifulSoup(html, "html.parser")
#     scripts = soup.find_all("script")

#     for script in scripts:
#         # PENTING: gunakan script.string, bukan script (Tag) atau script.strip
#         txt = script.string
#         if not txt:
#             continue
#         if "self.__next_f.push" in txt and "productResponse" in txt:
#             # Ambil object yang memuat 'productResponse'
#             obj = find_balanced_object_containing_key(txt, "productResponse")
#             if not obj:
#                 print("⚠️ Tidak menemukan object seimbang berisi productResponse (coba fallback)...")
#                 # fallback: cari dari literal '"productResponse":'
#                 pos = txt.find('"productResponse"')
#                 if pos != -1:
#                     obj = find_balanced_object_containing_key(txt[pos-200:pos+2000], "productResponse")
#             if not obj:
#                 print("❌ Gagal menemukan potongan JSON yang berisi productResponse.")
#                 continue

#             # coba parse
#             try:
#                 data = try_parse_json(obj)
#             except ValueError as e:
#                 print("❌ Gagal parse JSON dari potongan (lihat pesan di bawah):")
#                 print(e)
#                 continue

#             # data sekarang harus dictionary yang mengandung productResponse (atau data sendiri mungkin productResponse)
#             product = data.get("productResponse") if isinstance(data, dict) else None
#             if product is None and isinstance(data, dict):
#                 # mungkin object yang kita ambil *adalah* object dengan productResponse sebagai nested.
#                 # Bisa jadi productResponse sudah di dalam data (cek lagi)
#                 # jika tidak, coba cari key-level deeper
#                 # fallback: cari 'productResponse' di string form json -> parse whole cleaned object above already
#                 for v in data.values():
#                     if isinstance(v, dict) and "productName" in v:
#                         product = v
#                         break

#             if product is None:
#                 # last fallback: jika data sendiri berisi productName
#                 if isinstance(data, dict) and "productName" in data:
#                     product = data

#                     # # coba parse
#                     # try:
#                     #     data = try_parse_json(obj)
#                     #     # Tambahan: print JSON dengan indented
#                     #     print(json.dumps(data, indent=2, ensure_ascii=False))
#                     # except ValueError as e:
#                     #     print("❌ Gagal parse JSON dari potongan (lihat pesan di bawah):")
#                     #     print(e)
#                     #     continue



#             if not product:
#                 print("⚠️ Tidak dapat menemukan objek produk di dalam JSON yang di-parse.")
#                 continue

#             # Ambil field penting
#             def clean_html_snippet(s):
#                 if not s:
#                     return s
#                 # s bisa mengandung HTML entities / tags (eg <strong>...). Hapus tags sederhana:
#                 return BeautifulSoup(s, "html.parser").get_text(separator=" ", strip=True)

#             name = clean_html_snippet(product.get("productName", ""))
#             brand = product.get("brand", {}).get("name") if product.get("brand") else None
#             price = product.get("price", {}).get("current") if product.get("price") else None
#             currency = product.get("price", {}).get("currency") if product.get("price") else None
#             sizes = product.get("sizes") or []
#             colours = [c.get("name") for c in product.get("colours", [])] if product.get("colours") else []
#             images = product.get("media", {}).get("images") if product.get("media") else []

#             return {
#                 "name": name,
#                 "brand": brand,
#                 "price": price,
#                 "currency": currency,
#                 "sizes": sizes,
#                 "colours": colours,
#                 "images": images,
#             }
#     return None

# def main():
#     html = get_page()
#     prod = extract_product_from_html(html)
#     # if prod:
#     #     print("✅ Nama:", prod["name"])
#     #     print("✅ Brand:", prod["brand"])
#     #     print("✅ Harga:", prod["price"], prod["currency"])
#     #     print("✅ Sizes:", prod["sizes"])
#     #     print("✅ Colours:", prod["colours"])
#     #     print("✅ Images:", prod["images"])
#     # else:
#     #     print("❌ Produk tidak berhasil diekstrak dari halaman.")

# if __name__ == "__main__":
#     main()




import re
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# URL = "https://www.selfridges.com/GB/en/product/chanel-strongles-beiges-water-fresh-complexion-touchstrong-even-illuminate-hydrate-20ml_R04459609/#colour=Bo73"
URL = "https://www.selfridges.com/GB/en/product/victoria-beckham-beauty-colour-wash_R04509503"
# URL = 'https://www.selfridges.com/GB/en/product/malin-goetz-essentials-kit_R03744276/'
def get_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()
        page.goto(URL, timeout=90000)
        page.wait_for_timeout(6000)
        html = page.content()
        browser.close()
        return html

def find_balanced_object_containing_key(text: str, key: str):
    pos = text.find(key)
    if pos == -1:
        return None
    start = text.rfind('{', 0, pos)
    if start == -1:
        start = text.find('{', pos)
        if start == -1:
            return None

    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return None

def try_parse_json(js_text: str):
    attempts = []
    attempts.append(js_text)

    try:
        unescaped = js_text.encode('utf-8').decode('unicode_escape')
        attempts.append(unescaped)
    except Exception:
        unescaped = js_text

    cleaned = unescaped
    cleaned = re.sub(r'\bundefined\b', 'null', cleaned)
    cleaned = re.sub(r',\s*}', '}', cleaned)
    cleaned = re.sub(r',\s*]', ']', cleaned)
    cleaned = cleaned.replace(r'\/', '/')
    attempts.append(cleaned)

    last_err = None
    for txt in attempts:
        try:
            return json.loads(txt)
        except Exception as e:
            last_err = e
            continue
    raise ValueError(f"JSON parse failed: {last_err}\nSample:\n{js_text[:200]}")

def extract_product_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")

    for script in scripts:
        txt = script.string
        if not txt:
            continue
        if "self.__next_f.push" in txt and "productResponse" in txt:
            obj = find_balanced_object_containing_key(txt, "productResponse")
            if not obj:
                continue

            try:
                data = try_parse_json(obj)

                # ✅ Print JSON mentah
                print("==== RAW JSON (mentah) ====")
                print(json.dumps(data, indent=2, ensure_ascii=False))

            except ValueError as e:
                print("❌ Gagal parse JSON:", e)
                continue

            product = data.get("productResponse") if isinstance(data, dict) else None
            if not product and isinstance(data, dict) and "productName" in data:
                product = data

            if not product:
                continue

            def clean_html_snippet(s):
                if not s:
                    return s
                return BeautifulSoup(s, "html.parser").get_text(separator=" ", strip=True)

            name = clean_html_snippet(product.get("productName", ""))
            brand = product.get("brand", {}).get("name") if product.get("brand") else None
            price = product.get("price", {}).get("current") if product.get("price") else None
            currency = product.get("price", {}).get("currency") if product.get("price") else None
            sizes = product.get("sizes") or []
            colours = [c.get("name") for c in product.get("colours", [])] if product.get("colours") else []
            images = product.get("media", {}).get("images") if product.get("media") else []

            return {
                "name": name,
                "brand": brand,
                "price": price,
                "currency": currency,
                "sizes": sizes,
                "colours": colours,
                "images": images,
            }
    return None

def main():
    html = get_page()
    prod = extract_product_from_html(html)
    # if prod:
    #     print("\n==== DATA RINGKAS ====")
    #     print(json.dumps(prod, indent=2, ensure_ascii=False))
    # else:
    #     print("❌ Produk tidak berhasil diekstrak.")

if __name__ == "__main__":
    main()
