import requests
import csv
import time
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


# ==========================================================
# CONFIG
# ==========================================================

slug = "face-makeup"
# slug = "eye-makeup"
# slug = "lips-makeup"
# slug = "cheek-makeup"

base_url = (
    f"https://www.sephora.com/api/v2/catalog/categories/{slug}/seo"
)

params = {
    "targetSearchEngine": "NLP",
    "currentPage": 1,
    "pageSize": 60,
    "content": "true",
    "includeRegionsMap": "true",
    "pickupRampup": "true",
    "sddRampup": "true",
    "includeEDD": "true",
    "loc": "en-US",
    "ch": "rwd"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.sephora.com/",
}


# ==========================================================
# CATEGORY
# ==========================================================

def get_category_path(category_data):
    categories = []

    current = category_data

    while current:
        display_name = current.get("displayName")

        if display_name:
            categories.append(display_name)

        current = current.get("parentCategory")

    categories.reverse()

    return " > ".join(categories)


def get_top_level_category(category_data):
    while category_data.get("parentCategory"):
        category_data = category_data["parentCategory"]

    return category_data.get("displayName")


# ==========================================================
# RATING
# ==========================================================

def format_rating(rating):
    try:
        return f"{round(float(rating), 1)}"
    except:
        return None


def format_review_count(count):
    try:
        count = int(count)

        if count >= 1000:
            return f"{round(count / 1000, 1)} K"

        return str(count)

    except:
        return None



def clean_html_text(html):
    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Ubah <br> menjadi newline
    for br in soup.find_all("br"):
        br.replace_with("\n")

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    # Rapikan whitespace
    lines = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines)


# ==========================================================
# GET CATEGORY TOTAL PAGES
# ==========================================================

response = requests.get(
    base_url,
    headers=headers,
    params=params,
    timeout=30
)

response.raise_for_status()

data = response.json()

# Untuk sementara tetap 1 page seperti kode sebelumnya
total_pages = 1

print(
    f"📄 Total Pages: {total_pages}\n"
    f"{'=' * 60}"
)


# ==========================================================
# STORAGE
# ==========================================================

all_data = []

# Untuk menghindari duplicate product utama
seen_detail_urls = set()

# Untuk menghindari duplicate SKU yang BENAR-BENAR berhasil
seen_sku_urls = set()


# ==========================================================
# PAGE LOOP
# ==========================================================

# ==========================================================
# PAGINATION CONFIG
# ==========================================================

current_page = 1
page_size = 60

params["pageSize"] = page_size


# ==========================================================
# STORAGE
# ==========================================================

all_data = []

# Untuk menghindari duplicate product utama
seen_detail_urls = set()

# Untuk menghindari duplicate SKU yang berhasil
seen_sku_urls = set()


# ==========================================================
# PAGINATION LOOP
# ==========================================================

