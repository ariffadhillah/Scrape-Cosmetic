import csv

input_file = 'Badger.csv' # Ganti dengan nama file sumbermu
clean_file = 'clear-Badger.csv'
duplicate_file = 'walmart_duplicate_url.csv'

def clean_duplicates():
    seen_urls = set()
    clean_data = []
    duplicate_data = []
    header = []

    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Ambil header (Title, URL)

            for row in reader:
                if not row: continue
                url = row[0]
                
                # Cek duplikat berdasarkan URL
                if url not in seen_urls:
                    seen_urls.add(url)
                    clean_data.append(row)
                else:
                    duplicate_data.append(row)

        # 1. Simpan data yang BERSIH
        with open(clean_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(clean_data)

        # 2. Simpan data yang DUPLIKAT
        with open(duplicate_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(duplicate_data)

        print(f"Proses Selesai!")
        print(f"Total baris diproses : {len(clean_data) + len(duplicate_data)}")
        print(f"Data unik disimpan ke  : {clean_file} ({len(clean_data)} baris)")
        print(f"Data duplikat disimpan ke: {duplicate_file} ({len(duplicate_data)} baris)")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' tidak ditemukan. Pastikan namanya benar.")

if __name__ == "__main__":
    clean_duplicates()