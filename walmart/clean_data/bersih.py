# # import pandas as pd

# # file = "Scrape Walmart Grocery - 2 - Sheet1.csv"

# # # 1. Load file CSV Anda
# # file_input = file  # Ganti dengan nama file Anda
# # df = pd.read_csv(file_input)

# # # 2. Hitung jumlah total baris sebelum dibersihkan
# # total_awal = len(df)

# # # 3. Identifikasi jumlah baris yang duplikat berdasarkan kolom "SKU ID"
# # # (Tanpa menghapus dulu, hanya untuk menghitung)
# # jumlah_duplikat = df.duplicated(subset=['SKU ID']).sum()

# # # 4. Hapus data duplikat
# # # keep='first' artinya kita menyimpan baris pertama yang muncul dan menghapus sisanya
# # df_clean = df.drop_duplicates(subset=['SKU ID'], keep='first')

# # # 5. Hitung jumlah baris setelah dibersihkan
# # total_tersisa = len(df_clean)

# # # 6. Simpan hasil pembersihan ke file baru
# # df_clean.to_csv(f'cleaned_{file}', index=False)

# # # Tampilkan laporan
# # print(f"--- Laporan Pembersihan Data ---")
# # print(f"Total data awal      : {total_awal} baris")
# # print(f"Jumlah data duplikat : {jumlah_duplikat} baris")
# # print(f"Total data tersisa   : {total_tersisa} baris")
# # print(f"--------------------------------")
# # print(f"File berhasil disimpan dengan nama: cleaned_{df_clean.shape[0]}_{file}")




# import pandas as pd

# file = "cleaned_84939_walmart----2223 - Sheet1.csv"

# # 1. Load file dengan optimasi memori
# # low_memory=False menangani peringatan mixed types
# # engine='c' adalah engine tercepat untuk membaca CSV di Pandas
# file_input = file 
# df = pd.read_csv(file_input, low_memory=False, engine='c')

# # 2. Pembersihan awal pada kolom kunci (Opsional tapi disarankan)
# # Kadang SKU ID terbaca sebagai angka atau teks dengan spasi, 
# # kita seragamkan agar penghapusan duplikat lebih akurat.
# df['SKU ID'] = df['SKU ID'].astype(str).str.strip()

# # 3. Hitung jumlah total baris sebelum dibersihkan
# total_awal = len(df)

# # 4. Hitung jumlah duplikat
# jumlah_duplikat = df.duplicated(subset=['SKU ID']).sum()

# # 5. Hapus data duplikat
# df_clean = df.drop_duplicates(subset=['SKU ID'], keep='first')

# # 6. Hitung jumlah baris setelah dibersihkan
# total_tersisa = len(df_clean)

# # 7. Simpan hasil pembersihan
# output_name = f"hasil-cleaned_{total_tersisa}_{file}"
# df_clean.to_csv(output_name, index=False)

# # Tampilkan laporan
# print(f"--- Laporan Pembersihan Data ---")
# print(f"Total data awal      : {total_awal} baris")
# print(f"Jumlah data duplikat : {jumlah_duplikat} baris")
# print(f"Total data tersisa   : {total_tersisa} baris")
# print(f"--------------------------------")
# print(f"File berhasil disimpan dengan nama: {output_name}")




# import pandas as pd

# file = "hasil-cleaned_84939_cleaned_84939_walmart----2223 - Sheet1.csv"
# file_input = file 

# # 1. Load data
# df = pd.read_csv(file_input, low_memory=False)

# # 2. Bersihkan .0 di belakang
# for col in ['SKU ID', 'UPC']:
#     if col in df.columns:
#         df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
#         df[col] = df[col].str.strip()
#         df[col] = df[col].replace('nan', '')

# # 3. Format UPC untuk Google Sheets (Tambah nol ke 12 digit + Petik satu)
# if 'UPC' in df.columns:
#     df['UPC'] = df['UPC'].apply(lambda x: "'" + x.zfill(12) if x != '' else x)

# # 4. Tambahkan petik satu juga pada SKU ID agar aman di Sheets
# if 'SKU ID' in df.columns:
#     df['SKU ID'] = df['SKU ID'].apply(lambda x: "'" + x if x != '' else x)

# # 5. Hitung dan Hapus Duplikat berdasarkan SKU ID
# # Catatan: Kita hitung duplikat SETELAH pembersihan agar lebih akurat
# total_awal = len(df)
# jumlah_duplikat = df.duplicated(subset=['SKU ID']).sum()
# df_clean = df.drop_duplicates(subset=['SKU ID'], keep='first')
# total_tersisa = len(df_clean)

# # 6. Simpan Hasil
# output_name = f"hasil-hasil-cleaned_{total_tersisa}_{file}"
# # Gunakan quoting=None jika perlu, tapi standarnya to_csv sudah aman
# df_clean.to_csv(output_name, index=False)

# print(f"--- Laporan Akhir ---")
# print(f"Total data awal      : {total_awal}")
# print(f"Duplikat dihapus     : {jumlah_duplikat}")
# print(f"Total data bersih    : {total_tersisa}")
# print(f"Format Kolom         : UPC & SKU ID ditambahkan petik (') untuk Google Sheets")
# print(f"File disimpan sebagai: {output_name}")



import pandas as pd
import numpy as np

file = "walmart----2223 - Sheet1.csv"
file_input = file 

# 1. Load data
df = pd.read_csv(file_input, low_memory=False)

# 2. Bersihkan .0 di belakang
for col in ['SKU ID', 'UPC']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
        df[col] = df[col].str.strip()
        df[col] = df[col].replace('nan', '')

# 3. Format UPC untuk Google Sheets (Tambah nol ke 12 digit + Petik satu)
if 'UPC' in df.columns:
    df['UPC'] = df['UPC'].apply(lambda x: "'" + x.zfill(12) if x != '' else x)

# 4. Tambahkan petik satu pada SKU ID agar aman di Sheets
if 'SKU ID' in df.columns:
    df['SKU ID'] = df['SKU ID'].apply(lambda x: "'" + x if x != '' else x)

# 5. Hapus Duplikat berdasarkan SKU ID
df_clean = df.drop_duplicates(subset=['SKU ID'], keep='first')
total_bersih = len(df_clean)

# 6. Membagi file menjadi 3 bagian
# np.array_split memastikan pembagian baris merata
parts = np.array_split(df_clean, 3)

print(f"--- Laporan Pembersihan & Pembagian ---")
print(f"Total data bersih: {total_bersih} baris")
print(f"Membagi menjadi 3 file...\n")

# 7. Simpan setiap bagian
for i, part in enumerate(parts):
    # Nama file: part_1_cleaned_data.csv, part_2_... dst
    part_name = f"part_{i+1}_of_3_cleaned_{len(part)}_{file}"
    part.to_csv(part_name, index=False)
    print(f"Berhasil menyimpan: {part_name} ({len(part)} baris)")

print(f"\nSelesai! Sekarang Anda punya 3 file yang lebih ringan untuk diunggah.")