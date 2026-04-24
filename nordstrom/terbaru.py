# import csv
# import requests
# import time
# import os

# BASE_API = "https://www.nordstrom.com/api/browse/query/browse/beauty/makeup/face"
# BASE_URL = "https://www.nordstrom.com"
# CSV_FILE = "Face-Makeup-nordstrom_product_urls.csv"

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
#     'Accept': '*/*',
#     'Accept-Language': 'en-US,en;q=0.5',
#     'Accept-Encoding': 'gzip, deflate, br, zstd',
#     'Referer': 'https://www.nordstrom.com/browse/beauty/makeup/face',
#     'ads-nord-context-id': '0d89a417-9495-447b-a2ce-bc28a1f65235',
#     'cardmember': 'Non-CardMember',
#     'content-type': 'application/json',
#     'country-code': 'ID',
#     'currency-code': 'USD',
#     'customerauthstate': 'anonymous',
#     'eventcustomer': '{"idType":"SHOPPER_ID","id":"529d1d36a0f445c1a409b18c71ddf5f3"}',
#     'eventsource': '{"channel":"FULL_LINE","channelCountry":"US","platform":"WEB"}',
#     'experimentid': 'd0d37a21-4c45-41b2-bace-232fd6310382',
#     'experiments': '{"experiments":[],"optimizely":{"experiments":[{"n":"pdp_leapfrog_notes_display","v":"notesDisplay","p":"FULL_LINE_DESKTOP"},{"n":"gwp_upsell_in_bag","v":"gwp_upsell","p":"FULL_LINE_DESKTOP"},{"n":"pdp_chx_paypal_bnpl_v2","v":"paypalSB2","p":"FULL_LINE_DESKTOP"},{"n":"phdr_item_exchange","v":"default","p":"FULL_LINE_DESKTOP"},{"n":"pdp_leapfrog_notes_in_bag_v2","v":"notes_display","p":"FULL_LINE_DESKTOP"},{"n":"checkout_shopping_bag_express_payments_apple_pay","v":"apple_pay","p":"FULL_LINE_DESKTOP"},{"n":"checkout_global_header__on_order_confirmation","v":"global_header_on_oc","p":"FULL_LINE_DESKTOP"},{"n":"desktop_leapfrog_holdout","v":"leapfrogEligible","p":"FULL_LINE_DESKTOP"},{"n":"hp_leapfrog_cj1_canvas_web_v2","v":"default","p":"FULL_LINE_DESKTOP"},{"n":"hp_leapfrog_outfit_of_the_day_v3","v":"hpOutfitOfTheDayV3","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"chx_qr_code_in_wallet_hp","v":"qrCodeEnabled","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"sbn_departmenttiles","v":"departmentTiles","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"rec_tray_ab_test_tracking_page","v":"new_position","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"cam_guest_auth_ext","v":"extended","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"aynid","v":"default","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"phdr_store_returns_widget_ab_test","v":"additionalInstructions","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"desktop_icon_addcard_primary_approval_backend","v":"yes_consent_required","p":"JWN"},{"n":"desk_nmn_homepageherocomponent","v":"test2","p":"JWN"},{"n":"mow_iframe_modal","v":"iframe","p":"JWN"},{"n":"desktop_web_eta_styling","v":"eta_styling","p":"JWN"},{"n":"firstshopper_exposed_search_desktop_v1","v":"searchbar","p":"JWN"},{"n":"cat_appointment_skip_staff_selection_step","v":"off","p":"JWN"},{"n":"desk_sbn_brand_disco_conversion","v":"sbnbrandconv","p":"JWN"},{"n":"desktop_f2dd_variable_promise","v":"expedited","p":"JWN"},{"n":"credit_td_easy_rack","v":"off","p":"JWN"},{"n":"desktop_sbn_assisted_plp_enticements_nord_v1","v":"enticements","p":"JWN"},{"n":"desktop_iframe_modal","v":"iframe","p":"JWN"},{"n":"sierra_chat_do_no_harm_experiment","v":"sierra_chat_on","p":"JWN"},{"n":"desktop_nordstrom_forgot_pw_wallet_dump","v":"forgot_pw_wallet_dump","p":"JWN"},{"n":"desk_nordstrom_experiment_id","v":"correct_experiment_id","p":"JWN"},{"n":"credit_td_easy_employee","v":"off","p":"JWN"},{"n":"desk_ncom_loyalty_updates","v":"loyaltyverify_shopnow","p":"JWN"},{"n":"phdr_order_pickup_cancel","v":"on","p":"JWN"},{"n":"reco-mow_assisted_plp_datasimplification_nord_v1","v":"moduleredesign","p":"JWN"},{"n":"desktop_sbn_assisted_plp_reviews_nord_v1","v":"simplifyreviews","p":"JWN"},{"n":"desktop_sbn_assisted_plp_hearts_nord_v2","v":"hearts","p":"JWN"},{"n":"se_nord_desktop_filters_ui_grs","v":"dynamic_filters","p":"JWN"},{"n":"desk_hp_xdiv_fall_fashion","v":"default","p":"JWN"},{"n":"desk_ncom_checkout_otp_v2","v":"otp_checkout","p":"JWN"},{"n":"desk_sbn_brand_disco_mlp","v":"dbrandmlp","p":"JWN"},{"n":"ios_icon_addcard_primary_approval_backend","v":"yes_consent_required","p":"JWN"},{"n":"desktop_leapfrog_holdout_v1","v":"leapfrogeligible","p":"JWN"},{"n":"reco_text_context_ncom_web_pdp2","v":"MULTIMODAL","p":"JWN"},{"n":"reco_text_context_ncom_web","v":"default","p":"JWN"},{"n":"reco-desktop_assisted_plp_datasimplification_nord_v1","v":"moduleredesign","p":"JWN"},{"n":"credit_td_easy_nordstrom","v":"on","p":"JWN"},{"n":"desk_sbn_leapfrog_brands","v":"brandboutiquepoc","p":"JWN"},{"n":"ncom_desk_aaaa_test","v":"off","p":"JWN"},{"n":"se_nord_convo_search_desktop_tabbed_v2_grs","v":"conversational_search_tabbed","p":"JWN"},{"n":"desktop_paypal_braintree","v":"braintree","p":"JWN"},{"n":"hp_leapfrog_loyalty_signin_discovery_desktop","v":"signindiscovery","p":"JWN"},{"n":"icon_addcard_primary_approval","v":"no_consent_required","p":"JWN"},{"n":"phdr_opensearch_v2","v":"on","p":"JWN"}],"id":"d0d37a21-4c45-41b2-bace-232fd6310382"},"user_id":"d0d37a21-4c45-41b2-bace-232fd6310382"}',
#     'feature-flags': 'isbranddiscoveryenabled,iscanvas2enabledsbn,iseditorserviceenabledforsbn,isheartingenabled,isproductpinningenabled,issponsoredadsforbrowseactive,issponsoredadsforsearchactive',
#     'is-security-scan': 'false',
#     'isauxexperiment': 'true',
#     'ismobile': 'false',
#     'isproductdropexperiment': 'true',
#     'issanityexperiment': 'true',
#     'isusereventqualified': 'false',
#     'loyaltylevel': 'non-member',
#     'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIzMDUxMjEiLCJhcCI6IjMwMjQ2MTM4NiIsImlkIjoiODhlZTBmNzI3NmNiZGVjNyIsInRyIjoiOTU2NmVmZjI2NmY4ZDg3ZTFjMTczODc1NjMxZWYwOTgiLCJ0aSI6MTc2Nzc2ODEzMjA4MywidGsiOiIyMjkxMTU0In19',
#     'nord-authentication-status': 'UNRECOGNIZED',
#     'nord-channel-brand': 'NORDSTROM',
#     'nord-client-id': 'APP01196',
#     'nord-context-id': 'fa394f8d-1ce0-4b99-b736-b17e3bd2ac79',
#     'nord-country-code': 'US',
#     'nord-customer-experience': 'DESKTOP_WEB',
#     'nord-postalcode': '22153',
#     'nord-request-id': 'ePmcpzCdTT2qrn-UaY3MZg',
#     'nord-shopper-bearer-token': '',
#     'nordapiversion': '1.0',
#     'tracecontext': '0a3447b6-127e-4632-a3b8-77c5057dd89e',
#     'traceparent': '00-9566eff266f8d87e1c173875631ef098-88ee0f7276cbdec7-01',
#     'tracestate': '2291154^@nr=0-1-2305121-302461386-88ee0f7276cbdec7----1767768132083',
#     'true-client-ip': '182.3.5.68',
#     'true-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
#     'userauthentication': 'UNRECOGNIZED',
#     'userid': '529d1d36a0f445c1a409b18c71ddf5f3',
#     'userid-hashed': '',
#     'userqualificationtype': '-1',
#     'visitorstatus': 'New Customer',
#     'x-shopper-token': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MjlkMWQzNmEwZjQ0NWMxYTQwOWIxOGM3MWRkZjVmMyIsImF1ZCI6Imd1ZXN0IiwiaXNzIjoibm9yZHN0cm9tLWd1ZXN0LWF1dGgiLCJleHAiOjIwODMyOTEwODYsInJlZnJlc2giOjE3Njc3NzI2ODYsImp0aSI6IjVkZTM2YTQzLWJkNGUtNGJjZi05YzJmLTg4ZjRjOWE4NDBkYyIsImlhdCI6MTc2Nzc1ODI4Nn0.YC8iW-g-PN1L4E9IQQZYAqPBqwZ2CpF2T17L3Cw2cbAjcD1-U9Xvd6r74MYdS92HujzifyP5E8Bzswv6CTlBHbXfjLj9u83OL2Hu6VfepyAc42HpPoTqD6psLk34hjq0FWf5CvHFMM0LF-WTCvwGlYx_OqsDBRXRCC7w0Y9lz3XgTkLwGYvJ85Kz6hltdGf722bI80R59M7s6cEiBKSPHVeqTfLL3c5xCuR5Dso4vT75GD0q-4k08M1ode7GR7LorAooUyzzZCE7PuF3DRwoMaY-HMsat8mrY9WXNMVHnit8takdQobNdtdsUlpSYOYd_RnWjWmfnu2ZmTf1XE7fh7zlsNLszE4t1YhJ6Pq26LYwOAt34qN8k3ShYYuNbWgUX5S0Z-NIjxI701yKf1-cxfGn8pHDuknfnG2Ck7sOCXCT00Vj8CweJPQMe3vewGZ1ZmZMkubJdxLOeX6SJRngkeFoJwl2oFKI5j76Uub8oOU-gQtYej-B4uVYBq0pXIYzARFkLWkK7vXHuuGIgHCipFgbfd9420K3JYFodU-2v7ANSGn-Md5cPF2rU8PBM5bmZL7lMKRyJh8hr5uRi3hXmx1sKHSTY4D6l9xgQnMBPuaQmieYd7G-dOAqT1KLEUHf5pA_Hf9_qqyTg4yiPPyk9DE-Z-V5mqtFht-Dt7xENnI',
#     'X-y8S6k3DB-f': 'A4jampabAQAAo5jeEw2UXMkV6ltuZ7kM11V_WUw5EBfyhYbju4CxTnk3mfxwAbYDBUScuJhhwH8AAEB3AAAAAA==',
#     'X-y8S6k3DB-b': 'pd7ha9',
#     'X-y8S6k3DB-c': 'AMASgZabAQAAiqHaS2qz01YxdUkv6g70_aGqBvPW-Du2pu62MYrZRZ571GHc',
#     'X-y8S6k3DB-d': 'ABaAhIDBCKGFgQGAAYIQgISigaIAwBGAzv5Czi_33weK2UWee9Rh3AAAAAAvXY3EAJCNcSLI6afY7c867p1to90',
#     'X-y8S6k3DB-z': 'q',
#     'X-y8S6k3DB-a': 'hMPWcocUVVVGEB_a70YSZ051dy5B_kg6WQWWNXA2X47237yMw=10MTLXYcPU26QZwt-0S5zt5YTNHRbRLu=T2KrKPuvHhRJoRCUCNPuRnfei1rRXnygfJp1MztwO_7PJzHg8Y1yw3C2fF_2BFUCj8gG6SQWA7j7ByjIwYrS6yEM=Y7-JYq0=QTgClPy6rWkycbzUBfU6Ys2toU9r8tsD23Oc=YZmgfhflE651R3t8RZj5wsJ_v=HvskwMevmtBt8oyAMFHW3vngJADr0nWwwRd3t3Q68CqcILNkyBnyIb6Fr5bFIGH5hom6ImwVEsMAVCPcQzHobhlSL3UUUNHDSvB1OEo1TfAgS-9wSHTXgae1Lc99UyCWS_CSn3CEBfQm4q=n3rndcRJMZ-nTONeAM02aeFKHns2gNv5BzAnPVVl=fMcXOF_-_mWcs9Dfj1bC7NXzL2GPjLkPzTnTb1EvddSIA2czSUMAJ=ADn9wnSJigXT3G9CpsNCYo=svatmfw4uXlvVznbUvaiPy17wYkAcKcGWoCpesoonTnZzqpI7iu4yXXKDQEbu8YwwMeHVhaMhMM5N6q2zKhGm-H0jJaV2807zgSFlb8f_ejQEcQLizGkMPZnsVD3HBz9gdroiwnAPBITo-9kETWG63JDYAIP4=jJBUNopHjY24WdXPNv9kOvb8q-z6lK16BhkrlsfA40cdsmEz2mqcJgnYUR9qYkeMIrY4GE_G_1JmAWLnBO2WjM7yMCUHANJ446Tdj--79Mmef1WkqWZD1mLts3vNNu4=4jXXG_LvWmdGMAZhjFv-E8lVnCCc2kbciAOqAJzEmBqpOp_JFMILeeu=uaPwpMMVLfhi0qR7i8oYUq_BcuGZLnuQEpJ9f=C0da6bfk_h0-Ke5d-S_NPEJemsQp2rTBu3QrdTvru6Aj2iBdSioia889isukJeLb0SXDmFJKkRiCTbqWAqhjTMTeNdCVXZV8uCiQau-QF0H-aa7Xkc4R=CRealdXLgRQPbr6MgkL99SEgtaaj9NGA4=TYT-gK-WCJwG5QrH8fi2hI5Tj6npnXcL0DJiaKsOLNOoEu6lCGK-VF7fZZNsgzU-bOKga-0d6XAiTdDEZHIvCFBGVJu29C85cmMyjy=lCDTbhimLKOVn-3K38bVbft6ZquINtQZG6Jja0rEpK3eR12RoSTm0ZTOXX=HNPOD=oeQp11YtgYfOoOG6neu6Hfp87B0DmM3QDw6r4zg_081uy6KZo4Vpy89lU9Rj49PFGC=KwEX45m4ZaN_Ysjf5K2BAeGtCsUpLfWE2jwhVR8H4p9dvDtK5L5q8RNDhRyVYyt-Cih64Ui6es6uTcA0e5UsN3GBd3UiZiIkyLQcq=VlJp5oILJWTTU_bWzz729E22Lz81YdjR=95mgsVepsFmKV2Br9qVrp6OvnNEqV8tFN1FwpAhspgZVqsvUWvZsbzA-EhDcJBmZcaTrHyP3tnCRtPDPPWQ41nROcYHo1D-phV58Xj1_KngprqqqEljc4RyfXHKX3X93WLeD2kP2H=63oQ_ywc_yqH=IAFIvPCQil_RPpCXzPSWBq2F6oyAE3ljRXqWC5a-GO3sROLK3qLCIOdtrIrVFh6skOFiXyY9rQA9NeZShOrpIEV7A3SWpSZQqUDADgFmBVujFcR_wDgQyJeu32wDmtO1p7jZiEIOWkitq5Xt9WLqlyzFR2W3m9Sq5eHNRbWNd9n24b-eZrtT7rXTA_CB-_tKy7sNnpzSjguJTJ3aFY52gy6ozwIa62mLsuIFDBrCh9aXvmfWEmc6B_Luz54Dw=sQOUzQyjQKBthMDBQftywYTSdqfGOplOAtXWCSnNJFzwLs3YRPDmCCJb7fs1DP2tyVlVPDq88VLcM4JoqdsXwkK0BTaNA275AJ_cPE0=njHEI43lCz-OV=_g3TP2pDNbS_GgyJp0UkJJR57iqfbTIoGitlgTEPyNTkWTrWHK-YP4c-Rgi9=FZaVvUEEav06cTd0IXdANGK59W7zMOHeWiY3vMzDwvKSSaUkdVf3yzJ5HW3C8e1VShZGnK3Q0MHmf5_IXqcoUWC0=-0Vge_sHXsFHmkEIINZ_Zj39i5-VoPmRc6DeZ1L-1z2YcrZ3hu2PEhpnOtNt8qkIuYRHz=9YjtXbHob6Zbz39ztJF2Wp0I0-n7pmqGLUo7IONKyKOf5DLpAnw9s7_dFz6zrC_cGO3Ktb2FFumsHwIBkNcMgPjhE2TN5rjX3ZpKHdE-g6rM6nkcYM7rpAh6SqIwezGilD4fDVVJ2D8BnO5BErMdgJ1Nrl0Wm20X587X455a1l-hPKBfVsso6bzU8D77jAy4k-iK-N9KINv9JplHvTc2jAYwKeOiGzKe43gOJ4bFVYS2a2WrSesAnYn_Xqu7b1Yo9NFDwWdhoHWi7_C0fvwOcdoQRzEp8ZIkyPq=CT0rlvKDNBfEqh3WnNwzZtDuRiBDJbB7l-oOvWzSmr6Ps5mgpcVKcLiggfqKF=BslKbY8PBgRALgv39Fl7MNGSqzItoG4rz29NSFM5E4LJT9frn7IQ=QjyZ1A1qK_lc6_3TsJKpL-6gLQNzeXbCvnVvoJ-VmFIZpse4NIZKciFCtuwzU1s_NQVqL-r5T3E_TzBscEOVdEsXpZL2I2YvJI6tt7Z-BaYzo2X9imWeicBNbgXVQ3h-Eco8thKM44NrGXE8Jep04=jSPXTvkgI8FNvjBG4jmrc4b64agjl8yP4rDACKcOk3v4XYCFgoJCuI=HyaH-c5wYgnkwW01tYwCVwQs2TN0ITW2AFEltgdteuBMIKuplr7j4S5BuBoJZR9LBPdwwEMOTpmFW32-EtKGYO8YL_vAwywi25cOlrnyoAyy4J2_oUs1qpOGXXPLBQIipmNO_LzSr_Q8vH7dGHs6ZaTYr9EKiS_koazkkgrn57-fV=WqdBycu9TIF=kr=2hlT7G24uHYulfdv5bmBuq2hLUSK_03wAo8TFOQDg-Pz=z_JUG8U0qSBBZ=tUEiIigSLc831FGPgXhCob_nuqJ-35WAAtc-zcAEiz1ZbvDSHSCABgaCkg6O4Fgvqjf8lKL4v06M9-remrwwnERADrO=aunQcvVnTbSMjfp0_Hr-ceAOqjRFQjoOsQgRJhMCirim_JbKOOcQoBwcyPhCqkd5sjWWqmBryEFnNobpu4SqUc=HHUkX1OCXczTobz6P_TYkcUcBnrkcPaJGsSzpsrZUEzaVg7cNbiLZjpkPMfiwGez=7YAKEhR8ybHCf5IVRRS75psqzqGNZZnKF8opJEJIoCwOciFIulOGj_=OzaWa5ddLC8KjfK-u1Yygnm3QM47cmW=pHky5tzsfMuLVskZoOc4MjdRyoOeCH9MUj-Wb4rJzJsgOa9kW_EAWWl2_U==aOQ_jQVWVdYvB4S7J1lPjhMOBNTtt-l6DEKLT_UpVwlATdYjckRD5IuI4wMYXftHYS_o2I2OEEZeLyr_gOgTJGfAPSXSKRWrYeRBE7Rsyk5Ra--AMfSOsAEMdUYpzC9mh4rMibMllZiZTGlE2W6bf8wOEkGMeqAEVU75nc=NTYq4XijLPwIN4JIPF_omDXmBmg5C8OTk30GTBfIj5T4Z64_P0e2DVznWVG=VlS=NLNMdLV4GJ1gJJpCQb1cBI6KkGZWVL7CJQRBw5NFzT_YX0_8Q3ROjdZ_W7QXUonAFWwQMRwvZkMbNHiiL4cQUG_1UfpSnMK6=4VguZFZwwgFlplIoNEnQbgPGtLkGdPkWASK4Cj-y1NUUgS5d7zdf2-zRYvrKzsoqz7sqAZWcbR1ZIiAmA-yLjkKZbb2fCb2_Ld-1prK3M_JKqd47bHegcnwD4kAF5NuYC6vsc7hKNL0WW3_=KgdNoJRJPF7cWawwAb-sp3lpa6ts5jn4CU1EeEX5rkD5twadTYT8CyI8e5jCP0O5B2dEAdkOn=FfPkDIKewYq44XRd36pGbK_a2lNy4GKAM9jyt8vMj-=HCJyPdR1QiV_rd=z3DpfuyLI6bhp7WXB7lZLZIy8tHtUF1i-tSFORHfnRwkZ6u=4QZoKCEkQ-wGuUtUJIrkFeozN4k2En=JBCULCUgF9CuoOch=pZRJuy0Ga5dA8SinDSZeZ7r5SybeaDiUlEfqGuja1Zn8veSXMIjDI2J2O9njH_Id3n_6ZvDDWYCagt01DOKL0KttzY3LOHO2VCDcj1ULdlefV5A9hJUT1DfDZd-AYCL4s14DUC2XRllTHKtWJjSKWbS__jbR3cY5r-C-s=qCky93U6iv7dzGDekt-UH2vBvnR_CRh1RUjSM7J=OpRdkFXJF25MNudWlbL_pvjiy3QSKsHgKDorgaBFn6-2iUNHVc7MR8q6t2_HwVcTVkqA7pVSdZOkbUJX3TVOuQ-LtvJOKC-_uwgHb1vm8sWCkX=F3Q-gR67fGrUGsIO6HVpweuhbz9IG1-QotcpJdOFJslIAKD2TE2jOdL62L4OGsKe9Hn94kcK0GSJ37jZtCBS79hHboS3-13nYO6a4Fvf8Ut3lR-ScPt61i=cDDUPoht0TKzmn2BYU--XB9-dbWY3rjlu8jgSwLdhTseN3455ne-L4R3tGKu9KZBG59S5df0lEHsj=bPiE3qIPA2W7GNor1n5eG0KkZctVEnF_6sOICX8=b3pt4iOhaG8C18dICtKVMJKCLFteTfk0AMBeT83O=wpuAVRcskOg6o=lrZO_epk74u_sBZ6h5Qyz59MH5nJUQJd0fg-csW9YQNON9gHmNApDmVlTE6ZTJZzR5E2ilt8YLLWKs=fzjE_UYuO2AXGsypu04veNYOoKJWIYsJu-RdARwNc=_iZmWt9mmL7gMkXrW-C7TzPUAdFU6doLfh-vDLGe0ZKBO2j8BQV_j0BZXD0CoJpmLm9z=U2=b24ynfeMcyjp5zl6csdueQBQVdY37VbOXrMk2ZmLK0AK77JYI=J0_DT1VrITWWAsjAsWpGGhZ5yUneosnGKckgsuZ6WMOU_vv_Xdyd2XOKwEKgco7hZkBRie4sw16MgysYANE',
#     'Connection': 'keep-alive',
#     'Cookie': 'Ad34bsY56=A4PCmpabAQAAWdzXzAvzeAYst6AyVgi_BrCNhKWH6T6M534GMGsJSdz37oGQAbYDBUScuJhhwH8AAEB3AAAAAA|1|1|05a02ab0283ab1c179fa251a8d3344c64bedf849; audience=audiences=; internationalshippref=preferredcountry=ID&preferredcurrency=IDR&preferredcountryname=Indonesia; no-track=ccpa=false; nordstrom=bagcount=0&firstname=&ispinned=False&isSocial=False&shopperattr=||0|False|-1&shopperid=529d1d36a0f445c1a409b18c71ddf5f3&USERNAME=; nui=firstVisit=2026-01-07T03%3A58%3A06.826Z&geoLocation=&isModified=false&lme=false; session=FILTERSTATE=&RESULTBACK=&RETURNURL=http%3A%2F%2Fshop.nordstrom.com&SEARCHRETURNURL=http%3A%2F%2Fshop.nordstrom.com&FLSEmployeeNumber=&FLSRegisterNumber=&FLSStoreNumber=&FLSPOSType=&gctoken=&CookieDomain=&IsStoreModeActive=0; shoppertoken=shopperToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MjlkMWQzNmEwZjQ0NWMxYTQwOWIxOGM3MWRkZjVmMyIsImF1ZCI6Imd1ZXN0IiwiaXNzIjoibm9yZHN0cm9tLWd1ZXN0LWF1dGgiLCJleHAiOjIwODMyOTEwODYsInJlZnJlc2giOjE3Njc3NzI2ODYsImp0aSI6IjVkZTM2YTQzLWJkNGUtNGJjZi05YzJmLTg4ZjRjOWE4NDBkYyIsImlhdCI6MTc2Nzc1ODI4Nn0.YC8iW-g-PN1L4E9IQQZYAqPBqwZ2CpF2T17L3Cw2cbAjcD1-U9Xvd6r74MYdS92HujzifyP5E8Bzswv6CTlBHbXfjLj9u83OL2Hu6VfepyAc42HpPoTqD6psLk34hjq0FWf5CvHFMM0LF-WTCvwGlYx_OqsDBRXRCC7w0Y9lz3XgTkLwGYvJ85Kz6hltdGf722bI80R59M7s6cEiBKSPHVeqTfLL3c5xCuR5Dso4vT75GD0q-4k08M1ode7GR7LorAooUyzzZCE7PuF3DRwoMaY-HMsat8mrY9WXNMVHnit8takdQobNdtdsUlpSYOYd_RnWjWmfnu2ZmTf1XE7fh7zlsNLszE4t1YhJ6Pq26LYwOAt34qN8k3ShYYuNbWgUX5S0Z-NIjxI701yKf1-cxfGn8pHDuknfnG2Ck7sOCXCT00Vj8CweJPQMe3vewGZ1ZmZMkubJdxLOeX6SJRngkeFoJwl2oFKI5j76Uub8oOU-gQtYej-B4uVYBq0pXIYzARFkLWkK7vXHuuGIgHCipFgbfd9420K3JYFodU-2v7ANSGn-Md5cPF2rU8PBM5bmZL7lMKRyJh8hr5uRi3hXmx1sKHSTY4D6l9xgQnMBPuaQmieYd7G-dOAqT1KLEUHf5pA_Hf9_qqyTg4yiPPyk9DE-Z-V5mqtFht-Dt7xENnI; usersession=CookieDomain=nordstrom.com&SessionId=7e80a110-7235-422a-8eac-d097b73b6bcc; experiments=ExperimentId=d0d37a21-4c45-41b2-bace-232fd6310382; Bd34bsY56=A4vPmpabAQAA-WDFnq1ecOZKSPERSFibHvCotAG1jUAPCLnjxXoLNpvJFNhEAbYDBUScuJhhwH8AAEB3AAAAAA==; forterToken=d7f2dba2e84b444cb1b1d402b57d587e_1767758279385__UDF43-m4_23ck_; client=viewport=5_XLARGE; _gcl_au=1.1.104551211.1767758295; n.com_shopperId=529d1d36a0f445c1a409b18c71ddf5f3; _ga_11111111=GS2.1.s1767768124^$o2^$g0^$t1767768126^$j58^$l0^$h1997335501; _ga=GA1.1.1983041117.1767758297; FPID=FPID2.2.DemThntQWPcJhoURaUu1UV4gXVeAHepKZOf0qf%2BjGOE%3D.1767758297; FPLC=raQljWEKR44g4Px2NbaIEK9x%2FLno%2FeOn8sk5AcnZYW0xMVDbV1lZBEXZRr04WuKecJhf4DCGygKg%2B7VpbcCU8B0y96uYQ38r7aDHg%2Fn1cfNFba5vXRSLJ4K7CWZg%2BA%3D%3D; FPAU=1.1.104551211.1767758295; __ps_r=_; __ps_lu=https://www.nordstrom.com/browse/beauty/makeup/face?preferredStore=600&preferredPostalCode=22153&offset=9&page=2&postalCodeAvailability=22153; __ps_did=pscrb_a1336b39-42cb-43ba-f51a-bb5e2a8de3f7; __ps_fva=1767758299386; mp_nordstrom_com_mixpanel=%7B%22distinct_id%22%3A%20%2219b969b012b89-08b8e3eff0e7fa8-8535026-1fa400-19b969b012c2f6%22%2C%22bc_persist_updated%22%3A%201767758299439%7D; _tt_enable_cookie=1; _ttp=01KEB9P30K87S3QWB4BWF66A7M_.tt.1; ttcsid_C4A46SJV29O9OKB2G7A0=1767768131343::nFY_lD3_7X0W7LpjPcip.2.1767768131343.0; ttcsid=1767768131343::coJNYv9ZAVo3YWenQiaR.2.1767768131343.0; _fbp=fb.1.1767758302270.64491921520591006; _pin_unauth=dWlkPVltRmxaRGRqTlRrdE9ESmpZaTAwTWpaakxXSTVaak10T0RnMVlXWXdOR1EzTjJNMw; kampyle_userid=6e5d-a691-8af3-81ca-0e0e-3e70-af00-cbf7; Tld-kampyleUserSession=1767758306334; Tld-kampyleSessionPageCounter=3; Tld-kampyleUserSessionsCount=1; Tld-kampyleUserPercentile=25.747821681156513; _ga_FFQMSLD0QC=GS2.1.s1767768122^$o2^$g0^$t1767768126^$j56^$l1^$h1096127818; IR_gbd=nordstrom.com; IR_23920=1767758395567%7C5261518%7C1767758395567%7C%7C; IR_PI=26fcdb3c-eb7d-11f0-8a7a-4babecec4880%7C1767844795567; bluecoreNV=true; _uetsid=22761df0eb7d11f085567169d3649c6e; _uetvid=22764db0eb7d11f09f202f450f2f8858; QuantumMetricUserID=7d04db0b3f6bd31f0dc670774492709d; QuantumMetricSessionID=1df9bac0f29424426f91b9a3cf2f7e45',
#     'Sec-Fetch-Dest': 'empty',
#     'Sec-Fetch-Mode': 'cors',
#     'Sec-Fetch-Site': 'same-origin',
#     'Priority': 'u=4',
#     'TE': 'trailers'
# }


