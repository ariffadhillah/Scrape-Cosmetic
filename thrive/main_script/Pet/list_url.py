from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

name_url = "Pet Care"
tambah_url = 'https://thrivemarket.com/c/pet-care'
savecsv = f'{name_url}'

# --- KONFIGURASI ---
proxy_host = "191.96.254.80"
proxy_port = "6127"
proxy_user = "arssrhsq"
proxy_pass = "x1vpi09f4v1g"

proxy_options = {
    'proxy': {
        'http': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
        'https': f'https://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
        'no_proxy': 'localhost,127.0.0.1'
    }
}

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


all_product_urls = []
base_url = f"{tambah_url}?cur_page="

# Tentukan ingin scrape sampai halaman berapa (misal 1 sampai 5)
start_page = 1
end_page = 200

try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        seleniumwire_options=proxy_options,
        options=options
    )

    for page_num in range(start_page, end_page + 1):
        print(f"\n--- Mengambil Halaman {page_num} ---")
        current_url = f"{base_url}{page_num}"
        driver.get(current_url)

        # 1. Tunggu dan Hapus Popup (Hanya perlu sekali, tapi aman dijalankan setiap page)
        time.sleep(7)
        driver.execute_script("""
            var backdrop = document.querySelector('[data-testid="modal_backdrop"]');
            if (backdrop) { backdrop.parentElement.remove(); }
            document.body.style.overflow = 'auto';
            document.body.style.position = 'static';
            document.documentElement.style.overflow = 'auto';
        """)

        # 2. Tunggu Grid Produk Muncul
        try:
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="ProductGrid"]')))
            
            # 3. Auto-Scroll agar semua produk di halaman tersebut termuat
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 3000);")
            time.sleep(2)

            # 4. Ambil URL Produk
            links = driver.find_elements(By.CSS_SELECTOR, '[data-testid="ProductGrid"] a[href*="/p/"]')
            
            count_before = len(all_product_urls)
            for link in links:
                href = link.get_attribute('href')
                if href and href not in all_product_urls:
                    all_product_urls.append(href)
            
            new_links = len(all_product_urls) - count_before
            print(f"Ditemukan {new_links} URL baru di halaman {page_num}.")

            # Jika tidak ada produk baru sama sekali, mungkin halaman sudah habis
            if new_links == 0 and page_num > 1:
                print("Tidak ada produk lagi. Berhenti...")
                break

        except Exception as e:
            print(f"Gagal memuat halaman {page_num}: {e}")
            continue

    # 5. Simpan Hasil Akhir
    print(f"\nSelesai! Total URL terkumpul: {len(all_product_urls)}")
    with open(f"{savecsv}.csv", "w") as f:
        for p_url in all_product_urls:
            f.write(p_url + "\n")
    print(f"Semua data disimpan di {savecsv}.csv")

except Exception as e:
    print(f"Error utama: {e}")
finally:
    driver.quit()