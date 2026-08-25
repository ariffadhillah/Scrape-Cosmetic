import time
# PENTING: Kita mengimpor uc dari seleniumwire, BUKAN dari undetected_chromedriver langsung
from seleniumwire import undetected_chromedriver as uc 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Konfigurasi Proxy Anda (Ganti dengan IP yang paling segar/aktif dari list Anda)
proxy_host = "104.253.212.129"  # Contoh mencoba IP Toronto
proxy_port = "5539"
proxy_user = "cuxtoffl"
proxy_pass = "hv8pnsh88c3r"

proxy_options = {
    'proxy': {
        'http': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
        'https': f'https://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
        'no_proxy': 'localhost,127.0.0.1'
    }
}

options = uc.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')

# Gunakan User-Agent yang lebih baru agar sinkron dengan Chrome Anda
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

try:
    print(f"Membuka browser UC dengan Proxy Kanada ({proxy_host})...")
    
    # Membuka undetected-chromedriver menggunakan engine milik selenium-wire
    driver = uc.Chrome(
        seleniumwire_options=proxy_options,
        options=options
    )

    print("Membuka halaman No Frills...")
    url = "https://www.nofrills.ca/"
    driver.get(url)

    print("Menunggu halaman memuat konten...")
    time.sleep(12) # Naikkan jeda waktu karena proxy terkadang lambat

    print(f"Judul Halaman Saat Ini: {driver.title}")

    if "Access Denied" in driver.title:
        print("[WARNING] Masih terkena Access Denied. Berarti IP proxy ini sudah ditandai/diblokir oleh Akamai. Silakan ganti IP proxy lainnya.")
    else:
        print("[SUCCESS] Berhasil masuk halaman utama!")
        
        # --- BAGIAN PENGHILANG POPUP & AKTIVASI SCROLL ---
        print("Mencoba menghilangkan popup jika ada...")
        driver.execute_script("""
            var backdrop = document.querySelector('[data-testid="modal_backdrop"]');
            if (backdrop) {
                backdrop.parentElement.remove();
                console.log('Modal removed');
            }
            document.body.style.overflow = 'auto';
            document.body.style.position = 'static';
            document.documentElement.style.overflow = 'auto';
            document.body.className = ''; 
        """)
        
        # Coba scroll
        driver.execute_script("window.scrollBy(0, 500);")
        print("Scroll berhasil dieksekusi.")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")

finally:
    input("\nTekan Enter untuk menutup browser...")
    try:
        driver.quit()
    except:
        pass