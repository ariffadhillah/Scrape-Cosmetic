import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth


# =========================
# PARSER (REUSABLE)
# =========================
def extract_skus_from_styles(data):
    results = []

    selling = data.get("sellingEssentials", {})
    styles_by_id = selling.get("stylesById", {})

    for style_id, style in styles_by_id.items():
        product_name = style.get("productName") or style.get("productTitle")

        skus_by_id = style.get("skus", {}).get("byId", {})

        for sku_id, sku in skus_by_id.items():
            results.append({
                "product_name": product_name,
                "style_id": style_id,
                "sku_id": sku_id,
                "rmsSkuId": sku.get("rmsSkuId"),
                "color": sku.get("colorDisplayValue"),
                "size": sku.get("sizeDisplayValue"),
                "qty": sku.get("totalQuantityAvailable"),
                "isAvailable": sku.get("isAvailable"),
                "isShipAvailable": sku.get("isShipAvailable"),
            })

    return results


# def parse_initial_config(data):
#     sku_data = extract_skus_from_styles(data)

#     if not sku_data:
#         print("⚠️ No SKU data found")
#         return

#     for item in sku_data:
#         print("─────────────────────────")
#         print(f"Product Name : {item['product_name']}")
#         print(f"Style ID     : {item['style_id']}")
#         print(f"SKU ID       : {item['sku_id']}")
#         print(f"rmsSkuId     : {item['rmsSkuId']}")
#         print(f"Color        : {item['color']}")
#         print(f"Size         : {item['size']}")
#         print(f"Qty Avail    : {item['qty']}")
#         print(f"Available    : {item['isAvailable']}")
#         print(f"Ship Avail   : {item['isShipAvailable']}")

# def extract_skus_with_images(data):
#     results = []

#     # Ambil Data Style dari sellingEssentials
#     selling = data.get("sellingEssentials", {})
#     styles_by_id = selling.get("stylesById", {})

#     for style_id, style in styles_by_id.items():
#         # --- PERUBAHAN DI SINI: Ambil mediaExperiences dari DALAM style ---
#         media = style.get("mediaExperiences", {}) 
#         carousels = media.get("carouselsByColor", [])
        
#         # Buat dictionary pencarian warna untuk style saat ini
#         color_image_map = {}
#         for entry in carousels:
#             # Contoh: "RICH DEEP"
#             color_name = entry.get("colorName", "").strip().upper()
#             shots = entry.get("orderedShots", [])
#             if shots:
#                 # Ambil URL gambar pertama
#                 color_image_map[color_name] = shots[0].get("url")

#         # Ambil nama produk dan SKU
#         product_name = style.get("productName") or style.get("productTitle")
#         skus_by_id = style.get("skus", {}).get("byId", {})

#         for sku_id, sku in skus_by_id.items():
#             # Cocokkan warna SKU dengan map gambar
#             color_val = sku.get("colorDisplayValue", "").strip().upper()
#             image_url = color_image_map.get(color_val, "No Image Found")

#             results.append({
#                 "product_name": product_name,
#                 "style_id": style_id,
#                 "sku_id": sku_id,
#                 "rmsSkuId": sku.get("rmsSkuId"),
#                 "color": sku.get("colorDisplayValue"),
#                 "size": sku.get("sizeDisplayValue"),
#                 "qty": sku.get("totalQuantityAvailable"),
#                 "isAvailable": sku.get("isAvailable"),
#                 "image_url": image_url
#             })

#     return results

# def extract_skus_with_images(data):
#     results = []

#     # Ambil Data Style dari sellingEssentials
#     selling = data.get("sellingEssentials", {})
#     styles_by_id = selling.get("stylesById", {})

#     for style_id, style in styles_by_id.items():
#         # 1. Ambil Brand Name
#         # Lokasi: style -> brand -> brandName
#         brand_info = style.get("brand", {})
#         brand_name = brand_info.get("brandName", "No Brand")

#         # 2. Ambil mediaExperiences dari dalam style untuk mapping gambar
#         media = style.get("mediaExperiences", {}) 
#         carousels = media.get("carouselsByColor", [])
        
#         color_image_map = {}
#         for entry in carousels:
#             color_name = entry.get("colorName", "").strip().upper()
#             shots = entry.get("orderedShots", [])
#             if shots:
#                 color_image_map[color_name] = shots[0].get("url")

