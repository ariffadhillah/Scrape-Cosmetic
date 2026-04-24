from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.selfridges.com/GB/en/product/chanel-les-beiges-water-fresh-complexion-touch-even-illuminate-hydrate-20ml_R04459609/"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        print(f"🔗 Membuka halaman: {URL}")
        page.goto(URL, timeout=90000, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)  # biar semua request selesai

        # 🔍 1. Filter request hanya untuk images.selfridges.com
        print("\n🖼️ Product Images Found:")
        for req in page.context.requests:
            if "images.selfridges.com/is/image/selfridges" in req.url:
                print(" ", req.url)

        # 🔍 2. Ambil JSON-LD dari HTML
        soup = BeautifulSoup(page.content(), "html.parser")
        scripts = soup.find_all("script", type="application/ld+json")

        for i, script in enumerate(scripts, start=1):
            try:
                data = json.loads(script.string)
                print(f"\n📦 JSON-LD #{i}:")
                print(json.dumps(data, indent=2))
            except Exception as e:
                print(f"⚠️ Gagal parse JSON-LD #{i}: {e}")

        browser.close()

if __name__ == "__main__":
    run()
