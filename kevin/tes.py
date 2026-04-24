# import requests

# url = "https://www.gesec.fr/wp-json/sn/adherent/all"

# payload = {}
# headers = {
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0',
#   'Accept': 'application/json, text/plain, */*',
#   'Accept-Language': 'en-US,en;q=0.9',
#   'Accept-Encoding': 'gzip, deflate, br, zstd',
#   'Connection': 'keep-alive',
#   'Referer': 'https://www.gesec.fr/cartographie/?',
#   'Cookie': '_pk_id.4.518a=d3e268b275120894.1775136227.; _pk_ses.4.518a=1; axeptio_cookies={%22^$^$token%22:%22LaFCDpIo5apXsitMKMBRMCaKMj%22%2C%22^$^$date%22:%222026-04-02T13:23:48.061Z%22%2C%22^$^$cookiesVersion%22:{}%2C%22^$^$completed%22:false}; axeptio_authorized_vendors=%2C%2C; axeptio_all_vendors=%2C%2C',
#   'Sec-Fetch-Dest': 'empty',
#   'Sec-Fetch-Mode': 'cors',
#   'Sec-Fetch-Site': 'same-origin',
#   'TE': 'trailers'
# }

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)


import requests
import json
import pandas as pd

# 1. URL dan Headers (Sesuai yang Anda gunakan sebelumnya)
url = "https://www.gesec.fr/wp-json/sn/adherent/all"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.gesec.fr/cartographie/?',
}

def simpan_ke_csv():
    try:
        print("Sedang mengambil data dari server...")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Ambil data JSON
        raw_data = response.json()
        
        # 2. Proses Pembersihan Data
        # Kolom 'travaux', 'maintenance', dan 'sav' isinya adalah string JSON list.
        # Kita ubah jadi teks biasa yang dipisahkan koma agar rapi di CSV.
        for item in raw_data:
            for col in ['travaux', 'maintenance', 'sav']:
                if col in item and item[col]:
                    try:
                        # Ubah string "['A', 'B']" menjadi "A, B"
                        cleaned_list = json.loads(item[col])
                        item[col] = ", ".join(cleaned_list)
                    except:
                        continue

        # 3. Masukkan ke DataFrame (Tabel)
        df = pd.DataFrame(raw_data)

        # 4. Simpan ke CSV
        # Gunakan sep=',' atau sep=';' (tergantung setting Excel Anda)
        # utf-8-sig penting supaya simbol derajat atau aksen Prancis tidak berantakan
        nama_file = "data_gesec_all.csv"
        df.to_csv(nama_file, index=False, sep=';', encoding='utf-8-sig')

        print("-" * 30)
        print(f"BERHASIL!")
        print(f"Total data: {len(df)} baris")
        print(f"File tersimpan sebagai: {nama_file}")
        print("-" * 30)

    except Exception as e:
        print(f"Waduh, ada error: {e}")

if __name__ == "__main__":
    simpan_ke_csv()