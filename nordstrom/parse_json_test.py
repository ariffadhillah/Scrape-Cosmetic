# import json
# import os

# TESTING_DIR = "testing_json"  # folder berisi file json

# def extract_skus_from_styles(data):
#     results = []

#     selling = data.get("sellingEssentials", {})
#     styles_by_id = selling.get("stylesById", {})

#     for style_id, style in styles_by_id.items():
#         product_name = style.get("productName")

#         skus_by_id = style.get("skus", {}).get("byId", {})

#         for sku_id, sku in skus_by_id.items():
#             results.append({
#                 "product_name": product_name,
#                 "style_id": style_id,
#                 "sku_id": sku_id,
#                 "rmsSkuId": sku.get("rmsSkuId"),
#                 "colorDisplayValue": sku.get("colorDisplayValue"),
#                 "sizeId": sku.get("sizeId"),
#                 "sizeDisplayValue": sku.get("sizeDisplayValue"),
#                 "totalQuantityAvailable": sku.get("totalQuantityAvailable"),
#                 "isAvailable": sku.get("isAvailable"),
#                 "isShipAvailable": sku.get("isShipAvailable"),
#             })

#     return results


# sku_data = extract_skus_from_styles(data)

# for item in sku_data:
#     print("-" * 50)
#     print(f"Product Name : {item['product_name']}")
#     print(f"SKU ID       : {item['sku_id']}")
#     print(f"rmsSkuId     : {item['rmsSkuId']}")
#     print(f"Color        : {item['colorDisplayValue']}")
#     print(f"Size ID      : {item['sizeId']}")
#     print(f"Size Display : {item['sizeDisplayValue']}")
#     print(f"Qty Avail    : {item['totalQuantityAvailable']}")




# def parse_file(filepath):
#     with open(filepath, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     selling = data.get("sellingEssentials", {})
#     styles_by_id = selling.get("stylesById", {})

#     if not styles_by_id:
#         print("⚠️ stylesById not found")
#         return

#     # 🔑 LOOP TANPA PEDULI ID "5495553"
#     for style_id, style_data in styles_by_id.items():
#         product_name = style_data.get("productTitle")
#         print(f"🧴 Product Name: {product_name}")
#         print(f"🆔 Style ID    : {style_id}")

#         skus = style_data.get("skus", {}).get("byId", {})

#         if not skus:
#             print("   ⚠️ No SKUs found")
#             continue

#         for sku_id, sku_data in skus.items():
#             print("   ─────────────────────────")
#             print(f"   SKU ID            : {sku_id}")
#             print(f"   rmsSkuId          : {sku_data.get('rmsSkuId')}")
#             print(f"   sizeId            : {sku_data.get('sizeId')}")
#             print(f"   sizeDisplayValue  : {sku_data.get('sizeDisplayValue')}")

#         print("=" * 60)


# print("🔍 Reading JSON testing files...\n")

# for file in os.listdir(TESTING_DIR):
#     if not file.endswith(".json"):
#         continue

#     print("=" * 60)
#     print(f"📄 File: {file}")
#     print("-" * 60)

#     try:
#         parse_file(os.path.join(TESTING_DIR, file))
#     except Exception as e:
#         print(f"❌ Error reading {file}: {e}")

# print("\n✅ Done reading all JSON files")



import json
import os

TESTING_DIR = "testing_json"




# print(get_main_image({  }))
def extract_skus_from_styles(data):
    results = []

    selling = data.get("sellingEssentials", {})
    styles_by_id = selling.get("stylesById", {})

    for style_id, style in styles_by_id.items():
        product_name = (
            style.get("productName")
            or style.get("productTitle")
        )

        skus_by_id = style.get("skus", {}).get("byId", {})

        for sku_id, sku in skus_by_id.items():
            results.append({
                "product_name": product_name,
                "style_id": style_id,
                "sku_id": sku_id,
                "rmsSkuId": sku.get("rmsSkuId"),
                "colorDisplayValue": sku.get("colorDisplayValue"),
                "sizeId": sku.get("sizeId"),
                "sizeDisplayValue": sku.get("sizeDisplayValue"),
                "totalQuantityAvailable": sku.get("totalQuantityAvailable"),
                "isAvailable": sku.get("isAvailable"),
                "isShipAvailable": sku.get("isShipAvailable"),
            })

    return results


def parse_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    sku_data = extract_skus_from_styles(data)

    if not sku_data:
        print("⚠️ No SKU data found")
        return

    for item in sku_data:
        print("   ─────────────────────────")
        print(f"   Product Name : {item['product_name']}")
        print(f"   Style ID    : {item['style_id']}")
        print(f"   SKU ID      : {item['sku_id']}")
        print(f"   rmsSkuId    : {item['rmsSkuId']}")
        print(f"   Color       : {item['colorDisplayValue']}")
        print(f"   Size ID     : {item['sizeId']}")
        print(f"   Size Display: {item['sizeDisplayValue']}")
        print(f"   Qty Avail   : {item['totalQuantityAvailable']}")


print("🔍 Reading JSON testing files...\n")

for file in os.listdir(TESTING_DIR):
    if not file.endswith(".json"):
        continue

    print("=" * 60)
    print(f"📄 File: {file}")
    print("=" * 60)

    try:
        parse_file(os.path.join(TESTING_DIR, file))
    except Exception as e:
        print(f"❌ Error reading {file}: {e}")

print("\n✅ Done reading all JSON files")
