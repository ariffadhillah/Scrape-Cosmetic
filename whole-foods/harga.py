# # import requests
# # import re
# # import random
# # import time

# # def get_price_from_twister_ajax(variant_asin, parent_asin, session):
# #     """
# #     Mengambil harga dari endpoint Twister Dimension Slots (AJAX).
# #     """
# #     # Gunakan URL yang Anda temukan
# #     url = "https://www.amazon.com/gp/product/ajax/twisterDimensionSlotsDefault"
    
# #     params = {
# #         "isDimensionSlotsAjax": "1",
# #         "asinList": variant_asin, # Bisa diisi list ASIN dipisahkan koma
# #         "asin": variant_asin,
# #         "parentAsin": parent_asin,
# #         "productTypeDefinition": "SAUCE",
# #         "productGroupId": "grocery_display_on_website",
# #         "twisterFlavor": "twisterPlusDesktopConfigurator",
# #         "deviceType": "web",
# #         "showFancyPrice": "false"
# #     }

# #     headers = {
# #         "accept": "text/html,*/*",
# #         "x-requested-with": "XMLHttpRequest",
# #         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
# #         "referer": f"https://www.amazon.com/dp/{variant_asin}"
# #     }

# #     try:
# #         # Jeda sebentar agar tidak agresif
# #         time.sleep(random.uniform(1, 2))
# #         res = session.get(url, params=params, headers=headers, timeout=30)
        
# #         if res.status_code == 200:
# #             html_content = res.text
            
# #             # Cara 1: Sniper menggunakan class yang Anda temukan di awal
# #             # Mencari nilai di dalam a-offscreen yang berada di dekat apex-pricetopay-value
# #             price_match = re.search(r'apex-pricetopay-value.*?a-offscreen">(\$[\d\.]+)<', html_content, re.DOTALL)
# #             if price_match:
# #                 return price_match.group(1)
            
# #             # Cara 2: Mencari a-offscreen secara umum di dalam respon
# #             offscreen_match = re.search(r'class="a-offscreen">(\$[\d\.]+)<', html_content)
# #             if offscreen_match:
# #                 return offscreen_match.group(1)
            
# #             # Cara 3: Regex mentah untuk angka harga jika class berubah
# #             raw_price = re.search(r'\$\d+\.\d{2}', html_content)
# #             if raw_price:
# #                 return raw_price.group(0)

# #     except Exception as e:
# #         print(f"Error pada ASIN {variant_asin}: {e}")
    
# #     return "Price Not Found"

# # # --- INTEGRASI KE LOOP UTAMA ---
# # def main():
# #     session = requests.Session()
# #     # Simulasikan cookie agar dikenali sebagai user USA
# #     session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
    
# #     parent_asin = "B0G4F1LXVC"
# #     variant_list = ["B09XJ9HSRQ", "B0B781T4C8", "B0FQFKZQB5"] # Masukkan semua varian hasil scraping awal

# #     for v_asin in variant_list:
# #         print(f"Mengambil harga untuk {v_asin}...")
# #         price = get_price_from_twister_ajax(v_asin, parent_asin, session)
# #         print(f"HASIL: {v_asin} -> {price}")
# #         print("-" * 30)

# # if __name__ == "__main__":
# #     main()



# import requests
# from bs4 import BeautifulSoup
# import json
# import re
# import time
# import random

# # --- KONFIGURASI ---
# TARGET_ASIN = "B09DS5J8F9" 
# BASE_URL = "https://www.amazon.com/dp/"
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
# ]

# def get_headers(referer=None):
#     headers = {
#         "authority": "www.amazon.com",
#         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
#         "accept-language": "en-US,en;q=0.9",
#         "user-agent": random.choice(USER_AGENTS),
#         "x-requested-with": "XMLHttpRequest"
#     }
#     if referer:
#         headers["referer"] = referer
#     return headers

# def get_parent_asin(soup):
#     """Mencari Parent ASIN dari script atau hidden input"""
#     # Coba dari input hidden
#     parent_el = soup.find("input", {"id": "parent_asin"})
#     if parent_el: return parent_el.get("value")
    
#     # Coba dari script colorToAsin
#     script_text = str(soup.find_all("script"))
#     match = re.search(r'"parentAsin"\s*:\s*"([^"]+)"', script_text)
#     if match: return match.group(1)
    
#     return None

# def get_price_via_ajax(variant_asin, parent_asin, session):
#     url = "https://www.amazon.com/gp/product/ajax/twisterDimensionSlotsDefault"
#     params = {
#         "isDimensionSlotsAjax": "1",
#         "asinList": variant_asin,
#         "asin": variant_asin,
#         "parentAsin": parent_asin,
#         "productTypeDefinition": "SAUCE",
#         "productGroupId": "grocery_display_on_website",
#         "twisterFlavor": "twisterPlusDesktopConfigurator",
#         "deviceType": "web"
#     }
    
