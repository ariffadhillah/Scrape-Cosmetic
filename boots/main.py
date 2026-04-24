# import requests
# import json
# import time

# url = "https://www.boots.com/online/api/search/v2/multiple-query/uk"

# payload = json.dumps({
#   "query": "",
#   "indices": {
#     "products": {
#       "paging": {
#         "index": 0,
#         "size": 44
#       },
#       "criteria": {
#         "category": [
#           "beauty & skincare",
#           "makeup",
#           "face"
#         ]
#       },
#       "sortBy": "mostRelevant"
#     }
#   },
#   "returnHits": True,
#   "returnSuggestions": False,
#   "returnFacets": True,
#   "returnChanel": False,
#   "searchRequired": True,
#   "adRequired": True,
#   "adParams": {
#     "pageId": "viewCategoryApiDesktop",
#     "eventType": "viewCategory",
#     "environment": "desktop",
#     "customerId": "",
#     "category": "1595015>1595036>1595098"
#   }
# })

# headers = {
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
#   'Accept': '*/*',
#   'Accept-Language': 'en-US,en;q=0.5',
#   'Accept-Encoding': 'gzip, deflate, br, zstd',
#   'content-type': 'application/json',
#   'x-client-id': '9c5ed6f8b3d1ec6191ae260ae7daac',
#   'x-search-usertoken': '457ce85f-b9f3-41b6-b132-08691f8ff0ec',
#   'x-user-token': '457ce85f-b9f3-41b6-b132-08691f8ff0ec',
#   'Origin': 'https://www.boots.com',
#   'Connection': 'keep-alive',
#   'Referer': 'https://www.boots.com/beauty/makeup/face',
#   'Cookie': 'WC_PERSISTENT=vIYHLiRu5ClwzlB%2Bm5VOBpZ61PtnWIR3k4us8c1Q3F8%3D%3B2025-09-05+04%3A45%3A35.949_1757043935943-2360_11352_-1002%2C-1%2CGBP_11352; UserType=G; DISPLAYNAME=guest; x-search-usertoken=457ce85f-b9f3-41b6-b132-08691f8ff0ec; OptanonConsent=isIABGlobal=false&datestamp=Thu+Sep+25+2025+15%3A08%3A29+GMT%2B0700+(Indochina+Time)&version=6.14.0&hosts=&consentId=101230b7-221e-4608-87a8-02431d45c631&interactionCount=1&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2CBG79%3A1&geolocation=%3B&AwaitingReconsent=false; OneTrustPrevious=isIABGlobal=false&datestamp=Thu+Sep+25+2025+15:08:05+GMT+0700+(Indochina+Time)&version=6.14.0&hosts=&consentId=101230b7-221e-4608-87a8-02431d45c631&interactionCount=1&landingPath=NotLandingPage&groups=1:1,2:1,3:1,4:1,BG79:1&geolocation=; gig_bootstrap_3_tgWZjPmf4Y0eeO0Okf-Cl3OjuaTNMW5aSIYEi0dY66KmwQXWyItwHA1Kb_uGmB9r=account_ver4; OptanonAlertBoxClosed=2025-09-05T03:45:20.487Z; mbox=PC^#a90ffa7dea594e17b3c460f23d9483ef.38_0^#1822032468|session^#fc74a2b8251d4ad28a0647c7cd00d09c^#1758874148; _gcl_au=1.1.1934184293.1757043921; _ga=GA1.1.177724597.1757043916; _ga_C3KVJJE2RH=GS2.1.s1758872271^$o11^$g0^$t1758872285^$j46^$l0^$h0; ATCurrentSessionID=7422dcef-39d6-4dc9-b4c2-2b232b45362b; bt_lastClick=other; _mibhv=anon-1757043924934-4050210286_6980; lantern=d307c447-14fe-4c1f-8bff-af3001642c26; _taggstar_vid=c1f34905-8a0a-11f0-8b7f-99ec76f2a30c; _taggstar_exps={"sp":{"id":"","group":""}}; _ga_1QMWXFX88F=GS2.1.s1758814171^$o10^$g0^$t1758814171^$j60^$l0^$h1415379423; _pin_unauth=dWlkPU1qWTVOakUzT0dVdFlXRmlaQzAwT0dFekxXRTFOemt0WkdZMk5EQXdORGRoTURrMQ; AMCV_591A299B5B5F2D0F0A495E91%40AdobeOrg=-1124106680%7CMCIDTS%7C20357%7CMCMID%7C70175513930240434105988775747159006370%7CMCAID%7CNONE%7CMCOPTOUT-1758797121s%7CNONE%7CvVersion%7C5.2.0%7CMCAAMLH-1757899550%7C3%7CMCAAMB-1758787231%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-20347; _scid=UhPp0-rfNIU1NBDchRJeyVQopVQOByIf; _gtmeec=eyJlbSI6ImUzYjBjNDQyOThmYzFjMTQ5YWZiZjRjODk5NmZiOTI0MjdhZTQxZTQ2NDliOTM0Y2E0OTU5OTFiNzg1MmI4NTUiLCJleHRlcm5hbF9pZCI6IjcwMTc1NTEzOTMwMjQwNDM0MTA1OTg4Nzc1NzQ3MTU5MDA2MzcwIn0%3D; __qca=P1-92aaabac-604b-4732-8f90-e8b42219663a; _fbp=fb.1.1757043927716.41529981018679585; s_tslv=1758787709962; s_vnc365=1790323542121%26vn%3D7; _tt_enable_cookie=1; _ttp=01K4BZNAV3Q1YWCM83CCNNNXP3_.tt.1; ttcsid_C8CBIFSN9V2G1TDUK3HG=1758789838684::9b6Eo9Skfbx8ShWyxk9s.9.1758789838684.0; ttcsid=1758787553367::g-8PvsZC5k5SxItKlDj4.7.1758787712637.0; _cs_c=0; _cs_id=5fc42854-9d76-aa92-8b23-ca53272c76b6.1757043929.13.1758814161.1758814161.1755512350.1791207929438.1.x; _sctr=1%7C1758474000000; DataLayerUserObject=-1002%7C%7CNew%7Cfalse%7Cfalse%7C%7C%7C%7CoNIL6IrlplWmH7KKXpnQwjl; adsDataLayerUserObject=-1002%7C%7CNew%7Cfalse%7Cfalse%7C%7C%7C%7C; BVBRANDID=861073db-0cf6-4982-95f7-2bbaafdc078c; s_fid=75D301CF6EC44AD0-326D8A010E4C0BF6; AAM_UUID=70323247655109316336046337714614952321; visid_incap_2478461=i6aT3BhTQs6dznKYUaukqM9C1mgAAAAAQUIPAAAAAAAKerscrHjqwzAGMZFrAUUm; QueueITAccepted-SDFrts345E=EventId%3Dbootsoutage2025uk%26QueueId%3D97e2d1df-6719-4a71-a6ba-7715dc31c0f3%26IsCookieExtendable%3Dtrue%26Expires%3D1758873485%26Hash%3Db5157a57b95d45689168ecd4c2cb111381778ba515ed8f309ce05459e9d8a3c6; _scid_r=XJPp0-rfNIU1NBDchRJeyVQopVQOByIfQAprJw; _uetsid=7cee98b099e611f091aa0d8c9e5391fd|gwyokk|2|fzm|0|2094; _uetvid=c398d4e08a0a11f0a2a725bd669df067|n2ef97|1758814169007|1|1|bat.bing.com/p/insights/c/j; nlbi_949787=4fpRAiV5mlUMaXoqR2Yj1QAAAABHSgAO5er4i+QGOtwlp1xJ; incap_ses_1747_949787=TGbmd8ubu0pv9PWeopc+GMRC1mgAAAAAQgu7/6h5T/ZKW5VvxMcGPg==; incap_ses_1364_2478461=2bhRDA8+uR2XAb4nFeftEs9C1mgAAAAABFsBLna2auV0QlJOxRR8CQ==; s_cc=true; _ALGOLIA=anonymous-ef16083d-f3fb-4ee5-9204-924fde4fd512; at_check=true; DataLayerLoginOption=Guest; adsDataLayerLoginOption=Guest; WC_PERSISTENT=HBS%2Fsn%2BI2sr%2FDL4JfO%2FHC4Y6slKhRTzikOKJqfMzpMI%3D%3B2025-09-08+03%3A51%3A36.884_1757299896884-58693_0; incap_ses_1700_949787=D4AeEXabSVMh0sjHgJ2XF0pD1mgAAAAAu66gDxRwZhG6ImUuTIRBXA==; nlbi_949787=ct0fUwiiA390V98oR2Yj1QAAAADon4dsjoNEK5bEQgeK8YtD; ADRUM_BT=R:40|i:3560379|g:d103b360-9a18-4182-a3d7-77b84bf134d28626|e:0|n:boots-prod_9a448c8a-6542-45a5-a186-0971b3b9ee8a',
#   'Sec-Fetch-Dest': 'empty',
#   'Sec-Fetch-Mode': 'cors',
#   'Sec-Fetch-Site': 'same-origin',
#   'TE': 'trailers'
# }



