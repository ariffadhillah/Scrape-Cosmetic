# import requests
# import json
# import re

# urltest="dior-dior-addict-lip-maximizer-gloss-prod259640088"

# url = "https://www.neimanmarcus.com/p/" + urltest

# payload = {}
# headers = {
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
#   'Accept': 'application/json, text/plain, */*',
#   'Accept-Language': 'en-US,en;q=0.5',
#   'Accept-Encoding': 'gzip, deflate, br, zstd',
#   'Referer': 'https://www.neimanmarcus.com',
#   'x-datadome-clientid': 'dkJFrOuaw~LLnabbjxMDxt4MeOXSxNGlLCeCJCBwtLRf7AlnwjnawkRujmFKUzpE~pCsoyHd8c6IFDaX87GzTLCK0M4OecL0PTURLp_pUN1PQEwsMQYCsNzqpvUtK0zE',
#   'X-Feature-Toggles': '{ "USE_PH": false, "USE_CM4": false,"PDP_MASTERSTYLE_GROUP_PRODUCTS": true,"USE_PRIVATE_LAUNCH": true,"USE_DISPLAYABLE_BETA": false, "USE_CM4_DBU": false, "PH_BACKORDER_FLAG": true, "USE_SELLABLE_STORE": false}',
#   'Sec-Fetch-Dest': 'empty',
#   'Sec-Fetch-Mode': 'cors',
#   'Sec-Fetch-Site': 'same-origin',
#   'Connection': 'keep-alive',
#   'Cookie': 'df_cid=df1cf8f7-36dc-4a9f-a180-306edb4ececc; m_bid=fb.2.1764318285.6060987951717347; _cplid=1764317770718313; _optuid=1764317770718271; ucaProfileData={%22firstName%22:%22%22%2C%22securityStatus%22:%22Anonymous%22%2C%22universal_customer_id%22:%22%22%2C%22logged_in_status%22:false%2C%22customer_registered%22:false%2C%22profile_type%22:%22customer%22%2C%22customer_segment%22:%220%22%2C%22countryPreference%22:%22US%22%2C%22currencyPreference%22:%22USD%22%2C%22localeUrl%22:%22/en-us%22}; datadome=dkJFrOuaw~LLnabbjxMDxt4MeOXSxNGlLCeCJCBwtLRf7AlnwjnawkRujmFKUzpE~pCsoyHd8c6IFDaX87GzTLCK0M4OecL0PTURLp_pUN1PQEwsMQYCsNzqpvUtK0zE; optimizelyEndUserId=oeu1764317779405r0.24951854071271473; AMCV_5E85123F5245B3520A490D45%40AdobeOrg=-330454231%7CMCIDTS%7C20445%7CMCMID%7C47024772310441187458936910627314394081%7CMCAID%7CNONE%7CMCOPTOUT-1766486939s%7CNONE%7CvVersion%7C3.1.2; _gcl_au=1.1.2102926558.1764317799; optimizelySession=0; s_ecid=MCMID%7C47024772310441187458936910627314394081; QuantumMetricUserID=4e472d2a930234efd19657ea5b7f4e10; dt_gender=W; _attn_=eyJ1Ijoie1wiY29cIjoxNzY0MzE3OTU3MjA2LFwidW9cIjoxNzY0MzE3OTU3MjA2LFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjY0NThmOGVmZDQxNTQ5MDRiZjgwODFhOGRhMDkxY2RhXCJ9In0=; __attentive_id=6458f8efd4154904bf8081a8da091cda; __attentive_cco=1764317957208; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Dec+23+2025+15%3A49%3A22+GMT%2B0700+(Indochina+Time)&version=202507.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=6349372a-2fce-4d0e-a4bf-26d515e01531&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1&AwaitingReconsent=false&geolocation=ID%3BAC; utag_main=v_id:019ac98b968800128060aea2312e05050008100d0086e^$_n:6^$_e:3^$_s:0^$_t:1766481905491^$vapi_domain:neimanmarcus.com^$dc_visit:6^$ses_id:1766479737488%3Bexp-session^$_n:2%3Bexp-session^$_revpage:product%20detail%3Bexp-1766483357107^$_revpagetype:product%20detail%3Bexp-1766483357107^$dc_event:2%3Bexp-session^$dc_region:ap-east-1%3Bexp-session; OptanonAlertBoxClosed=2025-12-23T08:49:22.401Z; _ga_1B8WTDSBDF=GS2.1.s1766479744^$o9^$g1^$t1766479757^$j47^$l0^$h0; _ga=GA1.1.800365987.1764318331; bopsSearchTerm=24188; checkout_continuity_service=341188ff-c4c7-4950-9450-5af344df44ce; bluecoreNV=false; __spdt=cc874b9d73934e6bb09604db56182925; smartDash=ae2ab475-498a-442e-bd9e-79d2337fa0cc; _cc=AWiUdRchSnnNM1i%2BZniuBudd; _cid_cc=AWiUdRchSnnNM1i%2BZniuBudd; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22qg6qsBtbEX1JXoCE4Uyu%22%2C%22expiryDate%22%3A%222026-12-23T08%3A49%3A24.557Z%22%7D; _scid=Zp4OuEBNaTQbH1cD47ha1YKjyjoWHEVh; _sctr=1%7C1766336400000; _tt_enable_cookie=1; _ttp=01KB4S3A0BBESSSQXRAW2N1TK9_.tt.1; ttcsid_C92S54BC77U6S6FRSI5G=1766479765956::2a6dJinHUy0l77K_AWj1.6.1766480454481.1; ttcsid=1766479765956::-wYNTSHr_1AUgBCHw3ho.6.1766480454481.0; cstmr=%7B%22customerId%22%3A%22df1cf8f7-36dc-4a9f-a180-306edb4ececc%22%2C%22cmdId%22%3A%22%22%2C%22isLoggedin%22%3Afalse%2C%22isGuest%22%3Afalse%2C%22chEm%22%3A%22%22%7D; s_vnum=1767200400127%26vn%3D4; nm_throttling=DT3; pdp_mfa=true; NMOCARTCHECKOUT=NEW; NMOMYACCOUNT=NEW; UCAACCOUNTOVERVIEW=NEW; _efca=SklEANuI5FkT+WQE3c7Tig==; __attentive_dv=1; _optanalytics=nmsss0006:b,nmbc0001:b,nmnv0001:b; _optanalytics_mfa=tl284:b,tl345:b,tl313:b,tl335:a,tl347:b,tl310:a,tl300:b,tl327:b,ng1:b,tl384-2:a,npdp15:b,nmvto0001:b; load_times=5.66_7.89; dt_gender_placement=undefined; pt_ck=undefined; _fs_cd_cp_pRdRgnTnF68pCV2F=AblzDO4cGeEcKr6L7KArz3agLAW5n5yzkJC_N0L203J8H2OeJQ_ZbhlTrLARtb3CSFe6BSIWRvofji38pvfWaxn5-3zOZdftvElArbSE_kJRbJUFJyoZveSJP1WILCNRJSI2EdOSn9bSGFlqg2ljuA==; s_invisit=true; s_ips=423; s_tp=3892; AMCVS_5E85123F5245B3520A490D45%40AdobeOrg=1; s_cc=true; guestUser.df1cf8f7-36dc-4a9f-a180-306edb4ececc.AccessToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik4yUm1NVEZtTlRBdFpHVTNPQzB4TVdWaUxXSmhPREF0TURJME1tRmpNVE13TURBMElBbz0ifQ.eyJzdWIiOiJkZjFjZjhmNy0zNmRjLTRhOWYtYTE4MC0zMDZlZGI0ZWNlY2MiLCJ0eXBlIjoiZ3Vlc3QiLCJpcCI6IjE2Ny44Mi4xNDMuMTAwIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwiYnJhbmQiOiJOTSIsImlhdCI6MTc2NjQ3OTc0MywiZXhwIjoxNzY2NDgzMzQzLCJhdWQiOiJuZWltYW5tYXJjdXMuY29tIiwiaXNzIjoiaHR0cHM6Ly9ndWVzdC1vYXV0aC5uZWltYW5tYXJjdXNjbG91ZC5jb20ifQ.WSyDaGMAuwEwJvxpPFr6NZgaTaHKAnXU5VTPMbDUK6QaKwpmIwcMRQhh1b9xObeln22LkM0AehYt-HmONIVLqS3JEfBgCSEOKRcu5XFpzUlxPjgOF0iLqCEkDBbfdvB6FLsdcJhJFWCpQBpEae9sbqnrrrfP-MdKxY3s-2devgXVa5rVSB1OuErM09k4UlhxsYsLqlRfQo4BYRDP4cOaIICXEDCBRwQFWAlggqnbDMMyPBkzcG4FPQpqPL9YCiYp7ozw5jMWLsYMeKmJRYM5Ji79P4Ld06KzwSIRD7J6ESEIgWPCg95fL93R0U4OOWv9IgOa5wz-OnxLbqK_x9nfTZfH7dwu3uwqOty9JjyB74o1tCiDK_NkAULOAVo0tiXG4LaE3BocKuUwVkOwy71Fpg-ZmkhxF79LSntNEWnywE3tCUMV1mlgxHunrooXh77T2bVD4kVNfMfk6XaHAGItsEl6LC8frXIYiSfuQHWePi3YIhL2ktKS-Aa5JMZjRYvFgZV0eAQOvy2kwW9RlpqVLsjx63iXdwbDHAshHYtUnLyf6r5IjKspKovYTHf1l0hN28utXCFQKmEP0lpknJmpM6aBUs4249qpW4mqyCCyJt4oPAcIJ6HbGHnLjhOzS0ZtmWfms8BduwA8IAa07rpSjGylK1Z_MYqlUMBFBsbqZDg; guestUser.df1cf8f7-36dc-4a9f-a180-306edb4ececc.RefreshToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik4yUm1NVEZtTlRBdFpHVTNPQzB4TVdWaUxXSmhPREF0TURJME1tRmpNVE13TURBMElBbz0ifQ.eyJ0eXBlIjoiZ3Vlc3QiLCJzdWIiOiJkZjFjZjhmNy0zNmRjLTRhOWYtYTE4MC0zMDZlZGI0ZWNlY2MiLCJpcCI6IjE2Ny44Mi4xNDIuODkiLCJ0b2tlbl91c2UiOiJyZWZyZXNoIiwiYnJhbmQiOiJOTSIsImlhdCI6MTc2NDMxNzg2MSwiZXhwIjoxNzcyMDkzODYxLCJhdWQiOiJuZWltYW5tYXJjdXMuY29tIiwiaXNzIjoiaHR0cHM6Ly9ndWVzdC1vYXV0aC5uZWltYW5tYXJjdXNjbG91ZC5jb20ifQ.EuJqLk0DJIL-p8hrpVHFNevb2PgXLjvBL6F_1Uz6HCl_yUxAwFfMfnJmsWyH3oGycEvdNOGYp-_ovydoLee2Kv7ZkM90yxZdUv_IkZKIwGIUz_dKK6BKAG7mYarMm6nO8EQ-vr_8iYoCUxSYaxRkRTN9nQzbZmCnPbNuuXbV0jsTkftKsASSoklwuxvD2LQgTuu_OZlCXRzS9fCMOylt4zOlVC7WSBw5HFruNo6JVdmU2uX901qOIy9vMb4wct5vPO_xmCtZ7AuzwHFilTPxb0gQsQ-TLfTZ1fpyWYK3_F1smhWsQPE7rKhcuIWygRMBU6rzKjyRGSXJEuY6ukvz08g2iaJOBUtt3qY9788gDp2b2qFb_QAwcOTmCcuMxm_Yg9WFBz0r0ndachtx4uN1Rzz2K4aHHr-drWRQhJu8BuAf7BZVfNbeC8WwVuVpeCcZGWk1t_M4_yt-C1Xg4Z6URSycuO046cpKUrp2wqEHhO6Xv5qU_HAwZ6BqqIxRXdXJpgkFalXlyZv-_mqHlnuZ0PxMJWX-qiWlVtIJqn5ym6uPMzkp8hrOoZkypVf7IaXzLcKjW2gY0_SI5ZH-qa7C6F_23QtV8qGr-b1-U6nNHqS20C8LdSA2y474x0z7SSTq95ENz716xyC8ZCiS3HftrALlbUoTc8IOvYG362mdBq4; guestUser.df1cf8f7-36dc-4a9f-a180-306edb4ececc.TokenType=Bearer; guestUser.df1cf8f7-36dc-4a9f-a180-306edb4ececc.Sub=df1cf8f7-36dc-4a9f-a180-306edb4ececc; guestUser.df1cf8f7-36dc-4a9f-a180-306edb4ececc.ExpiresAt=1766483342955; QuantumMetricSessionID=179a38a5f38536d43fd77055df901f89; s_ppv=https%253A%252F%252Fwww.neimanmarcus.com%252Fp%252Ff"{urltest}"%2C23%2C11%2C911%2C2%2C9; mp_neiman_marcus_mixpanel=%7B%22distinct_id%22%3A%20%2219ac99179e39d0-03c3f4dd08c019-8505025-100200-19ac99179e41ba3%22%2C%22bc_persist_updated%22%3A%201764318345701%7D; _uetsid=5d33f240df2a11f086c58741f168d12c; _uetvid=dbe4bfa0cc3311f0958f9f7dcb873f63; __attentive_session_id=5911ce99f4f447c795ba6c4aac40ed8d; _scid_r=jR4OuEBNaTQbH1cD47ha1YKjyjoWHEVhrqBnEg; __attentive_pv=1; __attentive_ss_referrer=ORGANIC; TTSVID=917cb97a-f684-4d6f-bf32-fe86370cf549; s_sq=nmgincglobalprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dproduct%252520detail%2526link%253D016%252520Shimmer%252520Nude%2526region%253Dbuy-block-container%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dproduct%252520detail%2526pidt%253D1%2526oid%253Dfunctionrg%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DSUBMIT; _efca=Kz4z9oxjKY3cOVByzODcLg==',
#   'Priority': 'u=0',
#   'TE': 'trailers'
# }