# # tulis header hanya sekali
# if not os.path.exists(CSV_FILE):
#     with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["product_url"])

# for page in range(1, 17):
#     print(f"\n📄 Fetching page {page} ...")
#     time.sleep(3)

#     params = {
#         "top": 72,
#         "preferredStore": 600,
#         "preferredPostalCode": 22153,
#         "offset": 9,
#         "page": page,
#         "isDynamicFacetsEnabled": "true"
#     }

#     response = requests.get(BASE_API, headers=headers, params=params, timeout=30)
#     response.raise_for_status()

#     data = response.json()
#     products = data.get("productsById", {})

#     if not products:
#         print("⚠️ No products found, stopping loop")
#         break

#     with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)

#         for info in products.values():
#             path = info.get("productPageUrl")
#             if path:
#                 product_url = BASE_URL + path
#                 writer.writerow([product_url])
#                 print(product_url)

# print("\n✅ SEMUA PAGE SELESAI — CSV TIDAK TERHAPUS")


import csv
import requests
import time
import os

BASE_API = "https://www.nordstrom.com/api/browse/query/browse/beauty/makeup/face"
BASE_URL = "https://www.nordstrom.com"
CSV_FILE = "12-Face-Makeup-nordstrom_product_urls.csv"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://www.nordstrom.com/browse/beauty/makeup/face',
    'ads-nord-context-id': '0d89a417-9495-447b-a2ce-bc28a1f65235',
    'cardmember': 'Non-CardMember',
    'content-type': 'application/json',
    'country-code': 'ID',
    'currency-code': 'USD',
    'customerauthstate': 'anonymous',
    'eventcustomer': '{"idType":"SHOPPER_ID","id":"529d1d36a0f445c1a409b18c71ddf5f3"}',
    'eventsource': '{"channel":"FULL_LINE","channelCountry":"US","platform":"WEB"}',
    'experimentid': 'd0d37a21-4c45-41b2-bace-232fd6310382',
    'experiments': '{"experiments":[],"optimizely":{"experiments":[{"n":"pdp_leapfrog_notes_display","v":"notesDisplay","p":"FULL_LINE_DESKTOP"},{"n":"gwp_upsell_in_bag","v":"gwp_upsell","p":"FULL_LINE_DESKTOP"},{"n":"pdp_chx_paypal_bnpl_v2","v":"paypalSB2","p":"FULL_LINE_DESKTOP"},{"n":"phdr_item_exchange","v":"default","p":"FULL_LINE_DESKTOP"},{"n":"pdp_leapfrog_notes_in_bag_v2","v":"notes_display","p":"FULL_LINE_DESKTOP"},{"n":"checkout_shopping_bag_express_payments_apple_pay","v":"apple_pay","p":"FULL_LINE_DESKTOP"},{"n":"checkout_global_header__on_order_confirmation","v":"global_header_on_oc","p":"FULL_LINE_DESKTOP"},{"n":"desktop_leapfrog_holdout","v":"leapfrogEligible","p":"FULL_LINE_DESKTOP"},{"n":"hp_leapfrog_cj1_canvas_web_v2","v":"default","p":"FULL_LINE_DESKTOP"},{"n":"hp_leapfrog_outfit_of_the_day_v3","v":"hpOutfitOfTheDayV3","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"chx_qr_code_in_wallet_hp","v":"qrCodeEnabled","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"sbn_departmenttiles","v":"departmentTiles","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"rec_tray_ab_test_tracking_page","v":"new_position","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"cam_guest_auth_ext","v":"extended","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"aynid","v":"default","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"phdr_store_returns_widget_ab_test","v":"additionalInstructions","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"desktop_icon_addcard_primary_approval_backend","v":"yes_consent_required","p":"JWN"},{"n":"desk_nmn_homepageherocomponent","v":"test2","p":"JWN"},{"n":"mow_iframe_modal","v":"iframe","p":"JWN"},{"n":"desktop_web_eta_styling","v":"eta_styling","p":"JWN"},{"n":"firstshopper_exposed_search_desktop_v1","v":"searchbar","p":"JWN"},{"n":"cat_appointment_skip_staff_selection_step","v":"off","p":"JWN"},{"n":"desk_sbn_brand_disco_conversion","v":"sbnbrandconv","p":"JWN"},{"n":"desktop_f2dd_variable_promise","v":"expedited","p":"JWN"},{"n":"credit_td_easy_rack","v":"off","p":"JWN"},{"n":"desktop_sbn_assisted_plp_enticements_nord_v1","v":"enticements","p":"JWN"},{"n":"desktop_iframe_modal","v":"iframe","p":"JWN"},{"n":"sierra_chat_do_no_harm_experiment","v":"sierra_chat_on","p":"JWN"},{"n":"desktop_nordstrom_forgot_pw_wallet_dump","v":"forgot_pw_wallet_dump","p":"JWN"},{"n":"desk_nordstrom_experiment_id","v":"correct_experiment_id","p":"JWN"},{"n":"credit_td_easy_employee","v":"off","p":"JWN"},{"n":"desk_ncom_loyalty_updates","v":"loyaltyverify_shopnow","p":"JWN"},{"n":"phdr_order_pickup_cancel","v":"on","p":"JWN"},{"n":"reco-mow_assisted_plp_datasimplification_nord_v1","v":"moduleredesign","p":"JWN"},{"n":"desktop_sbn_assisted_plp_reviews_nord_v1","v":"simplifyreviews","p":"JWN"},{"n":"desktop_sbn_assisted_plp_hearts_nord_v2","v":"hearts","p":"JWN"},{"n":"se_nord_desktop_filters_ui_grs","v":"dynamic_filters","p":"JWN"},{"n":"desk_hp_xdiv_fall_fashion","v":"default","p":"JWN"},{"n":"desk_ncom_checkout_otp_v2","v":"otp_checkout","p":"JWN"},{"n":"desk_sbn_brand_disco_mlp","v":"dbrandmlp","p":"JWN"},{"n":"ios_icon_addcard_primary_approval_backend","v":"yes_consent_required","p":"JWN"},{"n":"desktop_leapfrog_holdout_v1","v":"leapfrogeligible","p":"JWN"},{"n":"reco_text_context_ncom_web_pdp2","v":"MULTIMODAL","p":"JWN"},{"n":"reco_text_context_ncom_web","v":"default","p":"JWN"},{"n":"reco-desktop_assisted_plp_datasimplification_nord_v1","v":"moduleredesign","p":"JWN"},{"n":"credit_td_easy_nordstrom","v":"on","p":"JWN"},{"n":"desk_sbn_leapfrog_brands","v":"brandboutiquepoc","p":"JWN"},{"n":"ncom_desk_aaaa_test","v":"off","p":"JWN"},{"n":"se_nord_convo_search_desktop_tabbed_v2_grs","v":"conversational_search_tabbed","p":"JWN"},{"n":"desktop_paypal_braintree","v":"braintree","p":"JWN"},{"n":"hp_leapfrog_loyalty_signin_discovery_desktop","v":"signindiscovery","p":"JWN"},{"n":"icon_addcard_primary_approval","v":"no_consent_required","p":"JWN"},{"n":"phdr_opensearch_v2","v":"on","p":"JWN"}],"id":"d0d37a21-4c45-41b2-bace-232fd6310382"},"user_id":"d0d37a21-4c45-41b2-bace-232fd6310382"}',
    'feature-flags': 'isbranddiscoveryenabled,iscanvas2enabledsbn,iseditorserviceenabledforsbn,isheartingenabled,isproductpinningenabled,issponsoredadsforbrowseactive,issponsoredadsforsearchactive',
    'is-security-scan': 'false',
    'isauxexperiment': 'true',
    'ismobile': 'false',
    'isproductdropexperiment': 'true',
    'issanityexperiment': 'true',
    'isusereventqualified': 'false',
    'loyaltylevel': 'non-member',
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIzMDUxMjEiLCJhcCI6IjMwMjQ2MTM4NiIsImlkIjoiODhlZTBmNzI3NmNiZGVjNyIsInRyIjoiOTU2NmVmZjI2NmY4ZDg3ZTFjMTczODc1NjMxZWYwOTgiLCJ0aSI6MTc2Nzc2ODEzMjA4MywidGsiOiIyMjkxMTU0In19',
    'nord-authentication-status': 'UNRECOGNIZED',
    'nord-channel-brand': 'NORDSTROM',
    'nord-client-id': 'APP01196',
    'nord-context-id': 'fa394f8d-1ce0-4b99-b736-b17e3bd2ac79',
    'nord-country-code': 'US',
    'nord-customer-experience': 'DESKTOP_WEB',
    'nord-postalcode': '22153',
    'nord-request-id': 'ePmcpzCdTT2qrn-UaY3MZg',
    'nord-shopper-bearer-token': '',
    'nordapiversion': '1.0',
    'tracecontext': '0a3447b6-127e-4632-a3b8-77c5057dd89e',
    'traceparent': '00-9566eff266f8d87e1c173875631ef098-88ee0f7276cbdec7-01',
    'tracestate': '2291154^@nr=0-1-2305121-302461386-88ee0f7276cbdec7----1767768132083',
    'true-client-ip': '182.3.5.68',
    'true-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'userauthentication': 'UNRECOGNIZED',
    'userid': '529d1d36a0f445c1a409b18c71ddf5f3',
    'userid-hashed': '',
    'userqualificationtype': '-1',
    'visitorstatus': 'New Customer',
    'x-shopper-token': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MjlkMWQzNmEwZjQ0NWMxYTQwOWIxOGM3MWRkZjVmMyIsImF1ZCI6Imd1ZXN0IiwiaXNzIjoibm9yZHN0cm9tLWd1ZXN0LWF1dGgiLCJleHAiOjIwODMyOTEwODYsInJlZnJlc2giOjE3Njc3NzI2ODYsImp0aSI6IjVkZTM2YTQzLWJkNGUtNGJjZi05YzJmLTg4ZjRjOWE4NDBkYyIsImlhdCI6MTc2Nzc1ODI4Nn0.YC8iW-g-PN1L4E9IQQZYAqPBqwZ2CpF2T17L3Cw2cbAjcD1-U9Xvd6r74MYdS92HujzifyP5E8Bzswv6CTlBHbXfjLj9u83OL2Hu6VfepyAc42HpPoTqD6psLk34hjq0FWf5CvHFMM0LF-WTCvwGlYx_OqsDBRXRCC7w0Y9lz3XgTkLwGYvJ85Kz6hltdGf722bI80R59M7s6cEiBKSPHVeqTfLL3c5xCuR5Dso4vT75GD0q-4k08M1ode7GR7LorAooUyzzZCE7PuF3DRwoMaY-HMsat8mrY9WXNMVHnit8takdQobNdtdsUlpSYOYd_RnWjWmfnu2ZmTf1XE7fh7zlsNLszE4t1YhJ6Pq26LYwOAt34qN8k3ShYYuNbWgUX5S0Z-NIjxI701yKf1-cxfGn8pHDuknfnG2Ck7sOCXCT00Vj8CweJPQMe3vewGZ1ZmZMkubJdxLOeX6SJRngkeFoJwl2oFKI5j76Uub8oOU-gQtYej-B4uVYBq0pXIYzARFkLWkK7vXHuuGIgHCipFgbfd9420K3JYFodU-2v7ANSGn-Md5cPF2rU8PBM5bmZL7lMKRyJh8hr5uRi3hXmx1sKHSTY4D6l9xgQnMBPuaQmieYd7G-dOAqT1KLEUHf5pA_Hf9_qqyTg4yiPPyk9DE-Z-V5mqtFht-Dt7xENnI',
    'X-y8S6k3DB-f': 'A4jampabAQAAo5jeEw2UXMkV6ltuZ7kM11V_WUw5EBfyhYbju4CxTnk3mfxwAbYDBUScuJhhwH8AAEB3AAAAAA==',
    'X-y8S6k3DB-b': 'pd7ha9',
    'X-y8S6k3DB-c': 'AMASgZabAQAAiqHaS2qz01YxdUkv6g70_aGqBvPW-Du2pu62MYrZRZ571GHc',
    'X-y8S6k3DB-d': 'ABaAhIDBCKGFgQGAAYIQgISigaIAwBGAzv5Czi_33weK2UWee9Rh3AAAAAAvXY3EAJCNcSLI6afY7c867p1to90',
    'X-y8S6k3DB-z': 'q',
    'X-y8S6k3DB-a': 'hMPWcocUVVVGEB_a70YSZ051dy5B_kg6WQWWNXA2X47237yMw=10MTLXYcPU26QZwt-0S5zt5YTNHRbRLu=T2KrKPuvHhRJoRCUCNPuRnfei1rRXnygfJp1MztwO_7PJzHg8Y1yw3C2fF_2BFUCj8gG6SQWA7j7ByjIwYrS6yEM=Y7-JYq0=QTgClPy6rWkycbzUBfU6Ys2toU9r8tsD23Oc=YZmgfhflE651R3t8RZj5wsJ_v=HvskwMevmtBt8oyAMFHW3vngJADr0nWwwRd3t3Q68CqcILNkyBnyIb6Fr5bFIGH5hom6ImwVEsMAVCPcQzHobhlSL3UUUNHDSvB1OEo1TfAgS-9wSHTXgae1Lc99UyCWS_CSn3CEBfQm4q=n3rndcRJMZ-nTONeAM02aeFKHns2gNv5BzAnPVVl=fMcXOF_-_mWcs9Dfj1bC7NXzL2GPjLkPzTnTb1EvddSIA2czSUMAJ=ADn9wnSJigXT3G9CpsNCYo=svatmfw4uXlvVznbUvaiPy17wYkAcKcGWoCpesoonTnZzqpI7iu4yXXKDQEbu8YwwMeHVhaMhMM5N6q2zKhGm-H0jJaV2807zgSFlb8f_ejQEcQLizGkMPZnsVD3HBz9gdroiwnAPBITo-9kETWG63JDYAIP4=jJBUNopHjY24WdXPNv9kOvb8q-z6lK16BhkrlsfA40cdsmEz2mqcJgnYUR9qYkeMIrY4GE_G_1JmAWLnBO2WjM7yMCUHANJ446Tdj--79Mmef1WkqWZD1mLts3vNNu4=4jXXG_LvWmdGMAZhjFv-E8lVnCCc2kbciAOqAJzEmBqpOp_JFMILeeu=uaPwpMMVLfhi0qR7i8oYUq_BcuGZLnuQEpJ9f=C0da6bfk_h0-Ke5d-S_NPEJemsQp2rTBu3QrdTvru6Aj2iBdSioia889isukJeLb0SXDmFJKkRiCTbqWAqhjTMTeNdCVXZV8uCiQau-QF0H-aa7Xkc4R=CRealdXLgRQPbr6MgkL99SEgtaaj9NGA4=TYT-gK-WCJwG5QrH8fi2hI5Tj6npnXcL0DJiaKsOLNOoEu6lCGK-VF7fZZNsgzU-bOKga-0d6XAiTdDEZHIvCFBGVJu29C85cmMyjy=lCDTbhimLKOVn-3K38bVbft6ZquINtQZG6Jja0rEpK3eR12RoSTm0ZTOXX=HNPOD=oeQp11YtgYfOoOG6neu6Hfp87B0DmM3QDw6r4zg_081uy6KZo4Vpy89lU9Rj49PFGC=KwEX45m4ZaN_Ysjf5K2BAeGtCsUpLfWE2jwhVR8H4p9dvDtK5L5q8RNDhRyVYyt-Cih64Ui6es6uTcA0e5UsN3GBd3UiZiIkyLQcq=VlJp5oILJWTTU_bWzz729E22Lz81YdjR=95mgsVepsFmKV2Br9qVrp6OvnNEqV8tFN1FwpAhspgZVqsvUWvZsbzA-EhDcJBmZcaTrHyP3tnCRtPDPPWQ41nROcYHo1D-phV58Xj1_KngprqqqEljc4RyfXHKX3X93WLeD2kP2H=63oQ_ywc_yqH=IAFIvPCQil_RPpCXzPSWBq2F6oyAE3ljRXqWC5a-GO3sROLK3qLCIOdtrIrVFh6skOFiXyY9rQA9NeZShOrpIEV7A3SWpSZQqUDADgFmBVujFcR_wDgQyJeu32wDmtO1p7jZiEIOWkitq5Xt9WLqlyzFR2W3m9Sq5eHNRbWNd9n24b-eZrtT7rXTA_CB-_tKy7sNnpzSjguJTJ3aFY52gy6ozwIa62mLsuIFDBrCh9aXvmfWEmc6B_Luz54Dw=sQOUzQyjQKBthMDBQftywYTSdqfGOplOAtXWCSnNJFzwLs3YRPDmCCJb7fs1DP2tyVlVPDq88VLcM4JoqdsXwkK0BTaNA275AJ_cPE0=njHEI43lCz-OV=_g3TP2pDNbS_GgyJp0UkJJR57iqfbTIoGitlgTEPyNTkWTrWHK-YP4c-Rgi9=FZaVvUEEav06cTd0IXdANGK59W7zMOHeWiY3vMzDwvKSSaUkdVf3yzJ5HW3C8e1VShZGnK3Q0MHmf5_IXqcoUWC0=-0Vge_sHXsFHmkEIINZ_Zj39i5-VoPmRc6DeZ1L-1z2YcrZ3hu2PEhpnOtNt8qkIuYRHz=9YjtXbHob6Zbz39ztJF2Wp0I0-n7pmqGLUo7IONKyKOf5DLpAnw9s7_dFz6zrC_cGO3Ktb2FFumsHwIBkNcMgPjhE2TN5rjX3ZpKHdE-g6rM6nkcYM7rpAh6SqIwezGilD4fDVVJ2D8BnO5BErMdgJ1Nrl0Wm20X587X455a1l-hPKBfVsso6bzU8D77jAy4k-iK-N9KINv9JplHvTc2jAYwKeOiGzKe43gOJ4bFVYS2a2WrSesAnYn_Xqu7b1Yo9NFDwWdhoHWi7_C0fvwOcdoQRzEp8ZIkyPq=CT0rlvKDNBfEqh3WnNwzZtDuRiBDJbB7l-oOvWzSmr6Ps5mgpcVKcLiggfqKF=BslKbY8PBgRALgv39Fl7MNGSqzItoG4rz29NSFM5E4LJT9frn7IQ=QjyZ1A1qK_lc6_3TsJKpL-6gLQNzeXbCvnVvoJ-VmFIZpse4NIZKciFCtuwzU1s_NQVqL-r5T3E_TzBscEOVdEsXpZL2I2YvJI6tt7Z-BaYzo2X9imWeicBNbgXVQ3h-Eco8thKM44NrGXE8Jep04=jSPXTvkgI8FNvjBG4jmrc4b64agjl8yP4rDACKcOk3v4XYCFgoJCuI=HyaH-c5wYgnkwW01tYwCVwQs2TN0ITW2AFEltgdteuBMIKuplr7j4S5BuBoJZR9LBPdwwEMOTpmFW32-EtKGYO8YL_vAwywi25cOlrnyoAyy4J2_oUs1qpOGXXPLBQIipmNO_LzSr_Q8vH7dGHs6ZaTYr9EKiS_koazkkgrn57-fV=WqdBycu9TIF=kr=2hlT7G24uHYulfdv5bmBuq2hLUSK_03wAo8TFOQDg-Pz=z_JUG8U0qSBBZ=tUEiIigSLc831FGPgXhCob_nuqJ-35WAAtc-zcAEiz1ZbvDSHSCABgaCkg6O4Fgvqjf8lKL4v06M9-remrwwnERADrO=aunQcvVnTbSMjfp0_Hr-ceAOqjRFQjoOsQgRJhMCirim_JbKOOcQoBwcyPhCqkd5sjWWqmBryEFnNobpu4SqUc=HHUkX1OCXczTobz6P_TYkcUcBnrkcPaJGsSzpsrZUEzaVg7cNbiLZjpkPMfiwGez=7YAKEhR8ybHCf5IVRRS75psqzqGNZZnKF8opJEJIoCwOciFIulOGj_=OzaWa5ddLC8KjfK-u1Yygnm3QM47cmW=pHky5tzsfMuLVskZoOc4MjdRyoOeCH9MUj-Wb4rJzJsgOa9kW_EAWWl2_U==aOQ_jQVWVdYvB4S7J1lPjhMOBNTtt-l6DEKLT_UpVwlATdYjckRD5IuI4wMYXftHYS_o2I2OEEZeLyr_gOgTJGfAPSXSKRWrYeRBE7Rsyk5Ra--AMfSOsAEMdUYpzC9mh4rMibMllZiZTGlE2W6bf8wOEkGMeqAEVU75nc=NTYq4XijLPwIN4JIPF_omDXmBmg5C8OTk30GTBfIj5T4Z64_P0e2DVznWVG=VlS=NLNMdLV4GJ1gJJpCQb1cBI6KkGZWVL7CJQRBw5NFzT_YX0_8Q3ROjdZ_W7QXUonAFWwQMRwvZkMbNHiiL4cQUG_1UfpSnMK6=4VguZFZwwgFlplIoNEnQbgPGtLkGdPkWASK4Cj-y1NUUgS5d7zdf2-zRYvrKzsoqz7sqAZWcbR1ZIiAmA-yLjkKZbb2fCb2_Ld-1prK3M_JKqd47bHegcnwD4kAF5NuYC6vsc7hKNL0WW3_=KgdNoJRJPF7cWawwAb-sp3lpa6ts5jn4CU1EeEX5rkD5twadTYT8CyI8e5jCP0O5B2dEAdkOn=FfPkDIKewYq44XRd36pGbK_a2lNy4GKAM9jyt8vMj-=HCJyPdR1QiV_rd=z3DpfuyLI6bhp7WXB7lZLZIy8tHtUF1i-tSFORHfnRwkZ6u=4QZoKCEkQ-wGuUtUJIrkFeozN4k2En=JBCULCUgF9CuoOch=pZRJuy0Ga5dA8SinDSZeZ7r5SybeaDiUlEfqGuja1Zn8veSXMIjDI2J2O9njH_Id3n_6ZvDDWYCagt01DOKL0KttzY3LOHO2VCDcj1ULdlefV5A9hJUT1DfDZd-AYCL4s14DUC2XRllTHKtWJjSKWbS__jbR3cY5r-C-s=qCky93U6iv7dzGDekt-UH2vBvnR_CRh1RUjSM7J=OpRdkFXJF25MNudWlbL_pvjiy3QSKsHgKDorgaBFn6-2iUNHVc7MR8q6t2_HwVcTVkqA7pVSdZOkbUJX3TVOuQ-LtvJOKC-_uwgHb1vm8sWCkX=F3Q-gR67fGrUGsIO6HVpweuhbz9IG1-QotcpJdOFJslIAKD2TE2jOdL62L4OGsKe9Hn94kcK0GSJ37jZtCBS79hHboS3-13nYO6a4Fvf8Ut3lR-ScPt61i=cDDUPoht0TKzmn2BYU--XB9-dbWY3rjlu8jgSwLdhTseN3455ne-L4R3tGKu9KZBG59S5df0lEHsj=bPiE3qIPA2W7GNor1n5eG0KkZctVEnF_6sOICX8=b3pt4iOhaG8C18dICtKVMJKCLFteTfk0AMBeT83O=wpuAVRcskOg6o=lrZO_epk74u_sBZ6h5Qyz59MH5nJUQJd0fg-csW9YQNON9gHmNApDmVlTE6ZTJZzR5E2ilt8YLLWKs=fzjE_UYuO2AXGsypu04veNYOoKJWIYsJu-RdARwNc=_iZmWt9mmL7gMkXrW-C7TzPUAdFU6doLfh-vDLGe0ZKBO2j8BQV_j0BZXD0CoJpmLm9z=U2=b24ynfeMcyjp5zl6csdueQBQVdY37VbOXrMk2ZmLK0AK77JYI=J0_DT1VrITWWAsjAsWpGGhZ5yUneosnGKckgsuZ6WMOU_vv_Xdyd2XOKwEKgco7hZkBRie4sw16MgysYANE',
    'Connection': 'keep-alive',
    'Cookie': 'Ad34bsY56=A4PCmpabAQAAWdzXzAvzeAYst6AyVgi_BrCNhKWH6T6M534GMGsJSdz37oGQAbYDBUScuJhhwH8AAEB3AAAAAA|1|1|05a02ab0283ab1c179fa251a8d3344c64bedf849; audience=audiences=; internationalshippref=preferredcountry=ID&preferredcurrency=IDR&preferredcountryname=Indonesia; no-track=ccpa=false; nordstrom=bagcount=0&firstname=&ispinned=False&isSocial=False&shopperattr=||0|False|-1&shopperid=529d1d36a0f445c1a409b18c71ddf5f3&USERNAME=; nui=firstVisit=2026-01-07T03%3A58%3A06.826Z&geoLocation=&isModified=false&lme=false; session=FILTERSTATE=&RESULTBACK=&RETURNURL=http%3A%2F%2Fshop.nordstrom.com&SEARCHRETURNURL=http%3A%2F%2Fshop.nordstrom.com&FLSEmployeeNumber=&FLSRegisterNumber=&FLSStoreNumber=&FLSPOSType=&gctoken=&CookieDomain=&IsStoreModeActive=0; shoppertoken=shopperToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MjlkMWQzNmEwZjQ0NWMxYTQwOWIxOGM3MWRkZjVmMyIsImF1ZCI6Imd1ZXN0IiwiaXNzIjoibm9yZHN0cm9tLWd1ZXN0LWF1dGgiLCJleHAiOjIwODMyOTEwODYsInJlZnJlc2giOjE3Njc3NzI2ODYsImp0aSI6IjVkZTM2YTQzLWJkNGUtNGJjZi05YzJmLTg4ZjRjOWE4NDBkYyIsImlhdCI6MTc2Nzc1ODI4Nn0.YC8iW-g-PN1L4E9IQQZYAqPBqwZ2CpF2T17L3Cw2cbAjcD1-U9Xvd6r74MYdS92HujzifyP5E8Bzswv6CTlBHbXfjLj9u83OL2Hu6VfepyAc42HpPoTqD6psLk34hjq0FWf5CvHFMM0LF-WTCvwGlYx_OqsDBRXRCC7w0Y9lz3XgTkLwGYvJ85Kz6hltdGf722bI80R59M7s6cEiBKSPHVeqTfLL3c5xCuR5Dso4vT75GD0q-4k08M1ode7GR7LorAooUyzzZCE7PuF3DRwoMaY-HMsat8mrY9WXNMVHnit8takdQobNdtdsUlpSYOYd_RnWjWmfnu2ZmTf1XE7fh7zlsNLszE4t1YhJ6Pq26LYwOAt34qN8k3ShYYuNbWgUX5S0Z-NIjxI701yKf1-cxfGn8pHDuknfnG2Ck7sOCXCT00Vj8CweJPQMe3vewGZ1ZmZMkubJdxLOeX6SJRngkeFoJwl2oFKI5j76Uub8oOU-gQtYej-B4uVYBq0pXIYzARFkLWkK7vXHuuGIgHCipFgbfd9420K3JYFodU-2v7ANSGn-Md5cPF2rU8PBM5bmZL7lMKRyJh8hr5uRi3hXmx1sKHSTY4D6l9xgQnMBPuaQmieYd7G-dOAqT1KLEUHf5pA_Hf9_qqyTg4yiPPyk9DE-Z-V5mqtFht-Dt7xENnI; usersession=CookieDomain=nordstrom.com&SessionId=7e80a110-7235-422a-8eac-d097b73b6bcc; experiments=ExperimentId=d0d37a21-4c45-41b2-bace-232fd6310382; Bd34bsY56=A4vPmpabAQAA-WDFnq1ecOZKSPERSFibHvCotAG1jUAPCLnjxXoLNpvJFNhEAbYDBUScuJhhwH8AAEB3AAAAAA==; forterToken=d7f2dba2e84b444cb1b1d402b57d587e_1767758279385__UDF43-m4_23ck_; client=viewport=5_XLARGE; _gcl_au=1.1.104551211.1767758295; n.com_shopperId=529d1d36a0f445c1a409b18c71ddf5f3; _ga_11111111=GS2.1.s1767768124^$o2^$g0^$t1767768126^$j58^$l0^$h1997335501; _ga=GA1.1.1983041117.1767758297; FPID=FPID2.2.DemThntQWPcJhoURaUu1UV4gXVeAHepKZOf0qf%2BjGOE%3D.1767758297; FPLC=raQljWEKR44g4Px2NbaIEK9x%2FLno%2FeOn8sk5AcnZYW0xMVDbV1lZBEXZRr04WuKecJhf4DCGygKg%2B7VpbcCU8B0y96uYQ38r7aDHg%2Fn1cfNFba5vXRSLJ4K7CWZg%2BA%3D%3D; FPAU=1.1.104551211.1767758295; __ps_r=_; __ps_lu=https://www.nordstrom.com/browse/beauty/makeup/face; __ps_did=pscrb_a1336b39-42cb-43ba-f51a-bb5e2a8de3f7; __ps_fva=1767758299386; mp_nordstrom_com_mixpanel=%7B%22distinct_id%22%3A%20%2219b969b012b89-08b8e3eff0e7fa8-8535026-1fa400-19b969b012c2f6%22%2C%22bc_persist_updated%22%3A%201767758299439%7D; _tt_enable_cookie=1; _ttp=01KEB9P30K87S3QWB4BWF66A7M_.tt.1; ttcsid_C4A46SJV29O9OKB2G7A0=1767768131343::nFY_lD3_7X0W7LpjPcip.2.1767768131343.0; ttcsid=1767768131343::coJNYv9ZAVo3YWenQiaR.2.1767768131343.0; _fbp=fb.1.1767758302270.64491921520591006; _pin_unauth=dWlkPVltRmxaRGRqTlRrdE9ESmpZaTAwTWpaakxXSTVaak10T0RnMVlXWXdOR1EzTjJNMw; kampyle_userid=6e5d-a691-8af3-81ca-0e0e-3e70-af00-cbf7; Tld-kampyleUserSession=1767758306334; Tld-kampyleSessionPageCounter=3; Tld-kampyleUserSessionsCount=1; Tld-kampyleUserPercentile=25.747821681156513; _ga_FFQMSLD0QC=GS2.1.s1767768122^$o2^$g0^$t1767768126^$j56^$l1^$h1096127818; IR_gbd=nordstrom.com; IR_23920=1767758395567%7C5261518%7C1767758395567%7C%7C; IR_PI=26fcdb3c-eb7d-11f0-8a7a-4babecec4880%7C1767844795567; bluecoreNV=true; _uetsid=22761df0eb7d11f085567169d3649c6e; _uetvid=22764db0eb7d11f09f202f450f2f8858; QuantumMetricUserID=7d04db0b3f6bd31f0dc670774492709d; QuantumMetricSessionID=1df9bac0f29424426f91b9a3cf2f7e45',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=4',
    'TE': 'trailers'
}


# 👉 tulis header CSV sekali saja
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_url"])

for page in range(1, 17):
    offset = (page - 1) * 72

    params = {
        "top": 72,
        "offset": offset,
        "page": page,
        "preferredStore": 600,
        "preferredPostalCode": 22153,
        "isDynamicFacetsEnabled": "true"
    }

    print(f"\n📄 Fetching page {page} ...")

    response = requests.get(BASE_API, headers=headers, params=params)

    # if response.status_code != 200:
    #     print(f"❌ Page {page} blocked (status {response.status_code})")
    #     break

    if response.status_code != 200:
        print(f"⚠️ Page {page} blocked (status {response.status_code}), retry nanti")
        time.sleep(30)
        continue


    data = response.json()
    products = data.get("productsById", {})

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for info in products.values():
            path = info.get("productPageUrl")
            if path:
                url = BASE_URL + path
                writer.writerow([url])
                print(url)

    # time.sleep(10)  # ⏱️ WAJIB lambat

    if page % 5 == 0:
        print("😴 Cooling down...")
        time.sleep(60)

    time.sleep(12)


print("\n✅ Selesai — semua URL tersimpan tanpa overwrite")
