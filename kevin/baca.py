from googlesearch import search
import pandas as pd
import time

# Load file CSV Anda
df = pd.read_csv("Gesec scraping - Copy of Sheet1.csv")

def find_website(company_name, city):
    query = f"{company_name} {city} France website"
    try:
        # Mengambil hasil pertama dari Google
        for j in search(query, tld="co.id", num=1, stop=1, pause=2):
            return j
    except:
        return "Not Found"

# Filter hanya yang website-nya kosong (NaN atau string kosong)
mask = df['Website'].isna() | (df['Website'] == "")

for index, row in df[mask].iterrows():
    print(f"Mencari website untuk: {row['Company Name']}...")
    found_url = find_website(row['Company Name'], row['City'])
    df.at[index, 'Website'] = found_url
    time.sleep(1) # Jeda agar tidak diblokir Google

# Simpan kembali ke CSV baru
df.to_csv("Gesec_Data_Updated.csv", index=False)