# response = requests.request("GET", url, headers=headers, data=payload)

# # print(response.text)


# html = response.text

# pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
# match = re.search(pattern, html, re.DOTALL)

# if not match:
#     raise Exception("❌ __NEXT_DATA__ tidak ditemukan di response")

# next_data_raw = match.group(1)

# # parse ke dict Python
# next_data = json.loads(next_data_raw)

# # tampilkan (contoh, biar tidak banjir terminal)
# print(json.dumps(next_data, indent=2))





# # with open("test-1.json", "w", encoding="utf-8") as f:
# #     f.write(json.dumps(next_data, indent=2))

# # print("✅ response.text disimpan apa adanya ke response_raw.json")



from bs4 import BeautifulSoup
import requests
import json
import re




# url = "https://www.neimanmarcus.com/p/maison-francis-kurkdjian-baccarat-rouge-540-extrait-de-parfum-2-4-oz-prod203310173?childItemId=NMC4LTY_&msid=4186589&navpath=cat000000_cat000285&page=0&position=0"
# url = "https://www.neimanmarcus.com/p/dior-dior-addict-lip-maximizer-gloss-prod259640088"
# url = "https://www.neimanmarcus.com/p/bvlgari-eau-parfumee-the-blanc-body-shower-gel-10-1-oz-prod282740027?childItemId=NMC6CFD_&msid=5065063&navpath=cat000000_cat000285&page=1&position=104"