#     try:
#         time.sleep(random.uniform(1.5, 2.5))
#         res = session.get(url, params=params, headers=get_headers(f"{BASE_URL}{variant_asin}"), timeout=20)
        
#         if res.status_code == 200:
#             # Amazon memisahkan beberapa objek JSON dengan '&&&'
#             chunks = res.text.split("&&&")
            
#             for chunk in chunks:
#                 chunk = chunk.strip()
#                 if not chunk: continue
                
#                 try:
#                     data = json.loads(chunk)
                    
#                     # VALIDASI: Pastikan ASIN di JSON ini cocok dengan yang kita cari
#                     if data.get("ASIN") == variant_asin:
                        
#                         # PRIORITAS 1: Ambil langsung dari field 'price' di twisterSlotJson
#                         # Berdasarkan response Anda, ini adalah data paling akurat ($10.09)
#                         content = data.get("Value", {}).get("content", {})
#                         price_val = content.get("twisterSlotJson", {}).get("price")
                        
#                         if price_val:
#                             return f"${price_val}"
                        
#                         # PRIORITAS 2: Jika field price kosong, cari di dalam HTML twisterSlotDiv
#                         html_div = content.get("twisterSlotDiv", "")
#                         if html_div:
#                             # Cari harga yang ada di dalam class 'apex-pricetopay-value'
#                             # Kita cari pola $ angka di dalam aria-hidden="true"
#                             m = re.search(r'apex-pricetopay-value.*?aria-hidden="true">\$([\d\.]+)<', html_div, re.DOTALL)
#                             if m:
#                                 return f"${m.group(1)}"
                                
#                 except json.JSONDecodeError:
#                     continue
                    
#     except Exception as e:
#         print(f"      [!] Error detail: {e}")
        
#     return "Price Not Found"



# def get_variants(soup):
#     """Mengambil daftar semua ASIN varian"""
#     asins = set()
#     script_content = str(soup.find_all("script"))
#     matches = re.findall(r'"([A-Z0-9]{10})"', script_content)
#     # Filter ASIN yang valid (Amazon ASIN biasanya mulai dengan B)
#     for m in matches:
#         if m.startswith("B"): asins.add(m)
#     return list(asins)

# def main():
#     session = requests.Session()
#     session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
    
#     print(f"[*] Memulai crawling produk utama: {TARGET_ASIN}")
#     res = session.get(f"{BASE_URL}{TARGET_ASIN}", headers=get_headers())
#     if res.status_code != 200:
#         print("[-] Gagal akses Amazon. Coba ganti koneksi/IP.")
#         return

#     soup = BeautifulSoup(res.text, "html.parser")
#     parent_asin = get_parent_asin(soup) or TARGET_ASIN
#     variant_list = get_variants(soup)
    
#     if not variant_list: variant_list = [TARGET_ASIN]
    
#     print(f"[*] Parent ASIN Terdeteksi: {parent_asin}")
#     print(f"[*] Ditemukan {len(variant_list)} varian.\n")

#     # for i, v_asin in enumerate(variant_list):
#     #     print(f"[{i+1}/{len(variant_list)}] Memproses: {v_asin}")
        
#     #     # 1. Ambil Nama (dari halaman standar)
#     #     v_res = session.get(f"{BASE_URL}{v_asin}", headers=get_headers())
#     #     v_soup = BeautifulSoup(v_res.text, "html.parser")
#     #     title = v_soup.select_one("#productTitle")
#     #     name = title.get_text(strip=True)[:50] if title else "Unknown Name"
        
#     #     # 2. Ambil Harga (dari AJAX)
#     #     price = get_price_via_ajax(v_asin, parent_asin, session)
        
#     #     # 3. Ambil Kalori (Regex sederhana)
#     #     cal_match = re.search(r'Calories\s*(\d+)', v_res.text)
#     #     calories = cal_match.group(1) if cal_match else "N/A"

#     #     print(f"      NAME     : {name}...")
#     #     print(f"      PRICE    : {price}")
#     #     print(f"      CALORIES : {calories}")
#     #     print("-" * 50)


#     for i, v_asin in enumerate(variant_list):
#         print(f"[{i+1}/{len(variant_list)}] Memproses: {v_asin}")
        
#         # Buat URL produk yang bersih
#         product_url = f"https://www.amazon.com/dp/{v_asin}"
        
#         # 1. Ambil Nama & Kalori (dari halaman standar)
#         v_res = session.get(product_url, headers=get_headers())
#         v_soup = BeautifulSoup(v_res.text, "html.parser")
        
#         title = v_soup.select_one("#productTitle")
#         name = title.get_text(strip=True)[:50] if title else "Unknown Name"
        
