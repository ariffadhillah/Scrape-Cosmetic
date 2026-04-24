import requests
import json

url = "https://www.ulta.com/dxl/graphql?ultasite=en-us&user-agent=gomez&query=query%20NonCachedPage(%24stagingHost%3A%20String%2C%20%24previewOptions%3A%20JSON%2C%20%24moduleParams%3A%20JSON)%20%7B%0A%20%20Page%3A%20NonCachedPage(stagingHost%3A%20%24stagingHost%2C%20previewOptions%3A%20%24previewOptions%2C%20moduleParams%3A%20%24moduleParams%2C%20url%3A%20%7Bpath%3A%20%22https%3A%2F%2Fwww.ulta.com%2Fshop%2Fmakeup%2Flips%3Fpage%3D3%26loadPreviousIndex%3D2%22%7D%2C%20contentId%3A%20%22cb7c0efb-8772-4abc-9be0-4dfaf1b625ee%22)%20%7B%0A%20%20%20%20content%0A%20%20%20%20customResponseAttributes%0A%20%20%20%20meta%0A%20%20%20%20__typename%0A%20%20%7D%0A%7D%0A&operationName=NonCachedPage&variables=%7B%22moduleParams%22%3A%7B%22gti%22%3A%22eb9ae70c-311f-41dd-be0b-149654cd6d19%22%2C%22loginStatus%22%3A%22anonymous%22%2C%22retailerVisitorId%22%3A%2220d40221-124b-4304-a433-c63d766b8479%22%2C%22breakpoint%22%3A%22XL%22%7D%7D"

