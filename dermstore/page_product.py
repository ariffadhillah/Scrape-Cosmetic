import requests
import json
import re
from bs4 import BeautifulSoup
import sys 

sys.setrecursionlimit(3000)

# ==============================================================================
# I. FUNGSI HELPER (Ekstraksi dari HTML Langsung)
# ==============================================================================

def extract_product_overview_from_html(soup):
    """Fallback: Mencari Product Overview dari tab HTML."""
    # Mencari div utama untuk tab Product Overview
    target_div = soup.find('div', {'id': 'product-description-0'})
    if not target_div:
        target_div = soup.find('div', {'aria-labelledby': 'Product-Overview'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return None

def extract_ingredients_from_html(soup):
    """Fallback: Mencari Ingredients dari tab HTML."""
    # Mencari div utama untuk tab Ingredients
    target_div = soup.find('div', {'aria-labelledby': 'Ingredients'})
    if target_div:
        clean_text = target_div.get_text(separator='\n', strip=True)
        return clean_text
    return None

def extract_brand_from_html(soup):
    """Fallback: Mencari Brand dari Breadcrumbs atau Link Brand."""
    # 1. Dari Breadcrumbs
    breadcrumb = soup.find('ol', class_=lambda c: c and 'breadcrumbs' in c)
    if breadcrumb:
        # Ambil elemen kedua dari belakang (biasanya Brand)
        brand_link = breadcrumb.find_all('li')
        if len(brand_link) > 1:
            brand_name = brand_link[-2].get_text(strip=True)
            if brand_name and brand_name.lower() != 'all brands':
                return brand_name
    
    # 2. Dari Link Brand
    brand_link = soup.find('a', class_=lambda c: c and 'product-brand' in c)
    if brand_link:
        return brand_link.get_text(strip=True)
    
    return None

def extract_rating_and_reviews(soup):
    """Mengekstrak Rating dan Review dari JSON-LD schema markup."""
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    rating_data = None
    review_list = []
    
    for script in json_ld_scripts:
        if script.string:
            try:
                data = json.loads(script.string)
                # Menangani kasus di mana JSON-LD adalah list atau dictionary tunggal
                if isinstance(data, list):
                    data = next((item for item in data if item.get("@type") == "Product"), None)
                
                if isinstance(data, dict) and data.get("@type") == "Product":
                    # Ambil Aggregate Rating
                    aggregate_rating = data.get("aggregateRating")
                    if aggregate_rating:
                        rating_data = {
                            'value': aggregate_rating.get('ratingValue'), 
                            'count': aggregate_rating.get('reviewCount')
                        }
                    
                    # Ambil daftar Review (hanya 3 yang pertama)
                    reviews = data.get("review")
                    if reviews:
                        for review in reviews[:3]: 
                            review_list.append({
                                'rating': review['reviewRating'].get('ratingValue', 'N/A'),
                                'author': review['author'].get('name', 'Anonymous'),
                                'body': review.get('reviewBody', 'No body text'),
                                'date': review.get('datePublished', 'N/A')
                            })
                    
                    if rating_data or review_list:
                        return rating_data, review_list
            
            except json.JSONDecodeError:
                continue
                
    return rating_data, review_list

# ==============================================================================
# II. FUNGSI UTAMA SCRAPER
# ==============================================================================

def scrape_dermstore_data(url):
    """Mengambil semua data produk (variasi, ingredients, brand, rating, overview, image URL) dari URL Dermstore."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"Sedang mengambil data dari: {url} ...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"[ERROR] Gagal membuka halaman. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        # Inisialisasi variabel data
        variation_data = None
        ingredients_content = None
        brand_name = None 
        overview_content = None
        
        # 0. Ekstraksi Rating dan Reviews (JSON-LD)
        rating_data, review_list = extract_rating_and_reviews(soup)
        
        # 1. Cari Data Variasi (Prioritas Tinggi dari JavaScript)
        for script in scripts:
            if script.string and "const variationData =" in script.string:
                match = re.search(r'const variationData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                if match:
                    try:
                        variation_data = json.loads(match.group(1))
                        break
                    except json.JSONDecodeError:
                        pass
        
        # 2. Ekstraksi Konten dari Data Variasi (Jika Ditemukan)
        if variation_data:
            # Asumsikan konten utama ada di variasi pertama
            first_variation = variation_data[0] 
            content_list = first_variation.get('content', [])

            for content_item in content_list:
                
                # A. Ekstraksi Product Overview (synopsis)
                if content_item.get('key') == 'synopsis' and not overview_content:
                    try:
                        # Mendekode HTML di dalam struktur JSON
                        content_list_value = content_item['value']['richContentListValue'][0]['content']
                        for html_block in content_list_value:
                            if html_block['type'] == 'HTML':
                                soup_overview = BeautifulSoup(html_block['content'], 'html.parser')
                                overview_content = soup_overview.get_text(separator="\n", strip=True)
                                break
                    except (KeyError, TypeError, IndexError):
                        pass

                # B. Ekstraksi Ingredients
                if content_item.get('key') == 'ingredients' and not ingredients_content:
                    try:
                        # Mendekode HTML di dalam struktur JSON
                        content_html_list = content_item['value']['richContentValue']['content']
                        for html_block in content_html_list:
                            if html_block['type'] == 'HTML':
                                soup_ingredients = BeautifulSoup(html_block['content'], 'html.parser')
                                ingredients_content = soup_ingredients.get_text(separator="\n", strip=True)
                                break
                    except (KeyError, TypeError):
                        pass
                        
                # C. Ekstraksi Brand
                if content_item.get('key') == 'brand' and not brand_name:
                    try:
                        brand_list = content_item['value']['stringListValue']
                        if brand_list:
                            brand_name = brand_list[0]
                    except (KeyError, TypeError):
                        pass

        # 3. Fallback: Ekstraksi Overview, Ingredients, Brand dari HTML
        if not overview_content:
            overview_content = extract_product_overview_from_html(soup)
        
        if not ingredients_content:
            ingredients_content = extract_ingredients_from_html(soup)

        if not brand_name:
            brand_name = extract_brand_from_html(soup)

        # ======================================================================
        # III. OUTPUT HASIL EKSTRAKSI
        # ======================================================================

        # 1. Metadata
        print("\n" + "="*120)
        print("## 🏷️ Hasil Ekstraksi Metadata")
        print("="*120)
        print(f"{'Brand':<15}: {brand_name if brand_name else 'TIDAK DITEMUKAN'}")
        
        if rating_data:
            print(f"{'Rating':<15}: {rating_data['value']} ({rating_data['count']} reviews)")
        else:
            print(f"{'Rating':<15}: TIDAK DITEMUKAN")
        
        # 2. Product Overview
        if overview_content:
            print("\n" + "="*120)
            print("## 📄 Product Overview")
            print("="*120)
            # Batasi tampilan agar tidak terlalu panjang
            print(overview_content[:500] + '...' if len(overview_content) > 500 else overview_content)
        else:
            print("\n[INFO] Product Overview tidak ditemukan.")
            
        # 3. Variasi Produk (Harga, Stock, Image URL)
        if variation_data:
            print("\n" + "="*120)
            print("## 💄 Hasil Ekstraksi Variasi Produk")
            print("="*120)
            print(f"{'SKU':<10} | {'Status':<10} | {'Harga':<8} | {'Warna / Varian':<40} | {'Image URL'}")
            print("-" * 120)

            for item in variation_data:
                sku = item.get('sku')
                name_site = item.get('name')
                in_stock = "Ready" if item.get('inStock') else "Kosong"
                
                try:
                    price = item['price']['price']['displayValue']
                except (KeyError, TypeError):
                    price = "N/A"
                
                try:
                    # Ambil title dari pilihan (choices) atau title utama item
                    color_name = item['choices'][0]['title']
                    print("color_name", color_name)
                except (KeyError, IndexError, TypeError):
                    color_name = item.get('title', 'Unknown')
                    
                # Ekstraksi Image URL
                image_url = "N/A"
                try:
                    image_url = item['images'][0]['original']
                except (KeyError, IndexError, TypeError):
                    pass 
                
                # Info Subscription (jika ada)
                subscription_contract = next((c for c in item.get('subscriptionContracts', []) if c.get('recommended')), None)
                subscription_info = ""
                if subscription_contract:
                    initial_price = subscription_contract['initialPrice']['price']['displayValue']
                    freq = f"{subscription_contract['frequencyDuration']['duration']} {subscription_contract['frequencyDuration']['unit'].lower()}"
                    subscription_info = f" (Subs: {initial_price}/{freq})"

                print(f"{sku} | {'name_site'} {name_site} | {in_stock} | {price} | {color_name + subscription_info} | {image_url}")
        else:
             print("\n[INFO] Data variasi produk tidak ditemukan.")

        # 4. Ingredients
        if ingredients_content:
            print("\n" + "="*120)
            print("## 🌱 Hasil Ekstraksi Ingredients (Komposisi)")
            print("="*120)
            # Batasi tampilan agar tidak terlalu panjang
            print(ingredients_content[:500] + '...' if len(ingredients_content) > 500 else ingredients_content)
            print("\n" + "="*120)
        else:
            print("\n[INFO] Key 'ingredients' tidak ditemukan.")
        
        # 5. Ulasan (Review)
        if review_list:
            print("\n" + "="*120)
            print("## ⭐ Ulasan Terbaru (Reviews)")
            print("="*120)
            for i, review in enumerate(review_list):
                print(f"--- Review {i+1} ({review['date']}) ---")
                print(f"Rating: {review['rating']}/5 by {review['author']}")
                # Batasi ulasan agar tidak terlalu panjang
                print(f"Ulasan: {review['body'][:100]}...")
            print("\n" + "="*120)
        else:
            print("\n[INFO] Data ulasan (review) tidak ditemukan.")


    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat scraping: {e}")

# ==============================================================================
# IV. EKSEKUSI UJI KASUS
# ==============================================================================
if __name__ == "__main__":
    
    print("\n" + "=" * 50 + " MEMULAI PENGUJIAN PRODUK " + "=" * 50)
    
    # print("\n" + "--- UJI KASUS 1: RevitaLash (Single SKU) ---")
    # target_url_1 = "https://www.dermstore.com/p/above-us-steorra-eau-de-parfum-50ml/16895897/"
    # scrape_dermstore_data(target_url_1)

    print("\n" + "#" * 120 + "\n")

    print("--- UJI KASUS 2: Wander Beauty (Multiple Variations) ---")
    target_url_2 = "https://www.dermstore.com/p/alchimie-forever-protective-day-cream-spf23/11286078/"
    scrape_dermstore_data(target_url_2)

    print("\n" + "=" * 50 + " PENGUJIAN SELESAI " + "=" * 50)