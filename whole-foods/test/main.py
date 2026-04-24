from category import get_all_asins_from_category
from variant import process_asin, init_storage, finalize_storage
import time
import random

def main():
    print("\nAMBIL DATA ASIN DARI CATEGORY...\n")

    asin_list = get_all_asins_from_category()
    if not asin_list:
        print("Tidak ada ASIN ditemukan.")
        return

    print(f"TOTAL ITEM (category,asin): {len(asin_list)}\n")

    # dedupe global (category+asin)
    asin_list = list(dict.fromkeys(asin_list))

    # init storage dedupe/update
    init_storage()

    for i, (category, asin) in enumerate(asin_list, 1):
        print(f"\n===== [{i}/{len(asin_list)}] PROCESS {asin} =====")
        print("CATEGORY:", category)

        try:
            process_asin(asin, category)
        except Exception as e:
            print("ERROR:", e)

        time.sleep(random.uniform(3, 6))

    # write final CSV
    finalize_storage()

if __name__ == "__main__":
    main()