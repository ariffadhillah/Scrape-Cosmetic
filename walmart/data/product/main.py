import pandas as pd

# Baca file CSV
df = pd.read_csv("Fragrances-Cologne for Men.csv")

# (Opsional tapi sangat disarankan) rapikan URL dulu
df['Product Url'] = df['Product Url'].astype(str).str.strip().str.lower()

# Hapus duplicate URL (simpan yang pertama)
df_clean = df.drop_duplicates(subset='Product Url', keep='first')

# Simpan hasil
df_clean.to_csv("data_Fragrances-Cologne for Men.csv", index=False)

print(f"Data awal     : {len(df)} baris")
print(f"Setelah bersih: {len(df_clean)} baris")
