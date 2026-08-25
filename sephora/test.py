import asyncio
import httpx
from playwright.async_api import async_playwright

# --- Fungsi untuk ambil data dari halaman produk ---
import re

# async def scrape_product_data(page, product_url):
#     try:
#         await page.goto(product_url, timeout=60000)
#         await page.wait_for_selector(".css-4gyk6s", timeout=10000)

#         # Cari elemen deskripsi
#         description_element = await page.query_selector(".css-4gyk6s")
#         if not description_element:
#             print(f"Tidak ditemukan elemen dengan class css-4gyk6s di {product_url}")
#             return {"url": product_url, "skus": []}

#         # Cari semua <img> di dalam elemen tersebut
#         img_elements = await description_element.query_selector_all("img")

#         sku_list = []
#         for img in img_elements:
#             src = await img.get_attribute("src")
#             if src and "productimages/sku/s" in src:
#                 match = re.search(r"/s(\d+)\+sw-", src)
#                 if match:
#                     sku = match.group(1)
#                     sku_list.append(sku)

#         print(f"[{product_url}]")
#         print("SKUs:", sku_list)
#         return {"url": product_url, "skus": sku_list}

#     except Exception as e:
#         print(f"Error on {product_url}: {e}")
#         return {"url": product_url, "skus": []}

import re

async def scrape_product_data(page, product_url):
    try:
        await page.goto(product_url, timeout=60000)
        await page.wait_for_selector('div[data-comp="SwatchGroup "]', timeout=10000)

        # Ambil semua elemen SwatchGroup
        swatch_groups = await page.query_selector_all('div[data-comp="SwatchGroup "]')
        if not swatch_groups:
            print(f"Tidak ditemukan elemen SwatchGroup di {product_url}")
            return {"url": product_url, "skus": []}

        sku_list = []

        for group in swatch_groups:
            img_elements = await group.query_selector_all("img")
            for img in img_elements:
                src = await img.get_attribute("src")
                if src and "productimages/sku/s" in src:
                    match = re.search(r"/s(\d+)\+sw-", src)
                    if match:
                        sku = match.group(1)
                        sku_list.append(sku)

        print(f"[{product_url}]")
        print("SKUs:", sku_list)
        return {"url": product_url, "skus": sku_list}

    except Exception as e:
        print(f"Error on {product_url}: {e}")
        return {"url": product_url, "skus": []}



# --- Fungsi utama ---
async def main():
    url = "https://www.sephora.com/api/v2/catalog/categories/makeup-cosmetics/seo?targetSearchEngine=NLP&currentPage=1&pageSize=60&content=true&includeRegionsMap=true&pickupRampup=true&sddRampup=true&includeEDD=true&loc=en-US&ch=rwd"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        data = resp.json()

    products = data.get("products", [])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        results = []

        for product in products:
            target_url = product.get("targetUrl")
            if not target_url:
                continue

            brand = product.get("brandName")
            name = product.get("displayName")
            productId = product.get("productId")
            print(productId, brand, name)

            product_url = f"https://www.sephora.com{target_url}"
            print(f"Processing: {product_url}")
            result = await scrape_product_data(page, product_url)
            results.append(result)

        await browser.close()

# Jalankan
asyncio.run(main())
