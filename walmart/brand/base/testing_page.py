import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json

# --- KONFIGURASI GLOBAL ---
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5  # Jeda waktu antara retry (0.5s, 1s, 2s, dst.)
TIMEOUT = 30          # Perpanjang timeout menjadi 30 detik

# --- FUNGSI UNTUK MEMBUAT SESSION DENGAN RETRY ---

def create_session():
    """Membuat session requests dengan konfigurasi retry yang kuat."""
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504], # Kode status yang harus di-retry
        allowed_methods={"HEAD", "GET", "OPTIONS"}
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    return http

# Inisialisasi session yang akan digunakan untuk semua permintaan
SESSION = create_session()

# --- FUNGSI PENGAMBILAN URL VARIAN (Diperbarui menggunakan SESSION) ---

def ekstrak_dan_filter_urls_walmart(base_url, target_id, target_class):
    """
    Mengambil konten HTML dari URL utama, mencari tautan varian, 
    dan mengembalikan daftar URL unik.
    """
    try:
        # Header yang diperkuat
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8'
        }
        
        # Menggunakan SESSION global dengan timeout yang diperpanjang
        response = SESSION.get(base_url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        main_div = soup.find('div', id=target_id)
        
        # ... (Logika parsing elemen varian tetap sama) ...
        
        if not main_div:
            return []

        target_div = main_div.find('div', class_=target_class)
        
        if not target_div:
            return []
        
        all_links = target_div.find_all('a', href=True)
        extracted_urls = set() 
        
        for link in all_links:
            href = link.get('href')
            absolute_url = urljoin(base_url, href)
            extracted_urls.add(absolute_url)

        return list(extracted_urls)

    except requests.exceptions.RequestException as e:
        # Jika gagal setelah semua retry
        print(f"❌ Kesalahan fatal saat mengambil URL utama ({base_url}) setelah {MAX_RETRIES} percobaan: {e}")
        return []

# --- FUNGSI BARU: MENGAMBIL TITLE DARI URL VARIAN (Diperbarui menggunakan SESSION) ---

def ambil_title_dari_url(url, title_id="main-title"):
    """
    Mengunjungi URL varian, mencari title, dan mencoba JSON jika HTML gagal.
    """
    try:
        # Header yang sama
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        }
        
        # Menggunakan SESSION global dengan timeout yang diperpanjang
        response = SESSION.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Coba cari berdasarkan ID (Metode Asli)
        title_tag = soup.find('h1', id=title_id)
        
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # 2. Coba cari berdasarkan Class
        title_tag_by_class = soup.find('h1', class_='dark-gray mv1 lh-copy f4 mh0 b')
        
        if title_tag_by_class:
            return title_tag_by_class.get_text(strip=True)
            
        # 3. Coba cari title di dalam JSON __NEXT_DATA__ (Metode Paling Andal)
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if script_tag and script_tag.string:
            data_dict = json.loads(script_tag.string)
            # Jalur untuk nama produk di JSON
            product_name = data_dict['props']['pageProps']['initialData']['data']['product']['displayName']
            if product_name:
                print("   [INFO: Title berhasil diambil dari __NEXT_DATA__ JSON]")
                return product_name

        return "Title Tidak Ditemukan (Gagal di HTML dan JSON)"

    except requests.exceptions.RequestException as e:
        return f"Kesalahan Request: {e}"
    except KeyError:
        return "Title Tidak Ditemukan (Gagal di HTML dan JSON)"
    except Exception as e:
        return f"Kesalahan Lain: {e}"

# --- Proses Utama ---

# URL Utama (yang berisi link ke varian)
base_url = "https://www.walmart.com/ip/Marketside-Lamb-Shoulder-Chop-0-5-1-0-lb/710389244?classType=REGULAR"
# Target elemen untuk mencari link varian
target_id_main = "item-page-variant-group-bg-div"
target_class_main = "dn" 

print("## 1. Ekstraksi URL Varian dari Halaman Utama")
print("="*40)

# Langkah 1: Ambil semua URL varian yang unik
unique_urls = ekstrak_dan_filter_urls_walmart(base_url, target_id_main, target_class_main)

if not unique_urls:
    print("❌ Tidak ada URL varian yang berhasil diekstrak.")
else:
    print(f"✅ Berhasil mengekstrak {len(unique_urls)} URL varian unik.")
    print("\n## 2. Mengambil Title untuk Setiap URL Varian")
    print("="*40)
    
    product_titles = {}
    
    for i, url in enumerate(unique_urls):
        print(f"[{i+1}/{len(unique_urls)}] Memproses URL: {url}...")
        
        # Mengambil title
        title = ambil_title_dari_url(url)
        
        product_titles[url] = title
        
        print(f"   -> Title: {title[:80]}...") 
        
        # Tambahkan jeda waktu singkat (delay)
        time.sleep(2) # Tingkatkan jeda menjadi 2 detik

    print("\n## 3. Hasil Akhir (URL dan Title Produk)")
    print("="*40)
    
    for url, title in product_titles.items():
        print(f"URL: {url}")
        print(f"Title: {title}\n")