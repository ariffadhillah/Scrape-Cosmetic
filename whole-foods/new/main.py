from category import get_all_asins_from_category
from variant import process_asin
import time
import random


def main():

    print("\nAMBIL DATA ASIN DARI CATEGORY...\n")

    asin_list = get_all_asins_from_category()

    if not asin_list:
        print("Tidak ada ASIN ditemukan.")
        return

    print(f"TOTAL ASIN: {len(asin_list)}\n")

    # optional: hapus duplikat global
    asin_list = list(dict.fromkeys(asin_list))

    # for i, asin in enumerate(asin_list, 1):

    #     print(f"\n===== [{i}/{len(asin_list)}] PROCESS {asin} =====")

    #     try:
    #         process_asin(asin)

    #     except Exception as e:
    #         print("ERROR:", e)

    #     # jeda antar produk agar aman dari bot detection
    #     time.sleep(random.uniform(3,6))

    for i, (category, asin) in enumerate(asin_list, 1):

        print(f"\n===== [{i}/{len(asin_list)}] PROCESS {asin} =====")
        print("CATEGORY:", category)

        try:
            process_asin(asin, category)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(random.uniform(3,6))


if __name__ == "__main__":
    main()