while True:

    print("\n")
    print("=" * 70)
    print(f"📄 REQUEST PAGE: {current_page}")
    print(f"📦 Page Size: {page_size}")
    print("=" * 70)


    # ------------------------------------------------------
    # SET CURRENT PAGE
    # ------------------------------------------------------

    params["currentPage"] = current_page


    # ------------------------------------------------------
    # REQUEST CATEGORY PAGE
    # ------------------------------------------------------

    try:

        response = requests.get(
            base_url,
            headers=headers,
            params=params,
            timeout=30
        )

        print(
            f"🌐 HTTP Status: "
            f"{response.status_code}"
        )

        response.raise_for_status()

        page_data = response.json()


    except Exception as e:

        print(
            f"❌ Gagal mengambil page "
            f"{current_page}: {e}"
        )

        break


    # ------------------------------------------------------
    # GET PRODUCTS
    # ------------------------------------------------------

    products = page_data.get(
        "products",
        []
    )


    product_count = len(products)


    print(
        f"🛍️ Products on page "
        f"{current_page}: "
        f"{product_count}"
    )


    # ------------------------------------------------------
    # STOP JIKA TIDAK ADA PRODUK
    # ------------------------------------------------------

    if not products:

        print(
            "\n🛑 Tidak ada produk lagi."
        )

        print(
            f"📄 Pagination selesai "
            f"pada page {current_page - 1}"
        )

        break


    # ======================================================
    # PRODUCT LOOP
    # ======================================================

    for product_index, p in enumerate(
        products,
        start=1
    ):

        print("\n")
        print("=" * 60)

        print(
            f"📄 PAGE: {current_page}"
        )

        print(
            f"🛍️ PRODUCT "
            f"{product_index}/{product_count}"
        )

        print("=" * 60)


        time.sleep(0.5)


        product_url = p.get(
            "targetUrl"
        )


        if not product_url:

            print(
                "⚠️ targetUrl tidak ditemukan"
            )

            continue


        detail_url = (
            f"https://www.sephora.com"
            f"{product_url}"
        )


        # --------------------------------------------------
        # CHECK DUPLICATE PRODUCT
        # --------------------------------------------------

        if detail_url in seen_detail_urls:

            print(
                f"⏭️ Skip duplicate product:"
            )

            print(detail_url)

            continue


        seen_detail_urls.add(
            detail_url
        )


        print(
            f"🔗 Product URL:"
        )

        print(detail_url)


        # ==================================================
        # PRODUCT DETAIL
        # ==================================================

        try:

            time.sleep(0.5)


            res = requests.get(
                detail_url,
                headers=headers,
                timeout=30
            )


            print(
                f"🌐 Product HTTP Status: "
                f"{res.status_code}"
            )


            if res.status_code != 200:

                print(
                    f"❌ Product request gagal: "
                    f"{res.status_code}"
                )

                continue


            soup = BeautifulSoup(
                res.text,
                "html.parser"
            )


            script_tag = soup.find(
                "script",
                {
                    "id": "linkStore",
                    "type": "text/json"
                }
            )


            if not script_tag:

                print(
                    "❌ Script tag linkStore "
                    "tidak ditemukan"
                )

                continue


            data_json = json.loads(
                script_tag.string
            )


            product = (
                data_json
                .get("page", {})
                .get("product", {})
            )


            if not product:

                print(
                    "❌ Product data "
                    "tidak ditemukan"
                )

                continue


            # ==================================================
            # GET ALL SKU
            # ==================================================

            sku_list = product.get(
                "regularChildSkus",
                []
            )


            all_sku_ids = [
                sku.get("skuId")
                for sku in sku_list
                if sku.get("skuId")
            ]


            print("\n")
            print("📦 SKU DEBUG")
            print("-" * 50)


            print(
                "Product:",
                product
                .get("productDetails", {})
                .get("displayName")
            )


            print(
                "Total SKU:",
                len(all_sku_ids)
            )


            print(
                "SKU List:",
                all_sku_ids
            )


            print("-" * 50)


            if not all_sku_ids:

                print(
                    "⚠️ Tidak ada SKU"
                )

                continue


            # ==================================================
            # PARSE URL
            # ==================================================

            parsed_url = urlparse(
                detail_url
            )


            query_params = parse_qs(
                parsed_url.query
            )


            # ==================================================
            # SKU LOOP
            # ==================================================

            for sku_index, sku_id in enumerate(
                all_sku_ids,
                start=1
            ):

                print("\n")
                print(
                    f"📦 SKU "
                    f"{sku_index}/"
                    f"{len(all_sku_ids)}"
                )


                print(
                    f"Requested SKU: "
                    f"{sku_id}"
                )


                # --------------------------------------------------
                # BUILD SKU URL
                # --------------------------------------------------

                query_params["skuId"] = [
                    sku_id
                ]


                new_query = urlencode(
                    query_params,
                    doseq=True
                )


                new_sku_url = urlunparse(
                    (
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment
                    )
                )


                print(
                    f"📦 SKU URL:\n"
                    f"{new_sku_url}"
                )


                # --------------------------------------------------
                # DUPLICATE CHECK
                # --------------------------------------------------

                if new_sku_url in seen_sku_urls:

                    print(
                        f"⏭️ SKU sudah diproses: "
                        f"{sku_id}"
                    )

                    continue


                # ==================================================
                # RETRY SKU
                # ==================================================

                max_retries = 3

                sku_processed = False


                for attempt in range(
                    1,
                    max_retries + 1
                ):

                    print(
                        f"\n🔄 SKU {sku_id} "
                        f"- Attempt "
                        f"{attempt}/"
                        f"{max_retries}"
                    )


                    try:

                        time.sleep(0.5)


                        sku_res = requests.get(
                            new_sku_url,
                            headers=headers,
                            timeout=30
                        )


                        print(
                            f"🌐 SKU HTTP Status: "
                            f"{sku_res.status_code}"
                        )


                        if sku_res.status_code != 200:

                            print(
                                f"⚠️ SKU {sku_id} "
                                f"HTTP "
                                f"{sku_res.status_code}"
                            )

                            time.sleep(1)

                            continue


                        soup_res = BeautifulSoup(
                            sku_res.text,
                            "html.parser"
                        )


                        script_tag_res = soup_res.find(
                            "script",
                            {
                                "id": "linkStore",
                                "type": "text/json"
                            }
                        )


                        if not script_tag_res:

                            print(
                                f"⚠️ linkStore tidak "
                                f"ditemukan untuk SKU "
                                f"{sku_id}"
                            )

                            time.sleep(1)

                            continue


                        data_json_res = json.loads(
                            script_tag_res.string
                        )


                        product_res = (
                            data_json_res
                            .get("page", {})
                            .get("product", {})
                        )


                        if not product_res:

                            print(
                                f"⚠️ Product data kosong "
                                f"untuk SKU {sku_id}"
                            )

                            time.sleep(1)

                            continue


                        # --------------------------------------------------
                        # CURRENT SKU
                        # --------------------------------------------------

                        current_sku = (
                            product_res.get(
                                "currentSku",
                                {}
                            )
                        )


                        if not current_sku:

                            print(
                                f"⚠️ currentSku kosong "
                                f"untuk SKU {sku_id}"
                            )

                            time.sleep(1)

                            continue


                        actual_sku_id = (
                            current_sku.get(
                                "skuId"
                            )
                        )


                        print(
                            f"Requested SKU : "
                            f"{sku_id}"
                        )


                        print(
                            f"Returned SKU  : "
                            f"{actual_sku_id}"
                        )


                        # --------------------------------------------------
                        # VALIDATE SKU
                        # --------------------------------------------------

                        if str(
                            actual_sku_id
                        ) != str(
                            sku_id
                        ):

                            print(
                                "⚠️ SKU TIDAK COCOK!"
                            )

                            print(
                                f"   Requested: "
                                f"{sku_id}"
                            )

                            print(
                                f"   Returned: "
                                f"{actual_sku_id}"
                            )

                            time.sleep(1)

                            continue


                        # ==================================================
                        # CATEGORY
                        # ==================================================

                        specific_category = (
                            get_category_path(
                                product_res.get(
                                    "parentCategory",
                                    {}
                                )
                            )
                        )


                        # ==================================================
                        # PRODUCT DATA
                        # ==================================================

                        product_id = (
                            product_res
                            .get("productDetails", {})
                            .get("productId")
                        )

                        # ==================================================
                        # PRODUCT DESCRIPTION
                        # ==================================================

                        product_details = product_res.get(
                            "productDetails",
                            {}
                        )

                        product_description = clean_html_text(
                            product_details.get("longDescription")
                        )

                        suggestedUsage = clean_html_text(
                            product_details.get("suggestedUsage")
                        )


                        sku_id_product = (
                            current_sku.get(
                                "skuId"
                            )
                        )


                        product_brand = (
                            current_sku.get(
                                "brandName"
                            )
                        )


                        productName = (
                            current_sku.get(
                                "productName"
                            )
                        )


                        product_image = (
                            "https://www.sephora.com/"
                            "productimages/sku/"
                            f"s{sku_id_product}"
                            "-main-zoom.jpg"
                            "?imwidth=1224"
                        )


                        listPrice = (
                            current_sku.get(
                                "listPrice"
                            )
                        )


                        size_ = (
                            current_sku.get(
                                "size"
                            )
                        )


                        variationType = (
                            current_sku.get(
                                "variationType"
                            )
                        )


                        variationValue = (
                            current_sku.get(
                                "variationValue"
                            )
                        )


                        variationDesc = (
                            current_sku.get(
                                "variationDesc"
                            )
                        )


                        # ==================================================
                        # INGREDIENTS
                        # ==================================================

                        raw_ingredients = (
                            current_sku.get(
                                "ingredientDesc"
                            )
                        )


                        if raw_ingredients:

                            ing_soup = BeautifulSoup(
                                raw_ingredients,
                                "html.parser"
                            )


                            for tag in ing_soup.find_all(
                                [
                                    "p",
                                    "br",
                                    "strong",
                                    "u"
                                ]
                            ):

                                tag.append("\n")


                            clean_ingredients = (
                                ing_soup
                                .get_text()
                                .strip()
                            )


                            clean_ingredients = (
                                "\n\n".join(
                                    line.strip()
                                    for line
                                    in clean_ingredients.splitlines()
                                    if line.strip()
                                )
                            )

                        else:

                            clean_ingredients = None


                        # ==================================================
                        # RATING
                        # ==================================================

                        seo_json_str = (
                            product_res.get(
                                "productSeoJsonLd",
                                ""
                            )
                        )


                        rating = None
                        review_count = None


                        if isinstance(
                            seo_json_str,
                            str
                        ):

                            try:

                                seo_data = json.loads(
                                    seo_json_str
                                )


                                aggregate_rating = (
                                    seo_data.get(
                                        "aggregateRating",
                                        {}
                                    )
                                )


                                rating = (
                                    aggregate_rating.get(
                                        "ratingValue"
                                    )
                                )


                                review_count = (
                                    aggregate_rating.get(
                                        "reviewCount"
                                    )
                                )


                            except json.JSONDecodeError:

                                print(
                                    "⚠️ Gagal decode "
                                    "SEO JSON"
                                )


                        # ==================================================
                        # PRINT
                        # ==================================================

                        print(
                            f"🆔 Product ID: "
                            f"{product_id}"
                        )


                        print(
                            f"🆔 SKU ID: "
                            f"{sku_id_product}"
                        )


                        print(
                            f"⭐ Rating: "
                            f"{format_rating(rating)}"
                        )


                        print(
                            f"📝 Review Count: "
                            f"{format_review_count(review_count)}"
                        )


                        # ==================================================
                        # SAVE
                        # ==================================================

                        all_data.append(
                            {
                                "retailer": "Sephora",

                                "product_group_id":
                                    product_id,

                                "brand":
                                    product_brand,

                                "product_name":
                                    productName,

                                "variant":
                                    variationValue,

                                "variant_type": variationType.replace("size", "").strip() if variationType else "",

                                "shade_description":
                                    variationDesc,

                                "size":
                                    size_,

                                "product_url":
                                    new_sku_url,

                                "skuId":
                                    sku_id_product,

                                "category":
                                    specific_category,

                                "ingredients_raw":
                                    clean_ingredients,

                                "image_url":
                                    product_image,

                                "description":
                                    product_description,

                                "how_to_usage":
                                    suggestedUsage,

                                "price":
                                    listPrice,

                                "rating":
                                    format_rating(
                                        rating
                                    ),

                                "review_count":
                                    format_review_count(
                                        review_count
                                    ),
                            }
                        )


                        # --------------------------------------------------
                        # SKU BERHASIL
                        # --------------------------------------------------

                        seen_sku_urls.add(
                            new_sku_url
                        )


                        sku_processed = True


                        print(
                            f"✅ SKU BERHASIL: "
                            f"{sku_id_product}"
                        )


                        break


                    except Exception as e:

                        print(
                            f"❌ Error SKU "
                            f"{sku_id}: {e}"
                        )


                        time.sleep(1)


                # ==================================================
                # SKU FAILED
                # ==================================================

                if not sku_processed:

                    print(
                        f"❌ SKU {sku_id} "
                        f"gagal setelah "
                        f"{max_retries} percobaan"
                    )


        except Exception as e:

            print(
                f"❌ Gagal mengambil detail "
                f"produk: {e}"
            )

            continue


    # ==========================================================
    # CHECK NEXT PAGE
    # ==========================================================

    if product_count < page_size:

        print("\n")
        print("=" * 70)

        print(
            "🏁 PAGE TERAKHIR TERDETEKSI"
        )

        print(
            f"📄 Page: {current_page}"
        )

        print(
            f"🛍️ Products: "
            f"{product_count}"
        )

        print(
            f"📦 Page Size: "
            f"{page_size}"
        )

        print("=" * 70)

        break


    # ==========================================================
    # NEXT PAGE
    # ==========================================================

    current_page += 1

    print("\n")
    print(
        f"➡️ Melanjutkan ke "
        f"Page {current_page}..."
    )


