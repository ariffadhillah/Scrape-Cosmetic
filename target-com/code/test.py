import requests

url = "https://islamweb.net/ar/fatwa/"

payload = {}
headers = {
  'Cookie': 'ISLAMWEB_VISITOR_FONT_SELECT=1; PHPSESSID=c1ctltfici27bn02nrdpurs5m0'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
