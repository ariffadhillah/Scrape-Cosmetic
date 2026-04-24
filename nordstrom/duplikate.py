import pandas as pd

# Baca file CSV
df = pd.read_csv("Hair-Scalp-Treatments.csv")

# Hapus duplicate berdasarkan kolom 'url'
df_clean = df.drop_duplicates(subset=["id"])

# Simpan ke file baru
df_clean.to_csv("urls-Hair-Scalp-Treatments.csv", index=False)

print(f"Data awal  : {len(df)} baris")
print(f"Setelah bersih: {len(df_clean)} baris")