#         # 2. Ambil Harga (dari AJAX sakti)
#         price = get_price_via_ajax(v_asin, parent_asin, session)
        
#         # 3. Ambil Kalori
#         cal_match = re.search(r'Calories\s*(\d+)', v_res.text)
#         calories = cal_match.group(1) if cal_match else "N/A"

#         # --- TAMPILAN OUTPUT ---
#         print(f"      ASIN     : {v_asin}")
#         print(f"      NAME     : {name}...")
#         print(f"      PRICE    : {price}")
#         print(f"      CALORIES : {calories}")
#         print(f"      URL      : {product_url}")
#         print("-" * 60)

# if __name__ == "__main__":
#     main()


import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random

# --- KONFIGURASI ---
TARGET_ASIN = "B09V3LWGWX" 
BASE_URL = "https://www.amazon.com/dp/"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def get_headers(referer=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://www.amazon.com/",
        "Upgrade-Insecure-Requests": "1"
    }
    if referer:
        headers["referer"] = referer
    return headers

def get_parent_asin(soup):
    """Mencari Parent ASIN untuk keperluan AJAX"""
    parent_el = soup.find("input", {"id": "parent_asin"})
    if parent_el: return parent_el.get("value")
    
    script_text = str(soup.find_all("script"))
    match = re.search(r'"parentAsin"\s*:\s*"([^"]+)"', script_text)
    return match.group(1) if match else None

def get_price_via_ajax(variant_asin, parent_asin, session):
    """Mengambil harga langsung dari JSON response (High Accuracy)"""
    url = "https://www.amazon.com/gp/product/ajax/twisterDimensionSlotsDefault"
    params = {
        "isDimensionSlotsAjax": "1",
        "asinList": variant_asin,
        "asin": variant_asin,
        "parentAsin": parent_asin,
        "productTypeDefinition": "SAUCE",
        "productGroupId": "grocery_display_on_website",
        "twisterFlavor": "twisterPlusDesktopConfigurator",
        "deviceType": "web"
    }
    
    try:
        # Jeda random agar tidak terdeteksi bot
        time.sleep(random.uniform(1.0, 2.0))
        res = session.get(url, params=params, headers=get_headers(f"{BASE_URL}{variant_asin}"), timeout=20)
        
        if res.status_code == 200:
            # Amazon memisahkan beberapa objek JSON dengan '&&&'
            chunks = res.text.split("&&&")
            
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk: continue
                
                try:
                    data = json.loads(chunk)
                    
                    # Cek jika ASIN sesuai
                    if data.get("ASIN") == variant_asin:
                        content = data.get("Value", {}).get("content", {})
                        
                        # PRIORITAS 1: Harga Mentah (Angka langsung) - Ini yang menghasilkan $10.09
                        price_val = content.get("twisterSlotJson", {}).get("price")
                        if price_val:
                            return f"${price_val}"
                        
                        # PRIORITAS 2: Parsing dari HTML Slot (Jika JSON price kosong)
                        html_div = content.get("twisterSlotDiv", "")
                        if html_div:
                            # Mencari di dalam apex-pricetopay-value
                            m = re.search(r'apex-pricetopay-value.*?aria-hidden="true">\$([\d\.]+)<', html_div, re.DOTALL)
                            if m: return f"${m.group(1)}"
                            
                            # Fallback: a-offscreen standar
                            m2 = re.search(r'class="a-offscreen">\$([\d\.]+)<', html_div)
                            if m2: return f"${m2.group(1)}"
                except:
                    continue
    except Exception as e:
        return f"Error: {str(e)[:20]}"
        
    return "Price Not Found"

def get_variants(soup):
    """Mencari daftar ASIN varian dalam satu halaman"""
    asins = set()
    script_content = str(soup.find_all("script"))
    matches = re.findall(r'"([A-Z0-9]{10})"', script_content)
    for m in matches:
        if m.startswith("B"): 
            asins.add(m)
    return list(asins)