#         # 3. Ambil data produk dan SKU
#         product_name = style.get("productName") or style.get("productTitle")
#         skus_by_id = style.get("skus", {}).get("byId", {})

#         for sku_id, sku in skus_by_id.items():
#             color_val = sku.get("colorDisplayValue", "").strip().upper()
#             image_url = color_image_map.get(color_val, "No Image Found")

#             results.append({
#                 "brand_name": brand_name,       # <--- Brand Name ditambahkan di sini
#                 "product_name": product_name,
#                 "style_id": style_id,
#                 "sku_id": sku_id,
#                 "rmsSkuId": sku.get("rmsSkuId"),
#                 "color": sku.get("colorDisplayValue"),
#                 "size": sku.get("sizeDisplayValue"),
#                 "qty": sku.get("totalQuantityAvailable"),
#                 "isAvailable": sku.get("isAvailable"),
#                 "image_url": image_url
#             })

#     return results


# def extract_skus_with_images(data):
#     results = []

#     # Ambil Data Style dari sellingEssentials
#     selling = data.get("sellingEssentials", {})
#     styles_by_id = selling.get("stylesById", {})

#     for style_id, style in styles_by_id.items():
#         # 1. Ambil Brand Name
#         brand_info = style.get("brand", {})
#         brand_name = brand_info.get("brandName", "No Brand")

#         # 2. Ambil Review dan Rating (Baru)
#         # Lokasi: style -> reviews
#         review_data = style.get("reviews", {})
#         avg_rating = review_data.get("averageRating", 0)
#         num_reviews = review_data.get("numberOfReviews", 0)

#         # 3. Ambil mediaExperiences dari dalam style untuk mapping gambar
#         media = style.get("mediaExperiences", {}) 
#         carousels = media.get("carouselsByColor", [])
        
#         color_image_map = {}
#         for entry in carousels:
#             color_name = entry.get("colorName", "").strip().upper()
#             shots = entry.get("orderedShots", [])
#             if shots:
#                 color_image_map[color_name] = shots[0].get("url")

#         # 4. Ambil data produk dan SKU
#         product_name = style.get("productName") or style.get("productTitle")
#         skus_by_id = style.get("skus", {}).get("byId", {})

#         for sku_id, sku in skus_by_id.items():
#             color_val = sku.get("colorDisplayValue", "").strip().upper()
#             image_url = color_image_map.get(color_val, "No Image Found")

#             results.append({
#                 "brand_name": brand_name,
#                 "product_name": product_name,
#                 "average_rating": avg_rating,    # <--- Tambah ke hasil
#                 "review_count": num_reviews,     # <--- Tambah ke hasil
#                 "style_id": style_id,
#                 "sku_id": sku_id,
#                 "rmsSkuId": sku.get("rmsSkuId"),
#                 "color": sku.get("colorDisplayValue"),
#                 "size": sku.get("sizeDisplayValue"),
#                 "qty": sku.get("totalQuantityAvailable"),
#                 "isAvailable": sku.get("isAvailable"),
#                 "image_url": image_url
#             })

#     return results


def extract_skus_with_images(data):
    results = []

    # 1. Ambil Ingredients dari root -> viewData
    # Kita ambil sekali saja di luar loop karena biasanya berlaku untuk satu produk
    view_data = data.get("viewData", {})
    ingredients_text = view_data.get("ingredients", "No ingredients found")

    # Ambil Data Style dari sellingEssentials
    selling = data.get("sellingEssentials", {})
    styles_by_id = selling.get("stylesById", {})

    for style_id, style in styles_by_id.items():
        # 2. Ambil Brand Name
        brand_info = style.get("brand", {})
        brand_name = brand_info.get("brandName", "No Brand")

        # 3. Ambil Review dan Rating
        review_data = style.get("reviews", {})
        avg_rating = review_data.get("averageRating", 0)
        num_reviews = review_data.get("numberOfReviews", 0)

        # 4. Ambil mediaExperiences untuk mapping gambar per warna
        media = style.get("mediaExperiences", {}) 
        carousels = media.get("carouselsByColor", [])
        
        color_image_map = {}
        for entry in carousels:
            color_name = entry.get("colorName", "").strip().upper()
            shots = entry.get("orderedShots", [])
            if shots:
                color_image_map[color_name] = shots[0].get("url")

        # 5. Ambil data produk dan SKU
        product_name = style.get("productName") or style.get("productTitle")
        skus_by_id = style.get("skus", {}).get("byId", {})

        for sku_id, sku in skus_by_id.items():
            color_val = sku.get("colorDisplayValue", "").strip().upper()
            image_url = color_image_map.get(color_val, "No Image Found")

            results.append({
                "brand_name": brand_name,
                "product_name": product_name,
                "average_rating": avg_rating,
                "review_count": num_reviews,
                "ingredients": ingredients_text,  # <--- Tambahkan Ingredients
                "style_id": style_id,
                "sku_id": sku_id,
                "rmsSkuId": sku.get("rmsSkuId"),
                "color": sku.get("colorDisplayValue"),
                "size": sku.get("sizeDisplayValue"),
                "qty": sku.get("totalQuantityAvailable"),
                "isAvailable": sku.get("isAvailable"),
                "image_url": image_url,
                
            })

    return results