url = "https://www.neimanmarcus.com/p/dior-dior-addict-lip-glow-oil-prod229290078"

datadome = "PPjxEES23nTMbpvD6jqkg9EqxviuZLrgph1FpBKMnIUbUNeicIAErhA4WjOPoRK44Ga97yPlFh6FMzM_QG717hAFdtPLtulYhav7FB_aM3qccxfWAvNxcrZUxDIy6h4Z; Max-Age=31536000; Domain=.neimanmarcus.com; Path=/; Secure; SameSite=Lax"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": url,
    "Origin": "https://www.neimanmarcus.com",
    "x-datadome-clientid": datadome,
    "X-Feature-Toggles": '{ "USE_PH": false, "USE_CM4": false,"PDP_MASTERSTYLE_GROUP_PRODUCTS": true,"USE_PRIVATE_LAUNCH": true,"USE_DISPLAYABLE_BETA": false, "USE_CM4_DBU": false, "PH_BACKORDER_FLAG": true, "USE_SELLABLE_STORE": false}',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}

cookies = {
    "df_cid": "df1cf8f7-36dc-4a9f-a180-306edb4ececc",
    "m_bid": "fb.2.1764318285.6060987951717347",
    "_cplid": "1764317770718313",
    "_optuid": "1764317770718271",
    "datadome": datadome,
    "optimizelyEndUserId": "oeu1764317779405r0.24951854071271473",
    "_ga": "GA1.1.800365987.1764318331",
    "_ga_1B8WTDSBDF": "GS2.1.s1766484035$o10$g0$t1766484035$j60$l0$h0",
    "QuantumMetricUserID": "4e472d2a930234efd19657ea5b7f4e10",
    "__attentive_id": "6458f8efd4154904bf8081a8da091cda",
    "OptanonAlertBoxClosed": "2025-12-23T10:00:59.401Z",
    "OptanonConsent": "isGpcEnabled=0&datestamp=Tue+Dec+23+2025+17:01:00+GMT+0700&version=202507.1.0",
    "utag_main": "v_id:019ac98b968800128060aea2312e05050008100d0086e",
    "s_cc": "true",
    "s_ppv": url,
    "nm_throttling": "DT3",
    "pdp_mfa": "true",
}


