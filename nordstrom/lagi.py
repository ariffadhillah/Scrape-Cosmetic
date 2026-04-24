import time
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# =========================
# 1. API FETCHER (Hanya Loop Page)
# =========================
def get_all_product_urls(total_pages=2):
    all_urls = []
    base_url = "https://www.nordstrom.com"
    
    # Gunakan headers yang Anda miliki (terutama X-y8S6k3DB-a dan Cookie jika perlu)
    headers = {
    'X-y8S6k3DB-a': 'JyUMivEn8jBImRDy2FW-729qdThSDUJPw=j5pkC2v3g2uq8QnF92ouN=dwNdOWqF-1yYS7iXfJWQE44RNU=D8TvXTFkTEz4Ed6LoNSzHE3P9sOJeO_QKuU1q1ZCmyTNyZkr7L5pZ_R6FsaXhpJprym9C-o4tNT98YDFRSwymRuGy85qYwuz2JAbeo8YI4JXak-8lAeo7e=L4TlaJ1RaLSgl_CKNghbwTajOzeGGdL7JN0AAoiJbWmZ2IApK9B8RaLG0EmTk_dIUY34GBA5OmUFOxNwaCNE0X6jQWY5EnhJUaQSgeOq43NOsclL_L2HcChgh81vtRkod0B0FOv8xz8ye40I-1F6RB-UmvSgmgbIkBH_TKhwcfDq=RCs=gGWyPk27L7UiQQgM0cF82Pb7d6o2-FiLgMLJ5cA-7vb=WRhs389yv6__zjE_i9CIF0_edEpde78lrAyjXD0e1saaAnRsrCekFzBRmkHmcqJ2t6ygahvj-ChQPx0JHcHP6UF72-CZIxQGaWJxd-fFQmpktIhzAAIs=K_RYg1EffQejBU0m6u9WTHsR=OCHBvSTgYRTYs57ERGn1qaIl_fqIN=OCrsFKWubfOimpNdb2HNkpl1N8Hwb4bLwWbxFee37ttfxYnNDAj1uslgbpof4LUd13Gs9DBOu5qBJpd=o3eI2UoNyES8GPnD6g9hcapGIYNwezUiolTQOC4dNGOC49Cd=ey0cfMdxPibK22ZR541m3zXOgW6SUT6C6DfZIfkDKwW6AFfeUXScHmnaLfKJk0dt9PSBDCW-OZa7tJ_1YL4WTEs0KPjrRTS=I5nIYU-gSwxpmP-PbFIQ5P5Q_24=koy2UQiyxYsZoBEDosZTPfjrmaDHRblUyN4qoe3zuEHfS3MEd=JkDRSlBqq-iI5MzvRI_oMrz9t4X1iWLWfDyld4sR7tpwwTx7t5xcjROoqy5SCu5xJNdlnFtafmqFPS03kv-JETvvtEBCzenjGI6vNjEwthmW3ZtzUCMrOwjO=5Wu7Ulo-sL7r=E=ch5U3uryrlzP2DDpWIbQ_OFQvLI-rHFR4ZOaKE-eEqlS-K3lgc=WgU6r2CXXpdaYf2oBGsJaqrFJOQ4o96E16NBLzLAjs0sNWJwGp=98TGDA90Y91116d8totvP8jAO4nHAKnKQfFuFa0KQ7Wm36MDFZ5HHNGNu6i=NirsbrfBTO1SoJrWkk2Gb81ZkTz-EYO1GWUnFNiaRLLGcmCvwcp76vzk2Fy2fgeyyzzcDEq_4zHyTA5wMRgPNNbeF8L2mbZaDjp6XvzyJGCdfIKWYwPIBjp2N9_H9dg=8forIKqzTy7fWm7cok8zuC0ukPLKMphzPKE373WCk44-dTeNBYCZwFiolBwY6iF6johqsBYxUNCyEsTP=UrNdDR6==dKyr9cvgtN-QpWBgZk-pv_gED_d5F_208AigQdUzw4vKDWJBPBj-Iuge8eZ87jGt0s0Nnizou2m8cCMnfNhIfzwEpEG4seh1ovonkbOSnfExUSNlynSaqLcoZJWXX5gm6Hg9s678KhG1RhGypeoMvJPrb138uNm3UjWW1OK0x8Q-57E2i-e2dBWzNbfh02NHheqDtfdIBfFoSS5gcfy4kRylNJTbE=JH3k0K5zrQ0SLlm424oxJcPKlxBKQeZ2g0WG=y6h4L84bPBmcr6Hi572a91zGJGAUivdMahbCE0A9=ju8iePaTm0H1ygO96GJl012Mm4ATh9SaSyiFFSI-ZHBakytyEHubpsiHoI_raZo9pHcKqt_t4L8M3gxBa0Jps1vZYfBbZtPt1=w_UIUgPja1qbKea-9NG3TwHNznpPABg7sEbjrBrJSfUn1_jYsyCQUPrjzEhvi7R8=urb47AaEeoQhrzHoakJkn757us4rWPWc--qYZ0XXtZLyrEj-MS-oECrSDZf8SAWoT4l2PSLAcGs7GRHEuc2E2RTg52ch9h-7jXnKoJjTDmrbXui2EMS-Kb89ofhw7tqWhdifc6p8-cTh5UM3lQeqsCkmG1RKfmHF7q9nDmQAZ32Tl5ozznez6DRcmyJN09LI9WYNZrd_OAXxsQGkmWEc4pPv6fM_FlDfDFSCEBfdPXFrKOL7zft1hTISw5TQGluwBBD-wYnqgp5pSQdIEh0NRqqlK=3JOlBqd1t3U=3_qOgOeyoxpgHMItqfkMEkFCoBMSETqC7ZzLKCtpUuvw9wg9dnealfABOjE=M_Km4xJxdAWZqIjw8i=wLMu4lrzcRjp419kIDe4ylpdRJM95eZuvv=xvzN019H01jHB2OLt7ghovdTURkIfng-Zbgy90SRofN76kn4ShkEIaomrRuys5r=4mK1TDuLF=pCTiHvJUsxHnr-aANytqlNYmwL0AoaGTzd-NnAKx-1GApcWsAOj2rrfGQ65S5aWyUiziNgdSjwGWA0SBCWGDuaSekhTfOBtI9p32YQQFgLgkaUe3fn_56Cq4b7QQk=Cka99kXh8rRXO-FQiL32h89sr6PaCakbcIqva8OGOa7nSItwttf7QIXGN72sAMxvQWQPhL674OOf9Ft23RhJXw9uK=UoWv6DlTUofRcD8wFbhjxeOKwEi2nYe1sR4Oba_IbOnpxN1o_6LBs7al62UMgHrfWy84vka_OsTNSAB5sKlDgPGNnJnuWLApvAgBL=vcroui=phM9JwZmyvIzelOdj7iRAA4pmMgGOuOvBfQLxFcbObfapNuAjfIsLTLXleJqT7lk1uHMlOzwhHpiGsjroHjQCEyiwJcXuTHvv1NIbLy7t9BL474r9jsfikT7TAsPSXcQpuBQc0gBt7Ihf8R2moOwiTJS-Sa-LNt0SqXin9sha2HZ=c7v1oDQLXv=dOXWFDPzXm87mdcjp63jau61FqkfH4o9MFkdEguscWaLPerj4H8mKGR-Y9QsE3nmu4HW6cIqg76x7RiZ0_w2ce0d_vKLg3Y7_hBj2C=k2v=1A57sq-X89JTLWWb9CNFqsTmZk6pQP9lQhm=Z_zmig3iBHSwPxZmKWFpbNmKDyy-4uu_WdfsWgUah9L2me6vE5gUT30hSAC6IwZrPZ=FNnEqOaskfKqjdnTMv55SuibzniJxTnRLE7B3SFzPO6wQc4FbvhcrXsG3e-kGxihPc=FHh0tZdUkQ5pZMKgX5BbRMFOnX5Zbr2aKyPD0DlQ3Y2nv6p0Pd0-DMYzvFkb8t-BFuPmSCJu7-v=kvCnEX1bfpKhd2B-_fYEl8YHmHsEHxFWzr858QEIT5IN7sewk10_sdzboOcJ4Dd8TsG8Az8Hc5DPP7B-Bt4jMoW0gppyz6RTgiZbRKi6aOftEFt9tqLyeaxQGtQZCPv=eq6Ei=sqHBHzMQZF_MhTZlNq_0Pyavn-=1icvvEy0aIFSr_suD=-TWcaQRllhogFMduf2oA12hPRf_cratCd1jogT99aTqd_5OqRhni7mfQk5EOxemn-E3A8Pq=_nrbXxr0ncvwYiwy4Eovu-uXcPtxMAU2p9b=kL5Od_TSqFY5JI_KJxrjnP822Hra16BH4C8CBnR0DuRQiEsBycR0Zj_03MWquSCSyelx=MM6lRUOsf8NQKjMbO6QAYEOkXzbSLJPlMTpR4a_4Mof5ufL5Tol3n_wyhCEFX7pKoaifPqZT1gQMmsweFZm5c9eBj3lOfomojtup8anHgzoUin7anffW-eYoBL6mtw9zbl_=M=h1GFI6tN5C1q6vaIgHAfSxLauym=qCNgTb7HQKqel=CKvmNjlwu8Ry5lp7MUO_liGoUx3eUQgSZ1MtGoBzss0AffgShOa9NbsM3fk4T_so0pmFYhM7E=56=nbr5svezaxvq5Zo3aGvOPOP3i3r4Zym8Y-Nlgyj5aOoQ1nLKUKEabQ0Z0_9dZIax4Q2fa9afBIUJZIOmvpG3hf00=63wo-myZ0_dX6e_s3JeRkqQ_09WxgorEqh_H7lRGGx40xlJCMQYSU9AEZ7YfbwqrIzOZvasqXuaIhMzrjTu91_ReUK1glIvcyMUp__dBIuEP6m4nSJt=N65uad0ZHRGasruAFP4pjf2DymDzmW_3AnPN_Lpn-OyeTCl1-RRHgNg8wkkQ_8wdWq4mkQIuU6mt9zoZLrq4xhvh82Lo4P_Dh_Gqq50bzbxORdl52uytqyMwr5jhItnqa=ER5Wppmqz6jDlItlQ=03qlvbMvfIod73MNkT7wI0EOfi9m5JiNtzEerX3gdPrciEvKKR19NX8weBpOdCci7f0zPg6KDyBLKdpOC1BwQP65QowkUUsYEAJN4=9jFh9SGCRRULr4rUrPZGB=KS-BXqN9m7ZuzbHxxgoU54xJvn2OvMf9ccH1-nQIhq1TIwYT2-QPCowfu6AmqiiI6=Q=D0EMQCbnUx-KzTeqan7rKjpQkFvGW-p6hPj6DYyGrx_wInEkTnmp0kSevcw7YEDer0YW=jkkRRTWfdLJ2ooaBa9jWo9BSSJa4_IUzfn6--aOJTX4L7dY0opv1raGF1XMzcdlZB-ocrTNeXWc5sS3WDked1fzZScG=wjJfQqtE7H18ZH6laUiC2oJIawngfiQ1OpAw2SieqKSbYzD355qZRMY4IWF47CGPfy=GzYYZwQLDCgPFL26rAABYXQ0_r6QEsXuJ1Q5yfEna89wJjZnsJodwT2zN6zSFbl8-YdQRwq9QP861677HQBbkrxhCM1SrhvNb18bKZff7cu7Fch0Np-xQgEtI1oaI_2iOiRTEjL7Pz54Io3kQHB2wYRcNHA9DXlY-qBn=gbtCPgKp-4knohF5ixj2wbieiSmw3wk-90IiEpUDGNaazwHMuH-kY658N4m0X2qKdODDy5vPjbiLr-5qKHSiJQ_ikduLen8n58zxtcTmxpFd0CoC2atU3DwAatlQyltGu4M3YFDv=cgCiAhcjecwMogYcGFxk42EOa4sxB_Maejlz==KBdykuNqug6YMRfzSal4NNYD7aue3kov4FSIZbR7hkYfsn5uJsA65IzQhd67jiwfLuSN1fvfEue3ryW2qexZg2zRS9ydBlfLUPMYe2GNUoU11QQQQTGyIW1=DrqH7UwCHwRs6YRZSHnrclUAZsKDe6SxvEtUwEmf=a4TJSp295g5LkwCjFDBnNztYDKULmQcnTOBttnusokkXzey94wERLR6UwNpNzZNsFPOwIYbpy0asDSq0BDivPo_7wn97C9R65-WqY2IPv8hNbBCJgnZsX9uZPQrdRkah7=sQB_19CrtvJubmHORXXff0_MWk2p9PucuqWxJQBg=2ye-LDlSwW-49IvvgrchzWyCR_h58WQ8Y6XhP2PicpYLS-MTnh=GJXMBiW_5FI4RAEMEk80Hmjvr3azvsvFhw3Yu0=FC6N050fFZE2JByjAE0qPlFqhAa1zd-pIUatudCDzlmKbx19bdLlC-zcmix0eNPTWmxYxtcS0I0STZvTgMWGPUbv4zLJ=YwPZgi_qmC_ONe=8BrDEliwdmeuYjxDKyx1TLRC5ubDKIEtZXUr1HmlaSH7TBQjJ2ZdEW8jTui-KpTINLiI3jOIhJNiDM-Oo8By-=zCbWY1M8hbULiKLxBpQk0NhQOBuJU3gxeaTv5mC7QTcbtST5d82ubeb39H6L5jkMsZmtiGbtxfII_HqE_rsex0TEHwxlusvsJwLK1lAZ29e6RyLyGh1n8ptbxWU-PTUo1ZkEpvENI0mnPQJX5eAfyncsd1xAEvfcCSl75rTFIYb7AhQtbEza=m3JlClbibpQK_5aOIXFXl7UhfYX3Qg2Ldsc9ldfEm3yz7otndSBOm-uJnxPENa3oeT2bwp_G0FxSdTBAN5JiqEmKerPPXfPZK4hcc4v02YGPJ4JZMn5A2cjSKuS6Rv8tEufA5vdhKiNNHfnl9aYKbYgyjnvqhdpsxTMuN2SAJMQDflBcCf5kaM-0Rpqieyl1eBZa1TXF1s2FkAXpuIPhuJPnSYluRcwmlDo8H6Fpc1kWbJ6xuMz89QioaUr3SAqGLuPCcvaxrDSSwGFLdcs3h_4bNifAUKFCnNMjL=cHWIMRCWr6-La0dpcWvhSXlBM6ITrO-5gxiH5CwOxe1OnoduH2JocMunBFEM3yn2n_56p58-tam8A7eOcHkRL_AMf7=wUfBJXJPf99jsHAJ67rPE5648_lOJS95QMIh5gnDc1hDBFyy6jkOvfrzurEOwaqQgpNQU6PfrfngP_5sNwuHRLcJRpbdSFZFX15mk_9K2JMzLdy9IyNTkFU0PfQ8dQ-rTg81DZLXm-Bv4mJ2Pyw3rhAix_Bn2RtYjlJydkue4qyi6dLd8L-9cB2oU0A20pGa0rPSZRD1kxB2aqISZbuk2-CkYAOA-o1J2A-vJfchOoDXMTrhmLIOw=oPDBgsptE6zX6FN1dl9OmQqagOxNrvte4i2XlI0Nw77dg7yPkElQhPwKQ=nrp-v97tQAAZ1XQ_Y_zy6fYftc4KxckBjA4oipy=uMgPd8sNsudTDURlIHwizwtMQRYWXk-76NE2biLqoF1x9xR-FDUxdibNaRvpizglLkFgxynuOKRGxCRkxH2S2MFiZ-r8dnUkmkZF171OJjzPwHmTLtQOypJ7aG5O=zJTh00Bi9XB0nP5z=-MxdhxhJMjxFTmrRSpIffH5INx0_-ZGCi2CfKI37rZvQ8RnnJ5g=zxt-6jhX1oybv50uEHamYgnO5nOM=38i9G8y9jKHf8Bd0gg=H6S1dNXuK4pSxfLfzsLdk8Jyj1Fkmxx_hwJqu62z4oWGka7pCZwxA1its4oA395bYMfzGy=LBH6Dz3X5T1lGYmSioHZ-OrcShxYzUWrbvHctDv3OfGRnZcnW69xXqowCMPkjowBnWrvC9K0GF0pB7iiFFLOwCrWvBP=PGAFD1Lpfw1wcEGhTPtPL6N8KxeOH6qcFm1m8ZmkyUni3ma_A9=5QxyCCKSocOfLOWI1vF8Y5wm7Dj0JSljtevaQQYU7_wIam2N5537iGs-k7T0EHhOhzcuCk75=qXSyBiOygyk01OqgPUI=tl1t7uWY_unMJGd=A-gRPodT_LlQ0tdy=86A_zbWXlPEF9NJxlgfThmiz3yxrmqcCaUbHq6z4Sx-avIdnhshG0e2rQsFmHKT2og8mGibBWB0xq0MsyjN-6dGqacJ2WRcy606vcBImC5oAwWbrTSAu0MGSuYmrUuz27f1MoqHPpbSa_J4hGzxja2p-64FoNQo5SBc8a7ehMQWpZxnol3dbfYBj1',
    'userauthentication': 'UNRECOGNIZED',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'true-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'issanityexperiment': 'true',
    'is-security-scan': 'false',
    'sec-ch-ua-mobile': '?0',
    'cardmember': 'Non-CardMember',
    'traceparent': '00-88031183bb318ae0a18ea300f79fb46a-8c2efc930ad38d25-01',
    'X-y8S6k3DB-c': 'AAAL5JGbAQAAL6oUugq1tGkMZ_IZrPj6DP1_yxMgWVIoYrfYNPiC9JykF_LB',
    'loyaltylevel': 'non-member',
    'nordapiversion': '1.0',
    'content-type': 'application/json',
    'experiments': '{"experiments":[],"optimizely":{"experiments":[{"n":"pdp_leapfrog_notes_display","v":"notesDisplay","p":"FULL_LINE_DESKTOP"},{"n":"gwp_upsell_in_bag","v":"gwp_upsell","p":"FULL_LINE_DESKTOP"},{"n":"pdp_chx_paypal_bnpl_v2","v":"paypalSB2","p":"FULL_LINE_DESKTOP"},{"n":"phdr_item_exchange","v":"default","p":"FULL_LINE_DESKTOP"},{"n":"pdp_leapfrog_notes_in_bag_v2","v":"notes_display","p":"FULL_LINE_DESKTOP"},{"n":"checkout_shopping_bag_express_payments_apple_pay","v":"apple_pay","p":"FULL_LINE_DESKTOP"},{"n":"checkout_global_header__on_order_confirmation","v":"global_header_on_oc","p":"FULL_LINE_DESKTOP"},{"n":"desktop_leapfrog_holdout","v":"leapfrogEligible","p":"FULL_LINE_DESKTOP"},{"n":"hp_leapfrog_cj1_canvas_web_v2","v":"default","p":"FULL_LINE_DESKTOP"},{"n":"chx_qr_code_in_wallet_hp","v":"qrCodeEnabled","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"sbn_departmenttiles","v":"departmentTiles","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"rec_tray_ab_test_tracking_page","v":"new_position","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"cam_guest_auth_ext","v":"extended","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"aynid","v":"default","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"phdr_store_returns_widget_ab_test","v":"additionalInstructions","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"hp_leapfrog_outfit_of_the_day_v3","v":"hpOutfitOfTheDayV3","p":"FULL_LINE_BACKEND_SERVICE"},{"n":"desk_hp_xdiv_fall_fashion","v":"hpxdivfallfashion_on","p":"JWN"},{"n":"desk_nordstrom_experiment_id","v":"correct_experiment_id","p":"JWN"},{"n":"phdr_opensearch_v2","v":"on","p":"JWN"},{"n":"credit_td_easy_rack","v":"off","p":"JWN"},{"n":"desk_ncom_loyalty_updates","v":"loyaltyverify_shopnow","p":"JWN"},{"n":"firstshopper_exposed_search_desktop_v1","v":"searchbar","p":"JWN"},{"n":"desk_sbn_leapfrog_brands","v":"brandboutiquepoc","p":"JWN"},{"n":"desktop_web_eta_styling","v":"eta_styling","p":"JWN"},{"n":"ncom_desk_aaaa_test","v":"variation_2","p":"JWN"},{"n":"se_nord_convo_search_desktop_tabbed_v2_grs","v":"off","p":"JWN"},{"n":"hp_leapfrog_loyalty_signin_discovery_desktop","v":"signindiscovery","p":"JWN"},{"n":"desktop_sbn_assisted_plp_hearts_nord_v2","v":"hearts","p":"JWN"},{"n":"desk_sbn_brand_disco_mlp","v":"dbrandmlp","p":"JWN"},{"n":"desk_ncom_checkout_otp_v2","v":"otp_checkout","p":"JWN"},{"n":"desktop_paypal_braintree","v":"braintree","p":"JWN"},{"n":"ios_icon_addcard_primary_approval_backend","v":"yes_consent_required","p":"JWN"},{"n":"mow_iframe_modal","v":"iframe","p":"JWN"},{"n":"cat_appointment_skip_staff_selection_step","v":"on","p":"JWN"},{"n":"desk_nmn_homepageherocomponent","v":"test2","p":"JWN"},{"n":"desktop_nordstrom_forgot_pw_wallet_dump","v":"forgot_pw_wallet_dump","p":"JWN"},{"n":"desktop_iframe_modal","v":"iframe","p":"JWN"},{"n":"se_nord_desktop_filters_ui_grs","v":"dynamic_filters","p":"JWN"},{"n":"desktop_leapfrog_holdout_v1","v":"leapfrogeligible","p":"JWN"},{"n":"desktop_sbn_assisted_plp_enticements_nord_v1","v":"enticements","p":"JWN"},{"n":"reco-desktop_assisted_plp_datasimplification_nord_v1","v":"moduleredesign","p":"JWN"},{"n":"desk_sbn_brand_disco_conversion","v":"sbnbrandconv","p":"JWN"},{"n":"phdr_order_pickup_cancel","v":"on","p":"JWN"},{"n":"credit_td_easy_nordstrom","v":"off","p":"JWN"},{"n":"credit_td_easy_employee","v":"on","p":"JWN"},{"n":"desktop_f2dd_variable_promise","v":"expedited","p":"JWN"},{"n":"reco-mow_assisted_plp_datasimplification_nord_v1","v":"moduleredesign","p":"JWN"},{"n":"desktop_icon_addcard_primary_approval_backend","v":"yes_consent_required","p":"JWN"},{"n":"icon_addcard_primary_approval","v":"no_consent_required","p":"JWN"},{"n":"desktop_sbn_assisted_plp_reviews_nord_v1","v":"simplifyreviews","p":"JWN"}],"id":"1138cf13-ec2c-4668-89a6-ef93b47b001f"},"user_id":"1138cf13-ec2c-4668-89a6-ef93b47b001f"}',
    'isauxexperiment': 'true',
    'tracestate': '2291154@nr=0-1-2305121-302461386-8c2efc930ad38d25----1767690095402',
    'nord-authentication-status': 'UNRECOGNIZED',
    'customerauthstate': 'anonymous',
    'nord-request-id': '99G-UVvjQfKpDl65vQSD2g',
    'eventcustomer': '{"idType":"SHOPPER_ID","id":"98692b4f1ec4444092cb4fd78e74988d"}',
    'ads-nord-context-id': '2491ae68-266e-4a71-976c-213b8ba74397',
    'nord-customer-experience': 'DESKTOP_WEB',
    'Referer': 'https://www.nordstrom.com/',
    'X-y8S6k3DB-b': 'h4vfmj',
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIzMDUxMjEiLCJhcCI6IjMwMjQ2MTM4NiIsImlkIjoiOGMyZWZjOTMwYWQzOGQyNSIsInRyIjoiODgwMzExODNiYjMxOGFlMGExOGVhMzAwZjc5ZmI0NmEiLCJ0aSI6MTc2NzY5MDA5NTQwMiwidGsiOiIyMjkxMTU0In19',
    'country-code': 'US',
    'ismobile': 'false',
    'experimentid': '1138cf13-ec2c-4668-89a6-ef93b47b001f',
    'nord-client-id': 'APP01196',
    'visitorstatus': 'Repeat Customer',
    'eventsource': '{"channel":"FULL_LINE","channelCountry":"US","platform":"WEB"}',
    'sec-ch-ua-platform': '"Windows"',
    'nord-country-code': 'US',
    'nord-context-id': '6c8d3394-fbf2-4a59-84fb-19a09a0b7fbd',
    'nord-shopper-bearer-token': '',
    'feature-flags': 'isbranddiscoveryenabled,iscanvas2enabledsbn,iseditorserviceenabledforsbn,isheartingenabled,isproductpinningenabled,issponsoredadsforbrowseactive,issponsoredadsforsearchactive',
    'X-y8S6k3DB-d': 'ABaAhIDBCKGFgQGAAYIQgISigaIAwBGAzv5Czi_33wf4gvScpBfywQAAAAAvXY3EADMabsvPwY1PUIHPctqT_Ck',
    'X-y8S6k3DB-f': 'A85O5pGbAQAAYrt-N6exBZRmgZqzOiswbkX369wjPQonGA3PMM4soxRz0lTlAbYDBUSucmbRwH8AAEB3AAAAAA==',
    'userqualificationtype': '-1',
    'currency-code': 'USD',
    'nord-channel-brand': 'NORDSTROM',
    'tracecontext': '0d733a0d-1697-4d16-942e-7f5a935ea987',
    'x-shopper-token': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODY5MmI0ZjFlYzQ0NDQwOTJjYjRmZDc4ZTc0OTg4ZCIsImF1ZCI6Imd1ZXN0IiwiaXNzIjoibm9yZHN0cm9tLWd1ZXN0LWF1dGgiLCJleHAiOjIwODMyMTIxNDUsInJlZnJlc2giOjE3Njc2OTM3NDUsImp0aSI6IjA0OWZjYmFhLWM4YTEtNDIwMy1hODYzLTIyMWIyMDM0YzFlMCIsImlhdCI6MTc2NzY3OTM0NX0.J9iZhG0MfLen1KNtCxfsLs3dUW4LFqh3XsADjY2obXQejDfgOQyLe9Idplh91r7HIYZI0Va453KZInb4I1Igw8EqnpudkGCIB9921Ugwc5C97EkdPHlaKD2d3CPSpBspK1spGxLSRsu34G-RgJZjN_FhF1gD-QIBn4f3pTyHABaVg3MtJY6B-SN815GC14iV_poDfMhpAy3DTgmQ6rROezFh2JORe8TodvcBPV1HSF0zgfisrPi-nbsn_c1HtyF9h5a8rLxHb46hkP79pu6_IlTiT_4Jif7QHjUGlo3tTNi7pN4h4rDMy2ef30ztHLUulNUHOadcxBBhw-nwwTwdaJcLFH6GtVDFQXFkKmFS44KXsYiVQzXZWLMPlYdHcBygVwYrSDxGMMcO9Xei2Z0xOT_cPHqx4haWtShXoYe_r7Wd4cRg6mq0juTggrgqLMZLLNZiRVF2mqaeAiKe-bkFeq6Z1tW_AJCPqgjSUkD6uhPu3NPIvItHRe5YdcQ47piWChflyf8N9tV_T1BEtGlHmFnv4ZmGbkIOqc5PlR-ukJlEvA5ci_ziC_abqbKjukjuk0sbcQDJx1rpfhOvWTAmYTYhEr2v7WwsqJws_fT093vwGL6UD4UmvPcaSd_XZTCOs70b5J9qUpB7_C2Cpc4irXOhHjdvu9_sdSMlNrxvVfQ',
    'isusereventqualified': 'false',
    'isproductdropexperiment': 'true',
    'true-client-ip': '182.3.5.68',
    'X-y8S6k3DB-z': 'q',
    'nord-postalcode': '23126',
    'userid-hashed': '',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'DNT': '1',
    'userid': '98692b4f1ec4444092cb4fd78e74988d',
    'Cookie': 'Ad34bsY56=A0UYRWibAQAAr6YiwqsKVIT0U4MmeMs5zxR260f82bsYcivRr8XenZuPCG01ATZWMosAAAAAAAAAAAAAAAAAAA|1|1|db239549601fd1d7cc56891eac790b1b00b457bb'
    }

    for page in range(1, total_pages + 1):
        # URL disederhanakan hanya loop pada &page=
        api_url = f"https://www.nordstrom.com/api/browse/query/browse/beauty/makeup/face?top=72&postalCodeAvailability=23126&preferredStore=621&preferredPostalCode=23126&page={page}&isDynamicFacetsEnabled=true"
        
        try:
            print(f"🔍 Mengambil daftar produk Halaman {page}...")
            response = requests.get(api_url, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Error Hal {page}: {response.status_code}")
                continue
            
            data = response.json()
            products = data.get("productsById", {})
            
            for pid, info in products.items():
                path = info.get("productPageUrl")
                if path:
                    all_urls.append(base_url + path)
            
            time.sleep(1) # Jeda sopan agar tidak di-ban
        except Exception as e:
            print(f"❌ Gagal di halaman {page}: {e}")
            
    return all_urls

# =========================
# 2. PARSER DETAIL (Termasuk Harga per SKU)
# =========================


def extract_skus_with_images(data, product_url):
    results = []

    # 1. Ambil Ingredients dan Price data dari root
    view_data = data.get("viewData", {})
    ingredients_text = view_data.get("ingredients", "No ingredients found")
    
    # Ambil seluruh objek price
    price_data = data.get("price", {})
    prices_by_sku = price_data.get("bySkuId", {})

    # Ambil Data Style dari sellingEssentials
    selling = data.get("sellingEssentials", {})
    styles_by_id = selling.get("stylesById", {})

    for style_id, style in styles_by_id.items():
        brand_info = style.get("brand", {})
        brand_name = brand_info.get("brandName", "No Brand")

        review_data = style.get("reviews", {})
        avg_rating = review_data.get("averageRating", 0)
        num_reviews = review_data.get("numberOfReviews", 0)

        media = style.get("mediaExperiences", {}) 
        carousels = media.get("carouselsByColor", [])
        
        color_image_map = {}
        for entry in carousels:
            color_name = entry.get("colorName", "").strip().upper()
            shots = entry.get("orderedShots", [])
            if shots:
                color_image_map[color_name] = shots[0].get("url")

        product_name = style.get("productName") or style.get("productTitle")
        skus_by_id = style.get("skus", {}).get("byId", {})

        for sku_id, sku in skus_by_id.items():
            color_val = sku.get("colorDisplayValue", "").strip().upper()
            image_url = color_image_map.get(color_val, "No Image Found")

            # --- LOGIKA PENGAMBILAN HARGA ---
            # Cari harga berdasarkan sku_id di dalam prices_by_sku
            sku_price_info = prices_by_sku.get(str(sku_id), {})
            
            # Ambil harga dari kategori 'regular' jika ada
            price_value = "N/A"
            if sku_price_info:
                # Cek currentPriceType, biasanya 'REGULAR' atau 'SALE' (clearance)
                price_type = sku_price_info.get("currentPriceType", "regular").lower()
                price_obj = sku_price_info.get(price_type) or sku_price_info.get("regular")
                
                if price_obj and "price" in price_obj:
                    price_value = price_obj["price"].get("units")
            # -------------------------------

            results.append({
                "Product ID": style_id,
                "SKU ID": sku_id,
                "rmsSkuId": sku.get("rmsSkuId"),
                "Product Name": product_name,
                "Product Maker": brand_name,
                "Varian/color": sku.get("colorDisplayValue"),
                "size": sku.get("sizeDisplayValue"),
                "Product Url": product_url,  # <--- Menyimpan URL Produk
                "Major Category": "Makeup",
                "Category": "Face Makeup",
                "Ingredients": ingredients_text,
                "Product Image URL": image_url,
                "Price": price_value, # <--- Kolom Baru
                "Total Review Count": avg_rating,
                "Rating": f"'{num_reviews}",

            })

    return results


# =========================
# 3. MAIN RUNNER
# =========================
def run_scraper():
    all_urls = get_all_product_urls(total_pages=2)
    
    if not all_urls:
        return

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", fix_hairline=True)

    all_results = []
    try:
        for index, url in enumerate(all_urls):
            print(f"🚀 [{index+1}/{len(all_urls)}] Visiting: {url}")
            driver.get(url)
            time.sleep(7) 

            config = driver.execute_script("return window.__INITIAL_CONFIG__ || null;")
            if config:
                data = extract_skus_with_images(config, url)
                all_results.extend(data)
            
            # Simpan bertahap setiap 10 produk agar data tidak hilang jika crash
            if (index + 1) % 10 == 0:
                save_to_csv(all_results)

        save_to_csv(all_results) # Simpan terakhir
        print("✨ SELESAI!")

    finally:
        driver.quit()

def save_to_csv(data_list):
    if not data_list: return
    keys = data_list[0].keys()
    with open("Makeup-Face-Makeup.csv", "w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

if __name__ == "__main__":
    run_scraper()