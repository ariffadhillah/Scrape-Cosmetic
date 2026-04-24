# main.py
from walmart_url_extractor import ambil_daftar_url_dari_csv, ekstrak_dan_filter_urls_walmart
from walmart_json_processor import proses_dan_simpan_json
import time
url_csv = "Clear_walmart_pet_food.csv"
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