# # walmart_main.py (Diperbarui untuk Mengimpor Konfigurasi)

# from walmart_url_extractor import ekstrak_dan_filter_urls_walmart, get_config
# from walmart_json_processor import proses_dan_simpan_json
# import time

# # --- Konfigurasi Proses ---
# BASE_URL, URL_TARGET_ID, URL_TARGET_CLASS = get_config() # <<< Mengambil konfigurasi dari file lain!
# DELAY_BETWEEN_REQUESTS = 2 # Jeda 2 detik antar permintaan JSON

# # --- Proses Utama ---

# def main():
#     print("==============================================")
#     print("  Langkah 1: Mengambil Daftar URL Varian Unik ")
#     print("==============================================")
    
#     # Panggil fungsi dari walmart_url_extractor.py
#     unique_urls = ekstrak_dan_filter_urls_walmart(BASE_URL, URL_TARGET_ID, URL_TARGET_CLASS)

#     urls_to_process = []
    
#     if unique_urls:
#         # --- JALUR 1: PRODUK BERVARIAN ---
#         urls_to_process = unique_urls
#         print(f"\n✅ Total {len(urls_to_process)} URL varian unik berhasil diambil.")
#     else:
#         # --- JALUR 2: PRODUK TUNGGAL ---
#         print(f"\n⚠️ Tidak ditemukan elemen varian ('{URL_TARGET_ID}').")
#         print("   Asumsi: Produk tunggal, akan memproses JSON dari BASE_URL.")
        
#         # Tambahkan URL utama sebagai satu-satunya yang perlu diproses
#         urls_to_process = [BASE_URL]
        
#     print("\n==============================================")
#     print(f"  Langkah 2: Mengambil JSON untuk {len(urls_to_process)} URL ")
#     print("==============================================")

#     total_berhasil = 0
    
#     for i, url in enumerate(urls_to_process):
#         # Tambahkan jeda waktu antar permintaan
#         if i > 0:
#             time.sleep(DELAY_BETWEEN_REQUESTS)
            
#         print(f"\n[{i+1}/{len(urls_to_process)}] Memproses URL: {url}")
        
#         # Panggil fungsi dari walmart_json_processor.py
#         if proses_dan_simpan_json(url):
#             total_berhasil += 1

#     print("\n==============================================")
#     print(f"  Proses Selesai. Total JSON berhasil: {total_berhasil}/{len(urls_to_process)}")
#     print("==============================================")

# if __name__ == '__main__':
#     main()




# main.py
from walmart_url_extractor import ambil_daftar_url_dari_csv, ekstrak_dan_filter_urls_walmart
from walmart_json_processor import proses_dan_simpan_json
import time
url_csv = "Url-Cologne for Men.csv"
def jalan_otomatis():
    # 1. Ambil semua produk dari hasil scan kategori
    produk_awal = ambil_daftar_url_dari_csv(url_csv)
    print(f"🚀 Memulai pemrosesan {len(produk_awal)} produk dasar...")

    total_berhasil = 0

    for idx, url_produk in enumerate(produk_awal, 1):
        print(f"\n📦 [{idx}/{len(produk_awal)}] Mencari varian untuk: {url_produk}")
        
        # 2. Cari semua varian warna (misal: satu lipstik punya 10 warna)
        semua_varian = ekstrak_dan_filter_urls_walmart(url_produk)
        print(f"    ditemukan {len(semua_varian)} varian warna.")

        # 3. Proses setiap varian satu per satu
        for v_url in semua_varian:
            sukses = proses_dan_simpan_json(v_url)
            if sukses:
                total_berhasil += 1
            
            # Jeda agar tidak diblokir Walmart
            time.sleep(3)

    print(f"\n🏁 SELESAI! Berhasil menyimpan {total_berhasil} dari file {url_csv} baris data ke CSV.")

if __name__ == "__main__":
    jalan_otomatis()