def parse_initial_config(data):
    sku_data = extract_skus_with_images(data)

    if not sku_data:
        print("⚠️ No SKU data found")
        return

    for item in sku_data:
        print("─────────────────────────")
        print(f"Brand        : {item['brand_name']}")
        print(f"Product Name : {item['product_name']}")
        print(f"Style ID     : {item['style_id']}")
        print(f"SKU ID       : {item['sku_id']}")
        print(f"rmsSkuId     : {item['rmsSkuId']}")
        print(f"Color        : {item['color']}")
        print(f"Size         : {item['size']}")
        print(f"Qty Avail    : {item['qty']}")
        print(f"Image URL    : {item['image_url']}") # <--- Output gambar
        print(f"Rating       : ⭐ {item['average_rating']}") # Tampilkan rating
        print(f"Rating       : ⭐ ({item['review_count']} reviews)") # Tampilkan rating
        print(f"Ingredients  : {item['ingredients']}...")

# =========================
# SELENIUM + STEALTH SETUP
# =========================
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--lang=en-US,en")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

# =========================
# TARGET PRODUCT URL
# =========================
# PRODUCT_URL = "https://www.nordstrom.com/s/volo-hero-hair-towel/7255856?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FHair%20Care&color=020"
PRODUCT_URL = "https://www.nordstrom.com/s/rouge-pur-couture-caring-satin-lipstick-with-ceramides/7553812?origin=coordinating-7553812-0-4-FTR-recbot-recently_viewed_snowplow_mvp&recs_placement=FTR&recs_strategy=recently_viewed_snowplow_mvp&recs_source=recbot&recs_page_type=category&recs_seed=0&color=N1%20BEIGE%20TRENCH"
# PRODUCT_URL = "https://www.nordstrom.com/s/diamond-luminous-rich-luxury-cleanse/5526385?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FSkin%20Care&color=000"
# PRODUCT_URL = "https://www.nordstrom.com/s/oribe-conditioner-for-beautiful-color/4516681?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FHair%20Care&color=960"
# PRODUCT_URL = "https://www.nordstrom.com/s/colorescience-sunforgettable-total-protection-face-shield-flex-spf-50/7969304"

print("🔄 Opening Nordstrom homepage...")
driver.get("https://www.nordstrom.com/")
time.sleep(4)

print("🔄 Opening product page...")
driver.get(PRODUCT_URL)
time.sleep(8)

# =========================
# EXTRACT __INITIAL_CONFIG__
# =========================
print("📦 Extracting __INITIAL_CONFIG__ ...")

initial_config = driver.execute_script("""
    return window.__INITIAL_CONFIG__ || null;
""")

if not initial_config:
    print("❌ __INITIAL_CONFIG__ NOT found")
else:
    print("✅ __INITIAL_CONFIG__ found!")
    print("🔑 Root keys:", initial_config.keys())

    print("\n📊 Parsing SKU data...\n")
    parse_initial_config(initial_config)


# =========================
# COMMAND LOOP
# =========================
def auto_scroll():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


print("\nCommands:")
print("  scroll → scroll page")
print("  exit   → close browser\n")

while True:
    cmd = input("Command: ").strip().lower()

    if cmd == "scroll":
        auto_scroll()
        print("✅ Scrolled")
    elif cmd == "exit":
        print("🚪 Closing browser…")
        driver.quit()
        break
    else:
        print("⚠️ Unknown command")