# # try:
# #     data = response.json()  # langsung dapat dict
# # except json.JSONDecodeError:
# #     print("Response bukan JSON valid!")
# #     print(response.text)
# #     exit()

# # # Cetak JSON rapi untuk inspeksi
# # print(json.dumps(data, indent=2))

# # # Ambil list hits
# # hits = data["products"]["hits"]

# # for product in hits:
# #     if isinstance(product, dict):
# #         referenceUri = f'https://www.boots.com{product.get("referenceUri")}'
# #         # brand = product.get("brand")
# #         print(referenceUri)
# #     else:
# #         print("Warning: product is not a dict", product)




# all_urls = []
# page_index = 0
# page_size = 44  # sesuai "size"
# total_products = None

# while True:
#     payload = {
#         # sesuaikan dengan payload aslinya
#         "index": page_index,
#         "size": page_size
#     }
    
#     response = requests.post(url, headers=headers, data=payload)
#     data = response.json()
    
#     if total_products is None:
#         total_products = data["products"]["paging"]["total"]
#         print(f"🔎 Total produk: {total_products}")
    
#     hits = data["products"]["hits"]
#     if not hits:
#         break
    
#     for product in hits:
#         referenceUri = f'https://www.boots.com{product.get("referenceUri")}'
#         all_urls.append(referenceUri)
#         print(referenceUri)
    
