import pandas as pd
import openai

# 1. Inisialisasi API Key
client = openai.OpenAI(api_key="xxxx")
def is_clothing(url):
    try:
        # Mengambil nama produk dari URL untuk dianalisis AI
        product_name = url.split('/')[-2].replace('-', ' ')
        
        prompt = f"Identify if this product is clothing/apparel or food/drink. Answer only with 'CLOTHING' or 'FOOD'. \nProduct: {product_name}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        result = response.choices[0].message.content.strip().upper()
        return result == "CLOTHING"
    except:
        return False

# 2. Baca file CSV
df = pd.read_csv('Url-.csv')

# Asumsikan kolom URL Anda bernama 'url'
print("Sedang memproses pembersihan...")

# 3. Filter data
# Kita tambahkan kolom baru sebagai penanda agar data asli tidak hilang
df['is_clothing'] = df['url'].apply(is_clothing)

# 4. Pisahkan yang bukan pakaian
df_cleaned = df[df['is_clothing'] == False].drop(columns=['is_clothing'])

# 5. Simpan ke file baru
df_cleaned.to_csv('url_cleaned.csv', index=False)

print(f"Selesai! Data bersih disimpan di 'url_cleaned.csv'.")
print(f"Jumlah data dihapus: {len(df) - len(df_cleaned)}")