payload = {}
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0',
  'Accept': '*/*',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Referer': 'https://www.ulta.com/shop/makeup/lips?page=2',
  'content-type': 'application/json',
  'apollographql-client-name': 'ulta-graph',
  'x-ulta-dxl-query-id': 'NonCachedPage',
  'x-ulta-graph-page-url': f'https://www.ulta.com/shop/makeup/lips?page=1&loadPreviousIndex=2&gti=eb9ae70c-311f-41dd-be0b-149654cd6d19&loginStatus=anonymous&retailerVisitorId=20d40221-124b-4304-a433-c63d766b8479&breakpoint=XL',
  'x-ulta-graph-type': 'query',
  'x-ulta-graph-sub-type': 'noncachedpage',
  'x-ulta-graph-module-name': 'ProductListingResults',
  'x_ulta_site': 'CA',
  'x-ulta-client-country': 'US',
  'x-ulta-client-locale': 'en-US',
  'x-ulta-client-channel': 'web',
  'x-forwarded-proto': 'https',
  'traceparent': '00-E384D8D8C658506DD0ABEBA08F7DCD82-55279BFEE93C516D-01',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'Connection': 'keep-alive',
  'Cookie': 'ulta-context=dsp; __ruid=20d40221-124b-4304-a433-c63d766b8479; X_ULTA_VISITOR_ID=20d40221-124b-4304-a433-c63d766b8479; rxVisitor=1764320987354J45C8KJRF2OHI40FUUAU4QF0974KV9G4; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Nov+29+2025+22%3A30%3A26+GMT%2B0700+(Indochina+Time)&version=202508.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=2df988c1-90f5-42d4-80a6-b16d161a90fb&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0007%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&intType=1&geolocation=ID%3BAC; ULTA_DSP_RT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjcwMjIyMzg2NzAsImlhdCI6MTc2NDQzMDIzODY3MCwiYXVkIjoid3d3LnVsdGEuY29tIiwiaXNzIjoidWx0YS5jb20iLCJzdWIiOiJlYjlhZTcwYy0zMTFmLTQxZGQtYmUwYi0xNDk2NTRjZDZkMTkiLCJkZXZpY2VJZCI6IjM2MmJmNDUzLTBjYjAtNDJkMi1iZTcyLTg1Y2EzMDUzMWU5NyIsInN0YXlTaWduZWRJbiI6ZmFsc2UsInNvZnRMb2dpblN0YXR1cyI6IkFub24iLCJtZmFDbGFpbXMiOmZhbHNlLCJhdXRoMFNlc3Npb25JZCI6IiJ9.R5BhbKByK3Erlkhy7q-h2iO0EA0hYi-Z3sdV_GXvy6k; utag_main=v_id:019ac9bd0e260021b9c698e54ff205050001500d0086e^$_n:9^$_e:34^$_s:0^$_t:1764432202907^$vapi_domain:ulta.com^$ses_id:1764429528384%3Bexp-session^$_n:2%3Bexp-session; AMCV_C218F16F55CC57607F000101%40AdobeOrg=-1124106680%7CMCIDTS%7C20421%7CMCMID%7C45040531602482281350189668948275384841%7CMCAID%7CNONE%7CMCOPTOUT-1764437461s%7CNONE%7CvVersion%7C5.2.0; _scid=LCwdaNk5YwIUHvOzBP-qpC8x2eqvJAVO; _caid=7b8aa4a5-93f6-4f11-b348-1e6e4898bb7b; _pin_unauth=dWlkPU1HTmxOV1U0TkRndE9URXlOaTAwTTJabExUazVNakV0TlRKbVlqbGpaRE0yT1RJMA; __tvpa=77748ac1b8336981d247dd74434080a9; s_ecid=MCMID%7C45040531602482281350189668948275384841; kndctr_C218F16F55CC57607F000101_AdobeOrg_identity=CiY0NTA0MDUzMTYwMjQ4MjI4MTM1MDE4OTY2ODk0ODI3NTM4NDg0MVIRCMKD9s2sMxgBKgRTR1AzMAPwAcz%2Dx%5FysMw%3D%3D; _tt_enable_cookie=1; _ttp=01KB4VV0HFDC0S4NQT8RBNDPD4_.tt.1; ttcsid_CQ2N213C77U8BDE394M0=1764430251585::WS1Vc4JD1pkZsPcFIUfe.3.1764430402119.0; ttcsid=1764430251585::EGWELjde2eXV3vkIeH4z.11.1764430402119.0; _lc2_fpi=93b6d570cf50--01kb4vv1fqdj2hm15knq7drvnr; _bti=%7B%22app_id%22%3A%22ulta-salon%22%2C%22bsin%22%3A%22E2ds1sBNpADxdJGLJQSaG4meD6ljQLUiJhRrmaI75KAPMDUsz%2BW59bku1r2qmhpxM2hA5oaXYeFOvH7Yyv1Ylw%3D%3D%22%2C%22is_identified%22%3Afalse%7D; s_nr=1764430261879-Repeat; _sctr=1%7C1764262800000; _fbp=fb.1.1764321248395.35867040049622920; RoktRecogniser=4433fb1e-326b-4a6f-8c83-753587c74c23; _ga=GA1.1.962577876.1764321498; _gid=GA1.2.882512736.1764321498; kampyle_userid=e419-499c-7d63-7373-8d07-cf47-8218-15c8; kampyleUserSession=1764430284516; kampyleSessionPageCounter=1; kampyleUserSessionsCount=16; QuantumMetricUserID=afe238706b6bdb284d05311e1cd8ebb6; _gcl_au=1.1.389858529.1764321508; _ga_LKM7RC8LP8=GS2.1.s1764429533^$o11^$g1^$t1764430400^$j60^$l0^$h0; OptanonAlertBoxClosed=2025-11-28T09:20:01.498Z; __gads=ID=e65992cb37741587:T=1764321656:RT=1764425784:S=ALNI_Mbp_uXZW4kAHqtPu3TMEWNccOnWWg; __gpi=UID=000011be43303119:T=1764321656:RT=1764425784:S=ALNI_MaU6FywRX3ECZxHLNHQpvqyxz2tDA; __eoi=ID=c778ea553fa88071:T=1764321656:RT=1764425784:S=AA-AfjYJCCtQEMe_icqZNf-JaD5t; salsify_session_id=991c119c-b269-42cd-a32d-e22751f6b551; apt_pixel=eyJkZXZpY2VJZCI6IjVhMmRmMWZmLTc0MzUtNGVkMy05OWQyLWMwYjZkMTJjYThlNyIsInVzZXJJZCI6IiIsImV2ZW50SWQiOjM5LCJsYXN0RXZlbnRUaW1lIjoxNzY0NDI1NzY5NTE4fQ==; cto_bundle=fhBfdV9KbkhabkJsQzJ4WG52YUxHekxsOGp6RmtaVlclMkJwUlEzeFlSUFBMYXJSdGsxSTdRNGI3TjZaejBIT1JuRyUyQk84THl5bm83UjNDaTJSYjg5bmhrSVRBTWIlMkJ1eDBVZUZzZVBINjlVb0xJQUFBRmxCOGdlVDdLR0NhUDQlMkJMU0kzeGxBTnhVRm1EWWtlSmdDcXpEJTJCZjg5aFlHcTUxVlJXR2FoMjY3Y1hpTEVHJTJCSlElM0Q; IR_PI=cfb94ee3-cc3b-11f0-9eb0-670c10aa4a06%7C1764323178747; RT="z=1&dm=ulta.com&si=7a38d4bd-d2c6-4c66-abfd-bd3a7136ed12&ss=mikg6ndg&sl=1&tt=1tce&rl=1&ld=1tcg"; __pr.98w=7vGGs3hfwE; akaalb_alb_www_ulta=~op=WWW_ULTA_SITE_A:SiteA_Failover|~rv=22~m=SiteA_Failover:0|~os=6e40862a2abd586d46d773cd430ecffc~id=5495bfa4b6bad615514f9dd0a1f116a0; akavpau_vp-www-ulta-com=1764430580~id=55d4db18cc551762119aeb6ff61f1f76; ULTA_SITE=CA; X_ULTA_SITE=CA; akaalb_alb_www_dsp=~op=WWW_DSP_SITE_CA:Prod_DSP_SiteA_Origin_Central|~rv=97~m=Prod_DSP_SiteA_Origin_Central:0|~os=6e40862a2abd586d46d773cd430ecffc~id=94b77b879a438b285d1b7c71bbacbf37; dtCookie=v_4_srv_33_sn_20RML0BHIDSONK326CAJCQ6RDO9UPS2I_app-3A6fe4664190660d01_1_ol_0_perc_100000_mul_1_rcs-3Acss_1; dtPC=33^$430208884_849h-vPACKMNHKKFEIPHVHTRWAMMWPMCOQKKCH-0e0; rxvt=1764432086971|1764429718907; dtSa=-; User-Agent=gomez; ULTASITE=en-us; ULTA_DSP_AT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjQ0MzM4Mzg2NzAsImlhdCI6MTc2NDQzMDIzODY3MCwiYXVkIjoid3d3LnVsdGEuY29tIiwiaXNzIjoidWx0YS5jb20iLCJzdWIiOiJlYjlhZTcwYy0zMTFmLTQxZGQtYmUwYi0xNDk2NTRjZDZkMTkiLCJkZXZpY2VJZCI6IjM2MmJmNDUzLTBjYjAtNDJkMi1iZTcyLTg1Y2EzMDUzMWU5NyIsImF1dGhTdGF0dXMiOiJBbm9uIiwic2Vzc2lvbklkIjoiMTA4MzQwNzYtOTE3MS00MTdlLWE1OTQtZWE5Mzg0NDYwM2IwIiwiYXV0aDBTZXNzaW9uSWQiOiIifQ.7djSktgEtmdNM3fSjdohnbnxuCE-7nyAGKBP9IIshko; IR_gbd=ulta.com; IR_3037=1764430232138%7C123240%7C1764430232138%7C%7C; utag_ck_gtid=undefined; powerreviews_reviews=rouge allure liquid velvet ultrawear intense matte liquid lip colour : chanel; distinct_id=a0de6d2d-c498-5f0e-9a8e-7498291536d9; session_id=a53dae3d-b4ac-5dfc-9e74-635a8ba60b29; _li_dcdm_c=.ulta.com; _lc2_fpi_js=93b6d570cf50--01kb4vv1fqdj2hm15knq7drvnr; AMCVS_C218F16F55CC57607F000101%40AdobeOrg=1; s_cc=true; s_sq=%5B%5BB%5D%5D; QuantumMetricSessionID=8b5ee6efa86084a3cbfbda709ac7d5f3; gpv=makeup%3Alips; kndctr_C218F16F55CC57607F000101_AdobeOrg_cluster=sgp3; AKA_A2=A; _rdt_uuid=1764321505185.a3e95595-8deb-495f-a64a-fc33c1a22ee8; _bts=25bfe498-fc01-4093-e48c-b903cbb0baa2; _scid_r=M6wdaNk5YwIUHvOzBP-qpC8x2eqvJAVOz-e38A; _cavisit=19ad03d6a7a|; kampyleUserPercentile=14.732434098365754; _gat_gtag_UA_143014378_1=1; dtCookie=v_4_srv_33_sn_20RML0BHIDSONK326CAJCQ6RDO9UPS2I_perc_100000_ol_0_mul_1_app-3A6fe4664190660d01_1_rcs-3Acss_1; ULTASITE=en-us; ULTA_DSP_AT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjQ0MzQwNjQ4MzEsImlhdCI6MTc2NDQzMDQ2NDgzMSwiYXVkIjoid3d3LnVsdGEuY29tIiwiaXNzIjoidWx0YS5jb20iLCJzdWIiOiJlYjlhZTcwYy0zMTFmLTQxZGQtYmUwYi0xNDk2NTRjZDZkMTkiLCJkZXZpY2VJZCI6IjM2MmJmNDUzLTBjYjAtNDJkMi1iZTcyLTg1Y2EzMDUzMWU5NyIsImF1dGhTdGF0dXMiOiJBbm9uIiwic2Vzc2lvbklkIjoiMTA4MzQwNzYtOTE3MS00MTdlLWE1OTQtZWE5Mzg0NDYwM2IwIiwiYXV0aDBTZXNzaW9uSWQiOiIifQ.8FI8R_ChDXPOKME_OiOzfK0wiK2kQaOGvYY6rUEeTdM; ULTA_DSP_RT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjcwMjI0NjQ4MzEsImlhdCI6MTc2NDQzMDQ2NDgzMSwiYXVkIjoid3d3LnVsdGEuY29tIiwiaXNzIjoidWx0YS5jb20iLCJzdWIiOiJlYjlhZTcwYy0zMTFmLTQxZGQtYmUwYi0xNDk2NTRjZDZkMTkiLCJkZXZpY2VJZCI6IjM2MmJmNDUzLTBjYjAtNDJkMi1iZTcyLTg1Y2EzMDUzMWU5NyIsInN0YXlTaWduZWRJbiI6ZmFsc2UsInNvZnRMb2dpblN0YXR1cyI6IkFub24iLCJtZmFDbGFpbXMiOmZhbHNlLCJhdXRoMFNlc3Npb25JZCI6IiJ9.PLPsLajPwEhaLQrBm7Pg6xQpiHC8fGk-ELbRsI2_lgg; ULTA_SITE=CA; User-Agent=gomez; X_ULTA_SITE=CA; X_ULTA_VISITOR_ID=a6434bef-edeb-428d-9e4b-3de1996915a6; __ruid=a6434bef-edeb-428d-9e4b-3de1996915a6; akavpau_vp-www-ulta-com=1764430765~id=8a3ea8e22af74cd33339ff4f6f0f2af8',
  'Priority': 'u=4'
}

response = requests.get(url, headers=headers)
data = response.json()

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

# 1. items langsung
extract_urls(content)

# 2. kalau ada modules
if "modules" in content:
    for mod in content["modules"]:
        extract_urls(mod)

print("Total:", len(urls))
for u in urls:
    print(u)

