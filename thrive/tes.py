# # import requests

# # # Konfigurasi Proxy Anda
# # proxy_host = "191.96.254.80"
# # proxy_port = "6127"
# # proxy_user = "arssrhsq"
# # proxy_pass = "x1vpi09f4v1g"

# # # Format proxy dengan autentikasi
# # proxies = {
# #     "http": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
# #     "https": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
# # }

# # # URL asli (disarankan pakai domain langsung jika menggunakan proxy US)
# # url = "https://thrivemarket.com/api/v1/products?filter%5Bcategories%5D=1682&filter%5Bcategory_url_key%5D=soups-meals-sides&cur_page=3&page_size=60&multifilter=1&display_mode=grid&page_view_id=7b9ed97f-e72c-44fc-a334-28e6de78320e&page_type=category"

# # headers = {
# #     'accept': 'application/json, text/plain, */*',
# #     'accept-language': 'en-US,en;q=0.9',
# #     'referer': 'https://thrivemarket.com/c/soups-meals-sides?cur_page=3',
# #     'reqsource': 'web',
# #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
# #     # Note: Token WAF dan Cookie mungkin perlu diperbarui secara berkala
# # }

# # try:
# #     # Menambahkan parameter proxies dan verify=True (atau False jika ada masalah SSL)
# #     response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
    
# #     print(f"Status Code: {response.status_code}")
# #     print(response.text)
# # except requests.exceptions.RequestException as e:
# #     print(f"Error: {e}")


# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# # Konfigurasi Proxy Anda
# proxy_host = "191.96.254.80"
# proxy_port = "6127"
# proxy_user = "arssrhsq"
# proxy_pass = "x1vpi09f4v1g"

# # Format proxy untuk selenium-wire
# proxy_options = {
#     'proxy': {
#         'http': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
#         'https': f'https://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
#         'no_proxy': 'localhost,127.0.0.1'
#     }
# }

# # Opsi Chrome (Opsional: untuk menyamarkan bot)
# options = webdriver.ChromeOptions()
# # options.add_argument('--headless') # Buka komentar jika ingin berjalan di belakang layar
# options.add_argument('--start-maximized')
# options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# try:
#     # Inisialisasi WebDriver dengan selenium-wire
#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         seleniumwire_options=proxy_options,
#         options=options
#     )

#     print("Membuka halaman Thrive Market...")
#     url = "https://thrivemarket.com/c/poultry"
#     driver.get(url)

#     # Tunggu beberapa detik untuk memastikan halaman dimuat
#     time.sleep(10) 

#     # Ambil judul halaman sebagai bukti berhasil masuk
#     print(f"Judul Halaman: {driver.title}")
    
#     # Anda bisa menambahkan kode scraping di sini (misal: driver.page_source)

# except Exception as e:
#     print(f"Terjadi kesalahan: {e}")

# finally:
#     # Jangan langsung ditutup agar bisa melihat hasilnya
#     input("Tekan Enter untuk menutup browser...")
#     driver.quit()


from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Konfigurasi Proxy Anda
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

try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        seleniumwire_options=proxy_options,
        options=options
    )

    print("Membuka halaman Thrive Market...")
    url = "https://thrivemarket.com/p/badger-kids-sunscreen-cream-spf-40"
    driver.get(url)

    # Tunggu popup muncul (biasanya 5-8 detik)
    print("Menunggu popup muncul...")
    time.sleep(10) 

    # --- BAGIAN PENGHILANG POPUP & AKTIVASI SCROLL ---
    print("Mencoba menghilangkan popup dan mengaktifkan scroll...")
    driver.execute_script("""
        // 1. Cari elemen backdrop berdasarkan data-testid yang Anda temukan
        var backdrop = document.querySelector('[data-testid="modal_backdrop"]');
        
        if (backdrop) {
            // Hapus parent dari backdrop (biasanya ini adalah kontainer utama modal)
            backdrop.parentElement.remove();
            console.log('Modal removed');
        }

        // 2. Paksa body dan html untuk bisa di-scroll kembali
        // Kita hapus overflow: hidden dan position: fixed yang sering dipasang modal
        document.body.style.overflow = 'auto';
        document.body.style.position = 'static';
        document.documentElement.style.overflow = 'auto';
        
        // Opsional: Hapus class-class yang mungkin mengunci scroll
        document.body.className = ''; 
    """)

    print(f"Judul Halaman: {driver.title}")
    print("Sekarang Anda seharusnya sudah bisa men-scroll halaman.")

    # Contoh mencoba scroll ke bawah untuk membuktikan sudah aktif
    driver.execute_script("window.scrollBy(0, 500);")
    
except Exception as e:
    print(f"Terjadi kesalahan: {e}")

finally:
    input("Tekan Enter untuk menutup browser...")
    driver.quit()