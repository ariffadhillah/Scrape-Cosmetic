# import requests
# from bs4 import BeautifulSoup
# import time
# import re

# BASE_URL = "https://islamweb.net"
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
# }


# def get_listing_page(startno=0):
#     """Mengambil HTML daftar fatwa berdasarkan parameter startno."""
#     url = f"{BASE_URL}/ar/fatwa/loadmoreisti.php?startno={startno}"
#     resp = requests.get(url, headers=HEADERS, timeout=10)
#     resp.encoding = "utf-8"
#     return resp.text


# def parse_listing(html):
#     """Membaca semua <li> dan mengambil judul + URL dari setiap fatwa."""
#     soup = BeautifulSoup(html, "html.parser")
#     data = []
#     for li in soup.find_all("li"):
#         top_item = li.find("div", class_="top-item")
#         if not top_item:
#             continue

#         a_tag = top_item.find("h2").find("a")
#         if a_tag:
#             title = a_tag.get_text(strip=True)
#             href = BASE_URL + a_tag["href"]
#             data.append({"title": title, "url": href})
#     return data


# def get_fatwa_detail(url):
#     """Mengambil HTML halaman detail fatwa."""
#     resp = requests.get(url, headers=HEADERS, timeout=10)
#     resp.encoding = "utf-8"
#     return resp.text


# # def parse_item_fatwa(html):
# #     """Ambil data dari elemen <div class='item-fatwa'> dan pecah tanggal."""
# #     soup = BeautifulSoup(html, "html.parser")
# #     item = soup.find("div", class_="item-fatwa")
# #     if not item:
# #         return None

# #     # Title
# #     title_tag = item.find("div", class_="top-item").find("h2")
# #     title = title_tag.get_text(strip=True) if title_tag else ""

# #     # Footer
# #     footer = item.find("div", class_="footer-item")
# #     s = footer.find_all("samp") if footer else []

# #     fatwa_id = s[0].find("a").get_text(strip=True) if len(s) > 0 else ""
# #     views = s[1].find("a").get_text(strip=True) if len(s) > 1 else ""
# #     date_raw = s[2].find("a").get_text(strip=True) if len(s) > 2 else ""

# #     # Pisahkan tanggal dengan hati-hati
# #     day = hijri_date = greg_date = ""
# #     try:
# #         day, rest = date_raw.split(" ", 1)
# #         hijri_part, greg_part = rest.split(" - ")
# #         hijri_date = hijri_part.replace("هـ", "").strip()
# #         greg_date = greg_part.replace("م", "").strip()
# #     except Exception:
# #         pass  # kalau format tidak sesuai, biarkan kosong

# #     return {
# #         "title": title,
# #         "fatwa_id": fatwa_id,
# #         "views": views,
# #         "day": day.strip(),
# #         "hijri_date": hijri_date,
# #         "gregorian_date": greg_date,
# #     }

# # import re

# def parse_question_text(html):
#     """Ambil teks pertanyaan dari elemen <div class='mainitem quest-fatwa'>"""
#     soup = BeautifulSoup(html, "html.parser")
#     question_div = soup.find("div", class_="mainitem quest-fatwa")
#     if not question_div:
#         return ""

#     text_div = question_div.find("div", itemprop="text")
#     if text_div:
#         # Gabungkan semua <p> di dalamnya
#         paragraphs = text_div.find_all("p")
#         question_text = " ".join(p.get_text(strip=True) for p in paragraphs)
#         return question_text.strip()
    
#     return ""


# def parse_item_fatwa(html):
#     """Ambil data dari elemen <div class='item-fatwa'> dan pecah tanggal."""
#     soup = BeautifulSoup(html, "html.parser")

#     fatwa_info = parse_item_fatwa(html)
#     question_text = parse_question_text(html)

#     fatwa_info["question_text"] = question_text

#     item = soup.find("div", class_="item-fatwa")
#     if not item:
#         return None

#     # Title
#     title_tag = item.find("div", class_="top-item").find("h2")
#     title = title_tag.get_text(strip=True) if title_tag else ""

#     # Footer
#     footer = item.find("div", class_="footer-item")
#     s = footer.find_all("samp") if footer else []

#     fatwa_id = s[0].find("a").get_text(strip=True) if len(s) > 0 else ""
#     views = s[1].find("a").get_text(strip=True) if len(s) > 1 else ""
#     date_raw = s[2].find("a").get_text(strip=True) if len(s) > 2 else ""

