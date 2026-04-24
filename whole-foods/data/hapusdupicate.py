import pandas as pd

# 1. Membaca file CSV (ganti 'data_input.csv' dengan nama file Anda)
file_input = 'daftar_pa_care_asin.csv'
df = pd.read_csv(file_input)

# 2. Menghapus duplikat berdasarkan kolom 'ASIN'
# keep='first' artinya baris pertama yang ditemukan akan dipertahankan
df_unique = df.drop_duplicates(subset=['ASIN'], keep='first')

# 3. Menyimpan hasil ke file CSV baru
file_output = 'daftar_pa_care_asin-clean.csv'
df_unique.to_csv(file_output, index=False)

print(f"Selesai! Total baris setelah duplikat dihapus: {len(df_unique)}")
print(f"File disimpan sebagai: {file_output}")