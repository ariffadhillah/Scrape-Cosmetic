import requests
import json
import math
import urllib.parse


headers_template = {
    'User-Agent': 'Mozilla/5.0',
    'content-type': 'application/json',
    'apollographql-client-name': 'ulta-graph',
    'x-ulta-dxl-query-id': 'NonCachedPage',
    'x-ulta-graph-type': 'query',
    'x-ulta-graph-sub-type': 'noncachedpage',
    'x-ulta-graph-module-name': 'ProductListingResults',
}

# for page in range(jumlah_halaman):

    # encode URL page
path = "https://www.ulta.com/shop/makeup/lips?page=1&loadPreviousIndex=1&gti=eb9ae70c-311f-41dd-be0b-149654cd6d19&loginStatus=anonymous&retailerVisitorId=20d40221-124b-4304-a433-c63d766b8479&breakpoint=XL"
encoded_path = urllib.parse.quote(path, safe='')

    # MASUKKAN KE DALAM GRAPHQL QUERY
graphql_url = (
    "https://www.ulta.com/dxl/graphql?"
    "ultasite=en-us&user-agent=gomez&query="
    "query%20NonCachedPage(%24stagingHost%3A%20String%2C%20%24previewOptions%3A%20JSON%2C%20%24moduleParams%3A%20JSON)%20%7B"
    "%20%20Page%3A%20NonCachedPage(stagingHost%3A%20%24stagingHost%2C%20previewOptions%3A%20%24previewOptions%2C%20moduleParams%3A%20%24moduleParams%2C%20url%3A%20%7Bpath%3A%20%22"
    + encoded_path +
    "%22%7D%2C%20contentId%3A%20%22cb7c0efb-8772-4abc-9be0-4dfaf1b625ee%22)%20%7Bcontent%20customResponseAttributes%20meta%20__typename%7D%7D"
    "&operationName=NonCachedPage"
    "&variables=%7B%22moduleParams%22%3A%7B%22gti%22%3A%22eb9ae70c-311f-41dd-be0b-149654cd6d19%22%2C%22loginStatus%22%3A%22anonymous%22"
    "%2C%22retailerVisitorId%22%3A%2220d40221-124b-4304-a433-c63d766b8479%22%2C%22breakpoint%22%3A%22XL%22%7D%7D"
)

    # header khusus per page
headers = headers_template.copy()
headers["x-ulta-graph-page-url"] = path

r = requests.get(graphql_url, headers=headers)
data = r.json()
print(data)

urls = []
content = data["data"]["Page"]["content"]

def extract_urls(mod):
    if "items" in mod:
        for item in mod["items"]:
            try:
                u = item["action"]["url"]
                if u:
                    urls.append(u)
            except:
                pass

extract_urls(content)

if "modules" in content:
    for mod in content["modules"]:
        extract_urls(mod)

print(f"\n=== PAGE  → {len(urls)} URL ===")
for u in urls:
    print(u)



# def get_all_urls():
#     import requests
#     import json
#     import math
#     import urllib.parse

#     total_url = 11
#     per_halaman = 64
#     jumlah_halaman = math.ceil(total_url / per_halaman)

#     headers_template = {
#         'User-Agent': 'Mozilla/5.0',
#         'content-type': 'application/json',
#         'apollographql-client-name': 'ulta-graph',
#         'x-ulta-dxl-query-id': 'NonCachedPage',
#         'x-ulta-graph-type': 'query',
#         'x-ulta-graph-sub-type': 'noncachedpage',
#         'x-ulta-graph-module-name': 'ProductListingResults',
#     }

#     all_urls = []

#     for page in range(jumlah_halaman):

#         path = f"https://www.ulta.com/shop/makeup/lips?page={page}&loadPreviousIndex=1&gti=eb9ae70c-311f-41dd-be0b-149654cd6d19&loginStatus=anonymous&retailerVisitorId=20d40221-124b-4304-a433-c63d766b8479&breakpoint=XL"
#         encoded_path = urllib.parse.quote(path, safe='')

#         graphql_url = (
#             "https://www.ulta.com/dxl/graphql?"
#             "ultasite=en-us&user-agent=gomez&query="
#             "query%20NonCachedPage(%24stagingHost%3A%20String%2C%20%24previewOptions%3A%20JSON%2C%20%24moduleParams%3A%20JSON)%20%7B"
#             "%20%20Page%3A%20NonCachedPage(stagingHost%3A%20%24stagingHost%2C%20previewOptions%3A%20%24previewOptions%2C%20moduleParams%3A%20%24moduleParams%2C%20url%3A%20%7Bpath%3A%20%22"
#             + encoded_path +
#             "%22%7D%2C%20contentId%3A%20%22cb7c0efb-8772-4abc-9be0-4dfaf1b625ee%22)%20%7Bcontent%20customResponseAttributes%20meta%20__typename%7D%7D"
#             "&operationName=NonCachedPage"
#             "&variables=%7B%22moduleParams%22%3A%7B%22gti%22%3A%22eb9ae70c-311f-41dd-be0b-149654cd6d19%22%2C%22loginStatus%22%3A%22anonymous%22"
#             "%2C%22retailerVisitorId%22%3A%2220d40221-124b-4304-a433-c63d766b8479%22%2C%22breakpoint%22%3A%22XL%22%7D%7D"
#         )

#         headers = headers_template.copy()
#         headers["x-ulta-graph-page-url"] = path

#         r = requests.get(graphql_url, headers=headers)
#         data = r.json()

#         content = data["data"]["Page"]["content"]

#         def extract_urls(mod):
#             if "items" in mod:
#                 for item in mod["items"]:
#                     try:
#                         u = item["action"]["url"]
#                         if u:
#                             all_urls.append("https://www.ulta.com" + u)
#                     except:
#                         pass

#         extract_urls(content)

#         if "modules" in content:
#             for mod in content["modules"]:
#                 extract_urls(mod)

#         print(f"PAGE {page} → {len(all_urls)} URL total")

#     return all_urls


# # Jika file dijalankan langsung
# if __name__ == "__main__":
#     urls = get_all_urls()
#     for u in urls:
#         print(u)