#     page_index += 1
    
#     if page_index * page_size >= total_products:
#         break
    
#     time.sleep(1)  # delay biar aman

# print(f"\n✅ Total URL terkumpul: {len(all_urls)}")



import requests
import json
import time

url = "https://www.boots.com/online/api/search/v2/multiple-query/uk"

headers = {
    "User-Agent": "Mozilla/5.0",
    "content-type": "application/json",
    "x-client-id": "9c5ed6f8b3d1ec6191ae260ae7daac",
    "x-search-usertoken": "457ce85f-b9f3-41b6-b132-08691f8ff0ec",
    "x-user-token": "457ce85f-b9f3-41b6-b132-08691f8ff0ec",
    "Origin": "https://www.boots.com",
    "Referer": "https://www.boots.com/beauty/makeup/face"
}

all_urls = []
page_index = 0
page_size = 44
total_products = None

while True:
    payload = {
        "query": "",
        "indices": {
            "products": {
                "paging": {
                    "index": page_index,
                    "size": page_size
                },
                "criteria": {
                    "category": ["beauty & skincare", "makeup", "face"]
                },
                "sortBy": "mostRelevant"
            }
        },
        "returnHits": True,
        "returnSuggestions": False,
        "returnFacets": True,
        "returnChanel": False,
        "searchRequired": True,
        "adRequired": True,
        "adParams": {
            "pageId": "viewCategoryApiDesktop",
            "eventType": "viewCategory",
            "environment": "desktop",
            "customerId": "",
            "category": "1595015>1595036>1595098"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    data = response.json()

    if total_products is None:
        total_products = data["products"]["paging"]["total"]
        print(f"🔎 Total produk: {total_products}")

    hits = data["products"]["hits"]
    if not hits:
        break

    for product in hits:
        referenceUri = f'https://www.boots.com{product.get("referenceUri")}'
        all_urls.append(referenceUri)
        print(referenceUri)

    page_index += 1

    if page_index * page_size >= total_products:
        break

    time.sleep(1)

print(f"\n✅ Total URL terkumpul: {len(all_urls)}")
