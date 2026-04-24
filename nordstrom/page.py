from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import time
import json

# --- SETUP SELENIUM + STEALTH ---
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




# --- BUKA NORDSTROM ---
print("🔄 Opening Nordstrom…")
driver.get("https://www.nordstrom.com/")
time.sleep(5)

print("🔄 Opening beauty page…")
# driver.get("https://www.nordstrom.com/s/diamond-luminous-rich-luxury-cleanse/5526385?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FSkin%20Care&color=000")
# driver.get("https://www.nordstrom.com/s/rouge-pur-couture-caring-satin-lipstick-with-ceramides/7553812?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FMakeup&color=652")
# driver.get("https://www.nordstrom.com/s/rouge-pur-couture-caring-satin-lipstick-with-ceramides/7553812?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FMakeup&color=652")
# driver.get("https://www.nordstrom.com/s/yves-saint-laurent-candy-glaze-lip-gloss-stick/6666316")
# driver.get("https://www.nordstrom.com/s/vuori-performance-joggers/5093594?origin=coordinating-5093594-0-4-Holiday_HalfYearlySale.SUB_HalfYearlySale_1-recbot-browse_results_interleave&recs_placement=Holiday_HalfYearlySale.SUB_HalfYearlySale-1&recs_strategy=browse_results_interleave&recs_source=recbot&recs_page_type=home&recs_seed=0&color=PALE%20GREY%20HEATHER")
# driver.get("https://www.nordstrom.com/s/supersonic-nural-hair-dryer/7798822?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FHair%20Care&color=650")
# driver.get("https://www.nordstrom.com/s/yves-saint-laurent-candy-glaze-lip-gloss-stick/6666316?origin=category-personalizedsort&breadcrumb=Home%2FBeauty&color=650")
# driver.get("https://www.nordstrom.com/s/holiday-2025-beauty-box-gift-set-534-value/8559125?origin=category-personalizedsort&breadcrumb=Home%2FBeauty&color=000")
# driver.get("https://www.nordstrom.com/s/oribe-conditioner-for-beautiful-color/4516681?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FHair%20Care&color=960")
# driver.get("https://www.nordstrom.com/s/special-edition-airstrait-straightener-in-amber-silk/8482558?origin=coordinating-8482558-0-6-SEEDED_SUB_1-recbot-vertex_fbt_v3&recs_placement=SEEDED_SUB-1&recs_strategy=vertex_fbt_v3&recs_source=recbot&recs_page_type=product&recs_seed=7798822&color=AMBER%20SILK")
# driver.get("https://www.nordstrom.com/s/supersonic-nural-hair-dryer/7798822?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FHair%20Care&color=650")
# driver.get("https://www.nordstrom.com/s/maison-francis-kurkdjian-paris-baccarat-rouge-540-extrait-de-parfum/5495553?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FFragrance&color=000")
# driver.get("https://www.nordstrom.com/s/v4-infrared-sauna-blanket/8448307?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FFSA%2FHSA%20Eligible%20Beauty&color=000")
driver.get("https://www.nordstrom.com/s/colorescience-sunforgettable-total-protection-face-shield-flex-spf-50/7969304?origin=category-personalizedsort&breadcrumb=Home%2FBeauty%2FSkin%20Care%2FSunscreen&color=251")
time.sleep(8)

print("✅ Page opened! You can now type commands.")
print("Command: scroll  → scroll to bottom")
print("Command: exit    → close browser")
print("")

# --- FUNGSI SCROLL ---
def auto_scroll_to_bottom():
    print("\n🌀 Scrolling…")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("✅ Done scrolling.")
            break
        last_height = new_height

def get_initial_config():
    data = driver.execute_script("""
        return window.__INITIAL_CONFIG__ || null;
    """)
    return data


print("📦 Extracting __INITIAL_CONFIG__ ...")

initial_config = driver.execute_script("""
    return window.__INITIAL_CONFIG__ || null;
""")

if initial_config:
    print("✅ __INITIAL_CONFIG__ found!")
    print(initial_config.keys())

    # simpan ke file JSON
    with open("Sunforgettable® Total Protection® Face Shield Flex SPF 50.json", "w", encoding="utf-8") as f:
    # with open("Special edition Airstrait™ straightener in Amber Silk.json", "w", encoding="utf-8") as f:
        json.dump(initial_config, f, indent=2)

    print("💾 Saved to initial_config.json")
else:
    print("❌ __INITIAL_CONFIG__ NOT found")



# --- TERMINAL COMMAND LOOP ---
while True:
    cmd = input("Command (scroll / exit): ").strip().lower()

    if cmd == "scroll":
        auto_scroll_to_bottom()

    elif cmd == "exit":
        print("🚪 Closing browser…")
        driver.quit()
        break

    else:
        print("⚠️ Unknown command. Use: scroll / exit")