# ==========================================================
# RESULT
# ==========================================================

print("\n")
print("=" * 70)
print("🎉 SCRAPING SELESAI")
print("=" * 70)

print(
    f"📄 Total pages processed: "
    f"{current_page}"
)

print(
    f"📦 Total SKU data berhasil: "
    f"{len(all_data)}"
)

print(
    f"🔗 Total unique products: "
    f"{len(seen_detail_urls)}"
)

print(
    f"📦 Total unique SKU: "
    f"{len(seen_sku_urls)}"
)


# ==========================================================
# SAVE CSV
# ==========================================================

if all_data:

    filename = (
        f"{slug}_products.csv"
    )


    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=all_data[0].keys()
        )


        writer.writeheader()


        writer.writerows(
            all_data
        )


    print(
        f"\n✅ Data berhasil disimpan ke:"
        f"\n{filename}"
    )

else:

    print(
        "\n⚠️ Tidak ada data yang "
        "berhasil dikumpulkan."
    )

# ==========================================================
# RESULT
# ==========================================================

print("\n")
print("=" * 60)
print("🎉 SCRAPING SELESAI")
print("=" * 60)

print(
    f"📦 Total data SKU berhasil: "
    f"{len(all_data)}"
)

print(
    f"🔗 Total product URL: "
    f"{len(seen_detail_urls)}"
)

print(
    f"📦 Total SKU berhasil: "
    f"{len(seen_sku_urls)}"
)


# ==========================================================
# SAVE CSV
# ==========================================================

if all_data:

    filename = f"{slug}_products.csv"

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=all_data[0].keys()
        )

        writer.writeheader()

        writer.writerows(
            all_data
        )


    print(
        f"\n✅ Data berhasil disimpan ke:"
        f"\n{filename}"
    )

else:

    print(
        "\n⚠️ Tidak ada data yang berhasil "
        "dikumpulkan."
    )