#     # Pisahkan tanggal menggunakan regex agar lebih aman
#     # Contoh: "الأربعاء 15 جمادى الأولى 1447 هـ - 5-11-2025 م"
#     day = ""
#     hijri_date = ""
#     greg_date = ""

#     if date_raw:
#         # Ambil hari (kata Arab pertama sebelum angka)
#         match = re.match(r"^([\u0600-\u06FF]+)\s+(.*)", date_raw)
#         if match:
#             day = match.group(1).strip()
#             rest = match.group(2).strip()
#         else:
#             rest = date_raw.strip()

#         # Pisahkan hijriyah dan masehi
#         if " - " in rest:
#             hijri_part, greg_part = rest.split(" - ", 1)
#             hijri_date = hijri_part.replace("هـ", "").strip()
#             greg_date = greg_part.replace("م", "").strip()
#         else:
#             hijri_date = rest.strip()

#     return {
#         "title": title,
#         "fatwa_id": fatwa_id,
#         "views": views,
#         "day": day,
#         "hijri_date": hijri_date,
#         "gregorian_date": greg_date,
#     }


# def scrape_fatwas(start=0, pages=1, delay=2):
#     """Loop beberapa halaman dan kumpulkan hasil dari setiap URL."""
#     all_fatwas = []

#     for page in range(pages):
#         startno = start + (page * 20)
#         print(f"📄 Mengambil halaman {page+1} (startno={startno})...")

#         html = get_listing_page(startno)
#         listings = parse_listing(html)

#         for item in listings:
#             print(f"🔗 Membuka: {item['url']}")
#             html_detail = get_fatwa_detail(item["url"])
#             meta = parse_item_fatwa(html_detail)

#             if meta:
#                 item.update(meta)
#             else:
#                 item["fatwa_id"] = ""
#                 item["views"] = ""
#                 item["day"] = ""
#                 item["hijri_date"] = ""
#                 item["gregorian_date"] = ""

#             all_fatwas.append(item)

#             print(f"📜 {item['title']}")
#             print(f"📎 Fatwa ID: {item['fatwa_id']}")
#             print(f"📎 views: {item['views']}")
#             print(f"📎 Day: {item['day']}")
#             print(f"📎 hijri date: {item['hijri_date']}")
#             print(f"📎 gregorian date: {item['gregorian_date']}")
#             print("=" * 80)
#             time.sleep(delay)  # jeda agar tidak diblokir

#     return all_fatwas


# if __name__ == "__main__":
#     results = scrape_fatwas(pages=1)  # ambil 1 halaman dulu untuk test

#     print(f"\n✅ Total fatwa diambil: {len(results)}\n")
#     for fatwa in results[:2]:
#         print("Judul:", fatwa["title"])
#         print("URL:", fatwa["url"])
#         print("Fatwa ID:", fatwa["fatwa_id"])
#         print("Days:", fatwa["day"])
#         print("Tanggal Hijriyah:", fatwa["hijri_date"])
#         print("Tanggal Masehi:", fatwa["gregorian_date"])
#         print("-" * 80)



import requests
from bs4 import BeautifulSoup
import time
import re

BASE_URL = "https://islamweb.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
}


def get_listing_page(startno=0):
    """Mengambil HTML daftar fatwa berdasarkan parameter startno."""
    url = f"{BASE_URL}/ar/fatwa/loadmoreisti.php?startno={startno}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    return resp.text


def parse_listing(html):
    """Membaca semua <li> dan mengambil judul + URL dari setiap fatwa."""
    soup = BeautifulSoup(html, "html.parser")
    data = []
    for li in soup.find_all("li"):
        top_item = li.find("div", class_="top-item")
        if not top_item:
            continue

        a_tag = top_item.find("h2").find("a")
        if a_tag:
            title = a_tag.get_text(strip=True)
            href = BASE_URL + a_tag["href"]
            data.append({"title": title, "url": href})
    return data


def get_fatwa_detail(url):
    """Mengambil HTML halaman detail fatwa."""
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    return resp.text


def parse_question_text(html):
    """Ambil teks pertanyaan dari <div class='mainitem quest-fatwa'> tanpa itemprop."""
    soup = BeautifulSoup(html, "html.parser")
    question_div = soup.find("div", class_="mainitem quest-fatwa", itemprop=None)
    if not question_div:
        return ""

    text_div = question_div.find("div", itemprop="text")
    if text_div:
        paragraphs = text_div.find_all("p")
        question_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return question_text.strip()
    
    return ""