response = requests.get(
    url,
    headers=headers,
    cookies=cookies,
    timeout=20
)

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)


html = response.text

pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
match = re.search(pattern, html, re.DOTALL)

if not match:
    raise Exception("❌ __NEXT_DATA__ tidak ditemukan di response")

next_data_raw = match.group(1)

# parse ke dict Python
next_data = json.loads(next_data_raw)


def extract_active_price(product_data):
    for child in product_data.get("childProducts", []):
        price = child.get("price")
        if price:
            return {
                "retail": price.get("retailPrice"),
                "currency": price.get("currencyCode")
            }
    return None

def build_price_sources(product_data):
    price_map = {}

    # 1️⃣ childProducts (harga spesifik SKU)
    for child in product_data.get("childProducts", []):
        pid = child.get("id")
        price = child.get("price", {})

        if pid and price.get("retailPrice"):
            price_map[pid] = price.get("retailPrice")

    # 2️⃣ root product price
    root_price = (
        product_data.get("price", {}).get("retailPrice")
    )

    # 3️⃣ price range fallback
    range_price = (
        product_data.get("priceRange", {}).get("lowPrice")
    )

    return price_map, root_price, range_price


def map_sku_to_price(product_data):
    result = {}

    for child in product_data.get("childProducts", []):
        price = child.get("price", {}).get("retailPrice")

        options = child.get("options", {}).get("productOptions", [])
        for opt in options:
            if opt.get("label") == "size":
                for val in opt.get("values", []):
                    sku_id = val.get("skuId")
                    result[sku_id] = price

    return result

product_data = next_data["props"]["pageProps"]["productData"]
price = extract_active_price(product_data)

price_map, root_price, range_price = build_price_sources(product_data)

for sku in product_data.get("skus", []):
    sku_id = sku.get("id")
    product_id = sku.get("productId")
    size = sku.get("size", {}).get("name")

    # PRIORITAS PRICE
    price_data = (
        price_map.get(product_id)
        or root_price
        or range_price
    )

    print("SKU ID :", sku_id)
    print("Price  :", price_data)
    print("-" * 40)

