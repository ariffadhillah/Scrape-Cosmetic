import requests
from bs4 import BeautifulSoup
import time
import re
import csv

BASE_URL = "https://islamweb.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
}

def extract_category(soup):
    breadcrumb = soup.find("ol", {"itemtype": "http://schema.org/BreadcrumbList"})
    if not breadcrumb:
        return None
    names = breadcrumb.find_all("span", {"itemprop": "name"})
    if not names:
        return None
    return names[-1].get_text(strip=True)

def get_listing_page(startno=0):
    url = f"{BASE_URL}/ar/fatwa/loadmoreisti.php?startno={startno}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    return resp.text

def parse_listing(html):
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
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    return resp.text

def parse_question_text(html):
    soup = BeautifulSoup(html, "html.parser")
    # cari div pertanyaan tanpa itemprop acceptedAnswer
    question_div = soup.select_one("div.mainitem.quest-fatwa:not([itemprop='acceptedAnswer'])")
    if not question_div:
        # fallback: cari yang class gabungan
        question_div = soup.select_one("div.mainitem.quest-fatwa")
        # if it's the acceptedAnswer one, we later will treat accordingly
    if not question_div:
        return ""
    text_div = question_div.find("div", itemprop="text")
    if text_div:
        paragraphs = text_div.find_all("p")
        question_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return question_text.strip()
    return ""

def parse_answer_text(html):
    soup = BeautifulSoup(html, "html.parser")
    answer_div = soup.find("div", class_="mainitem quest-fatwa", itemprop="acceptedAnswer")
    if not answer_div:
        # fallback: find by itemprop only
        answer_div = soup.find(attrs={"itemprop": "acceptedAnswer"})
    if not answer_div:
        return ""
    text_div = answer_div.find("div", itemprop="text")
    if text_div:
        paragraphs = text_div.find_all("p")
        answer_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return answer_text.strip()
    return ""

def parse_mufti_names(html):
    """Ambil hanya nama mufti dari tab_content tab_3 itemslist."""
    soup = BeautifulSoup(html, "html.parser")
    tab_div = soup.find("div", class_="tab_content tab_3 itemslist")
    if not tab_div:
        return []
    mufti_tags = tab_div.find_all("a", class_="categorynem")
    muftis = [a.get_text(strip=True) for a in mufti_tags if a.get_text(strip=True)]
    return muftis

def parse_item_fatwa(html):
    soup = BeautifulSoup(html, "html.parser")

    question_text = parse_question_text(html)
    answer_text = parse_answer_text(html)
    mufti_names = parse_mufti_names(html)
    category = extract_category(soup)

    item = soup.find("div", class_="item-fatwa")
    if not item:
        return None

    title_tag = item.find("div", class_="top-item").find("h2")
    title = title_tag.get_text(strip=True) if title_tag else ""

    footer = item.find("div", class_="footer-item")
    s = footer.find_all("samp") if footer else []

    fatwa_id = s[0].find("a").get_text(strip=True) if len(s) > 0 else ""
    views = s[1].find("a").get_text(strip=True) if len(s) > 1 else ""
    date_raw = s[2].find("a").get_text(strip=True) if len(s) > 2 else ""

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

    # NOTE: do NOT include "url" here — URL exists in the outer 'item' dict
    return {
        "title": title,
        "fatwa_id": fatwa_id,
        "views": views,
        "day": day,
        "hijri_date": hijri_date,
        "gregorian_date": greg_date,
        "question_text": question_text,
        "answer_text": answer_text,
        "mufti_names": mufti_names,
        "category": category,
    }

def scrape_fatwas(start=0, pages=1, delay=2):
    all_fatwas = []
    for page in range(pages):
        startno = start + (page * 20)
        print(f"📄 Mengambil halaman {page+1} (startno={startno})...")
        html = get_listing_page(startno)
        listings = parse_listing(html)
        if not listings:
            print("⚠️ Tidak ada listing di halaman ini.")
            break

        for item in listings:
            print(f"🔗 Membuka: {item['url']}")
            html_detail = get_fatwa_detail(item["url"])
            meta = parse_item_fatwa(html_detail)
            if meta:
                item.update(meta)  # item already has 'url' and 'title' (listing)
            all_fatwas.append(item)
            print(f"📜 {item.get('title','')}")
            if meta and meta.get("mufti_names"):
                print("👳‍♂️ Muftis:")
                for m in meta["mufti_names"]:
                    print(f"  - {m}")
            print("=" * 80)
            time.sleep(delay)
    return all_fatwas

if __name__ == "__main__":
    filename = "fatwa_results.csv"
    # cek apakah file sudah ada
    try:
        with open(filename, "r", encoding="utf-8-sig"):
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    # contoh: ambil 2 halaman (ubah sesuai kebutuhan)
    results = scrape_fatwas(pages=1)

    print(f"\n✅ Total fatwa diambil: {len(results)}\n")

    # tulis/append ke CSV dengan urutan kolom sesuai header
    with open(filename, mode="a", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Original link", "Title", "Category", "Fatwa ID", "Days", "Hijri Date",
                "Gregorian Date", "Question text", "Full answer text", "Mufti's Name(s)"
            ])

        for fatwa in results:
            writer.writerow([
                fatwa.get("url", ""),
                fatwa.get("title", ""),
                fatwa.get("category") or "-",
                fatwa.get("fatwa_id", ""),
                fatwa.get("day", ""),
                fatwa.get("hijri_date", ""),
                fatwa.get("gregorian_date", ""),
                fatwa.get("question_text", "").replace("\n", " ").strip(),
                fatwa.get("answer_text", "").replace("\n", " ").strip(),
                "\n".join(fatwa.get("mufti_names", [])) if fatwa.get("mufti_names") else "-"
            ])

    print(f"\n📁 Data berhasil ditambahkan ke file: {filename}")