def main():
    session = requests.Session()
    # Setting wajib agar Amazon menampilkan harga USD/USA
    session.cookies.update({"i18n-prefs": "USD", "lc-main": "en_US"})
    
    print(f"[*] Menghubungi Amazon untuk produk: {TARGET_ASIN}...")
    try:
        res = session.get(f"{BASE_URL}{TARGET_ASIN}", headers=get_headers())
        if res.status_code != 200:
            print(f"[-] Gagal akses (Status: {res.status_code}). Gunakan VPN/Proxy.")
            return

        soup = BeautifulSoup(res.text, "html.parser")
        parent_asin = get_parent_asin(soup) or TARGET_ASIN
        variant_list = get_variants(soup)
        
        if not variant_list: 
            variant_list = [TARGET_ASIN]
            
        print(f"[*] Parent ASIN  : {parent_asin}")
        print(f"[*] Total Varian : {len(variant_list)}\n")
        print("="*65)

        for i, v_asin in enumerate(variant_list):
            print(f"[{i+1}/{len(variant_list)}] Sedang memproses ASIN: {v_asin}")
            
            product_url = f"{BASE_URL}{v_asin}"
            
            # 1. Ambil Halaman Varian (untuk Nama & Kalori)
            # v_res = session.get(product_url, headers=get_headers())
            # v_soup = BeautifulSoup(v_res.text, "html.parser")
            
            # Nama Produk
            # title_el = v_soup.select_one("#productTitle")
            # name = title_el.get_text(strip=True)[:60] if title_el else "Nama tidak ditemukan"
            
            # Kalori (Regex dinamis)
            # cal_match = re.search(r'Calories\s*(\d+)', v_res.text, re.IGNORECASE)
            # calories = cal_match.group(1) if cal_match else "N/A"
            
            # 2. Ambil Harga (via AJAX sakti)
            # price = get_price_via_ajax(v_asin, parent_asin, session)

            # --- OUTPUT ---
            # print(f"      NAME     : {name}...")
            # print(f"      PRICE    : {price}")
            # print(f"      CALORIES : {calories}")
            # print(f"      URL      : {product_url}")
            # print("-" * 65)



            print("PRICE:", price)
            print("Product Name:", product_name)
            print("Product_url:", product_url)
            print("Package Dimensions:", package_Dimensions)
            print("UPC:", upc)
            print("Manufacturer:", manufacturer)
            print("ASIN:", asin_val)
            print("Units:", units)

            print("Serving Size:", serving_size)
            print("Calories:", calories)

            print("Total Fat:", get_nutrition_value(soup, "Total Fat"))
            print("Saturated Fat:", get_nutrition_value(soup, "Saturated Fat"))
            print("Monounsaturated Fat:", get_nutrition_value(soup, "Monounsaturated Fat"))
            print("Polyunsaturated Fat:", get_nutrition_value(soup, "Polyunsaturated Fat"))
            print("Cholesterol:", get_nutrition_value(soup, "Cholesterol"))
            print("Sodium:", get_nutrition_value(soup, "Sodium"))
            print("Total Carbohydrate:", get_nutrition_value(soup, "Total Carbohydrate"))
            print("Dietary Fiber:", get_nutrition_value(soup, "Dietary Fiber"))
            print("Soluble Fiber:", get_nutrition_value(soup, "Soluble Fiber"))
            print("Insoluble Fiber:", get_nutrition_value(soup, "Insoluble Fiber"))
            print("Sugars:", get_nutrition_value(soup, "Sugars"))
            print("Added Sugars:", get_nutrition_value(soup, "Added Sugars"))
            print("Starch:", get_nutrition_value(soup, "Starch"))
            print("Other Carbohydrate:", get_nutrition_value(soup, "Other Carbohydrate"))
            print("Sugar Alcohol:", get_nutrition_value(soup, "Sugar Alcohol"))
            print("Protein:", get_nutrition_value(soup, "Protein"))
            print("Vitamin A:", get_nutrition_value(soup, "Vitamin A"))
            print("Vitamin C:", get_nutrition_value(soup, "Vitamin C"))
            print("Calcium:", get_nutrition_value(soup, "Calcium"))
            print("Iron:", get_nutrition_value(soup, "Iron"))


            print("Brand:", get_product_table_value(soup, "Brand"))
            print("Item Weight:", get_product_table_value(soup, "Item Weight"))
            print("Specialty:", get_product_table_value(soup, "Specialty"))
            print("Temperature Condition:", get_product_table_value(soup, "Temperature Condition"))
            print("Number of Pieces:", get_product_table_value(soup, "Number of Pieces"))
            print("Region of Origin:", get_product_table_value(soup, "Region of Origin"))
            print("Cuisine:", get_product_table_value(soup, "Cuisine"))
            print("Variety:", get_product_table_value(soup, "Variety"))
            print("Number of Items:", get_product_table_value(soup, "Number of Items"))
            print("Size:", get_product_table_value(soup, "Size"))

            print("Flavor:", get_product_table_value(soup, "Flavor"))
            print("Produce sold as:", get_product_table_value(soup, "Produce sold as"))
            print("Item Form:", get_product_table_value(soup, "Item Form"))

            print("INGREDIENTS:", ingredients)
            print("LEGAL DISCLAIMER:", legal_disclaimer)
            print("DISCLAIMER:", disclaimer)
            print("Product Description:", product_description)
            print("IMAGE:", image_url)





    except Exception as e:
        print(f"[!] Terjadi kesalahan sistem: {e}")

if __name__ == "__main__":
    main()