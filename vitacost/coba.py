# # from playwright.sync_api import sync_playwright

# # PROXY = {
# #     "server": "http://dc.decodo.com:10000",
# #     "username": "user-spdv8itjmq-country-us",
# #     "password": "0uHrpir4~kH9Ipb6Wg"
# # }

# # BASE = "https://www.vitacost.com"
# # URL = "https://www.vitacost.com/supplements-22"

# # def main():
# #     with sync_playwright() as p:
# #         browser = p.chromium.launch(
# #             headless=False,
# #             args=["--ignore-certificate-errors"]
# #         )

# #         context = browser.new_context(
# #             proxy=PROXY,
# #             ignore_https_errors=True,
# #         )

# #         page = context.new_page()

# #         print("🔎 Loading page via proxy...")
# #         page.goto(URL, timeout=120000)

# #         # Tunggu list produk
# #         page.wait_for_selector("ul.productWrapper.spPLB", timeout=30000)

# #         print("🔎 Ambil link dengan class .ellipsis60 ...")

# #         product_links = page.query_selector_all("li.product-block a.ellipsis60")

# #         print(f"✅ Ditemukan {len(product_links)} produk!")

# #         all_links = []

# #         for a in product_links:
# #             href = a.get_attribute("href")
# #             if href:
# #                 full_url = BASE + href.strip()
# #                 all_links.append(full_url)
# #                 print(" →", full_url)

# #         browser.close()

# #         print("\n🔚 Selesai!")

# # if __name__ == "__main__":
# #     main()




# from playwright.sync_api import sync_playwright

# PROXY = {
#     "server": "http://dc.decodo.com:10000",
#     "username": "user-spdv8itjmq-country-us",
#     "password": "0uHrpir4~kH9Ipb6Wg"
# }

# BASE = "https://www.vitacost.com"
# CATEGORY_URL = "https://www.vitacost.com/supplements-22"
# MAX_PAGE = 235


# def main():
#     all_links = []

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,
#             args=["--ignore-certificate-errors"]
#         )

#         for pg in range(1, MAX_PAGE + 1):
#             url = f"{CATEGORY_URL}?pg={pg}"
#             print(f"\n📄 Membuka halaman {pg}/{MAX_PAGE}: {url}")

#             # -------- NEW: context baru per halaman --------
#             context = browser.new_context(
#                 proxy=PROXY,
#                 ignore_https_errors=True,
#             )
#             page = context.new_page()

#             try:
#                 page.goto(url, timeout=220000)

#                 # Tunggu produk muncul
#                 page.wait_for_selector("ul.productWrapper.spPLB", timeout=90000)

#                 items = page.query_selector_all("li.product-block a.ellipsis60")
#                 print(f"   → ditemukan {len(items)} produk")

#                 for a in items:
#                     href = a.get_attribute("href")
#                     if not href:
#                         continue
#                     full = BASE + href.strip()
#                     all_links.append(full)
#                     print("      →", full)

#             except Exception as e:
#                 print("⚠️ ERROR halaman:", e)
#                 print(f"⚠️ Halaman {pg} gagal dimuat, skip...")

#             finally:
#                 # KONTEKS DITUTUP → fingerprint reset
#                 context.close()

#         browser.close()

#     print("\n============================")
#     print(f"🔚 TOTAL LINK TERKUMPUL: {len(all_links)}")
#     print("============================")


# if __name__ == "__main__":
#     main()



from playwright.sync_api import sync_playwright
import csv
import time
PROXY = {
    "server": "http://dc.decodo.com:10000",
    "username": "user-spdv8itjmq-country-us",
    "password": "0uHrpir4~kH9Ipb6Wg"
}

BASE = "https://www.vitacost.com"
CATEGORY_URL = "https://www.vitacost.com/supplements-22"
MAX_PAGE = 235
CSV_FILE = "product_list.csv"   # ← file output


def save_to_csv(url_list):
    """Simpan daftar URL ke CSV dengan kolom 'url'."""
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url"])            # header
        for u in url_list:
            writer.writerow([u])
    print(f"\n💾 CSV berhasil dibuat: {CSV_FILE} ({len(url_list)} baris)")


def main():
    all_links = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--ignore-certificate-errors"]
        )

        for pg in range(1, MAX_PAGE + 1):
            url = f"{CATEGORY_URL}?pg={pg}"
            print(f"\n📄 Membuka halaman {pg}/{MAX_PAGE}: {url}")
            time.sleep(1)

            context = browser.new_context(
                proxy=PROXY,
                ignore_https_errors=True,
            )
            page = context.new_page()

            try:
                page.goto(url, timeout=320000)

                page.wait_for_selector("ul.productWrapper.spPLB", timeout=99000)

                items = page.query_selector_all("li.product-block a.ellipsis60")
                print(f"   → ditemukan {len(items)} produk")

                for a in items:
                    href = a.get_attribute("href")
                    if not href:
                        continue
                    full = BASE + href.strip()
                    all_links.append(full)
                    print("      →", full)
                
                save_to_csv(all_links)

                time.sleep(1)

            except Exception as e:
                print("⚠️ ERROR halaman:", e)
                print(f"⚠️ Halaman {pg} gagal dimuat, skip...")

            finally:
                context.close()
                
        browser.close()

    # Simpan ke CSV
    # save_to_csv(all_links)

    print("\n============================")
    print(f"🔚 TOTAL LINK TERKUMPUL: {len(all_links)}")
    print("============================")


if __name__ == "__main__":
    main()