def parse_answer_text(html):
    """Ambil teks jawaban dari <div class='mainitem quest-fatwa' itemprop='acceptedAnswer'>"""
    soup = BeautifulSoup(html, "html.parser")
    answer_div = soup.find("div", class_="mainitem quest-fatwa", itemprop="acceptedAnswer")
    if not answer_div:
        return ""

    text_div = answer_div.find("div", itemprop="text")
    if text_div:
        paragraphs = text_div.find_all("p")
        answer_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return answer_text.strip()
    
    return ""


def parse_item_fatwa(html):
    """Ambil data dari elemen <div class='item-fatwa'> dan pecah tanggal."""
    soup = BeautifulSoup(html, "html.parser")

    # Ambil teks pertanyaan & jawaban
    question_text = parse_question_text(html)
    answer_text = parse_answer_text(html)

    item = soup.find("div", class_="item-fatwa")
    if not item:
        return None

    # Title
    title_tag = item.find("div", class_="top-item").find("h2")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Footer
    footer = item.find("div", class_="footer-item")
    s = footer.find_all("samp") if footer else []

    fatwa_id = s[0].find("a").get_text(strip=True) if len(s) > 0 else ""
    views = s[1].find("a").get_text(strip=True) if len(s) > 1 else ""
    date_raw = s[2].find("a").get_text(strip=True) if len(s) > 2 else ""

    # Pisahkan tanggal menggunakan regex
    day = ""
    hijri_date = ""
    greg_date = ""

    if date_raw:
        match = re.match(r"^([\u0600-\u06FF]+)\s+(.*)", date_raw)
        if match:
            day = match.group(1).strip()
            rest = match.group(2).strip()
        else:
            rest = date_raw.strip()

        if " - " in rest:
            hijri_part, greg_part = rest.split(" - ", 1)
            hijri_date = hijri_part.replace("هـ", "").strip()
            greg_date = greg_part.replace("م", "").strip()
        else:
            hijri_date = rest.strip()

    return {
        "title": title,
        "fatwa_id": fatwa_id,
        "views": views,
        "day": day,
        "hijri_date": hijri_date,
        "gregorian_date": greg_date,
        "question_text": question_text,
        "answer_text": answer_text,
    }


def scrape_fatwas(start=0, pages=1, delay=2):
    """Loop beberapa halaman dan kumpulkan hasil dari setiap URL."""
    all_fatwas = []

    for page in range(pages):
        startno = start + (page * 20)
        print(f"📄 Mengambil halaman {page+1} (startno={startno})...")

        html = get_listing_page(startno)
        listings = parse_listing(html)

        for item in listings:
            print(f"🔗 Membuka: {item['url']}")
            html_detail = get_fatwa_detail(item["url"])
            meta = parse_item_fatwa(html_detail)

            if meta:
                item.update(meta)

            all_fatwas.append(item)

            print(f"📜 {item['title']}")
            print(f"📎 Fatwa ID: {item['fatwa_id']}")
            print(f"📎 Day: {item['day']}")
            print(f"📎 Hijri: {item['hijri_date']}")
            print(f"📎 Gregorian: {item['gregorian_date']}")
            print(f"❓ Pertanyaan: {item['question_text'][:100]}...")
            print(f"💬 Jawaban: {item['answer_text'][:100]}...")
            print("=" * 80)
            time.sleep(delay)

    return all_fatwas


if __name__ == "__main__":
    results = scrape_fatwas(pages=1)  # ambil 1 halaman dulu untuk test

    print(f"\n✅ Total fatwa diambil: {len(results)}\n")
    # for fatwa in results[:2]:
    #     print("Judul:", fatwa["title"])
    #     print("Fatwa ID:", fatwa["fatwa_id"])
    #     print("Pertanyaan:", fatwa["question_text"][:200])
    #     print("Jawaban:", fatwa["answer_text"][:200])
    #     print("-" * 80)

    for fatwa in results[:2]:
        print("URL:", fatwa["url"])
        print("Judul:", fatwa["title"])
        print("Fatwa ID:", fatwa["fatwa_id"])
        print("Days:", fatwa["day"])
        print("Tanggal Hijriyah:", fatwa["hijri_date"])
        print("Tanggal Masehi:", fatwa["gregorian_date"])
        print("Pertanyaan:", fatwa["question_text"][:200])
        print("Jawaban:", fatwa["answer_text"][:200])
        print("-" * 80)
