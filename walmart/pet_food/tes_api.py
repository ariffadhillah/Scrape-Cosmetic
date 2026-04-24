
# # # import requests
# # # import json

# # # url = "https://www.walmart.com/orchestra/snb/graphql/Search/52742a6983b5a61016b8a92e92a035955b985edbf02486567619fd555e32e50d/search?variables=%7B%22id%22%3A%22%22%2C%22affinityOverride%22%3A%22store_led%22%2C%22pap%22%3A%22%7B%5C%22polaris%5C%22%3A%7B%5C%22ms_triggered%5C%22%3Atrue%7D%7D%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22pet%20food%22%2C%22nudgeContext%22%3A%22%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%22%22%2C%22facet%22%3A%22%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%2C%22isGenAiEnabled%22%3Atrue%2C%22rootDimension%22%3A%22%22%2C%22altQuery%22%3A%22%22%2C%22selectedFilter%22%3A%22%22%2C%22neuralSearchSeeAll%22%3Afalse%2C%22isModuleArrayReq%22%3Afalse%2C%22isLMPBrowsePage%22%3Afalse%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22pet%20food%22%2C%22cat_id%22%3A%22%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22%22%7D%2C%22ffAwareSearchOptOut%22%3Afalse%2C%22enableDesktopHighlights%22%3Afalse%2C%22enableVolumePricing%22%3Afalse%2C%22enableCopyBlock%22%3Atrue%2C%22enableVariantCount%22%3Afalse%2C%22enableSlaBadgeV2%22%3Afalse%2C%22fitmentFieldParams%22%3A%7B%22powerSportEnabled%22%3Atrue%2C%22dynamicFitmentEnabled%22%3Atrue%2C%22extendedAttributesEnabled%22%3Atrue%2C%22extendedAttributesV2Enabled%22%3Afalse%2C%22fuelTypeEnabled%22%3Atrue%7D%2C%22fitmentSearchParams%22%3A%7B%22id%22%3A%22%22%2C%22affinityOverride%22%3A%22store_led%22%2C%22pap%22%3A%22%7B%5C%22polaris%5C%22%3A%7B%5C%22ms_triggered%5C%22%3Atrue%7D%7D%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22pet%20food%22%2C%22nudgeContext%22%3A%22%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%22%22%2C%22facet%22%3A%22%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%2C%22isGenAiEnabled%22%3Atrue%2C%22rootDimension%22%3A%22%22%2C%22altQuery%22%3A%22%22%2C%22selectedFilter%22%3A%22%22%2C%22neuralSearchSeeAll%22%3Afalse%2C%22isModuleArrayReq%22%3Afalse%2C%22isLMPBrowsePage%22%3Afalse%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22pet%20food%22%2C%22cat_id%22%3A%22%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22%22%7D%2C%22ffAwareSearchOptOut%22%3Afalse%2C%22enableDesktopHighlights%22%3Afalse%2C%22enableVolumePricing%22%3Afalse%2C%22enableCopyBlock%22%3Atrue%2C%22enableVariantCount%22%3Afalse%2C%22enableSlaBadgeV2%22%3Afalse%2C%22cat_id%22%3A%22%22%2C%22_be_shelf_id%22%3A%22%22%7D%2C%22searchParams%22%3A%7B%22id%22%3A%22%22%2C%22affinityOverride%22%3A%22store_led%22%2C%22pap%22%3A%22%7B%5C%22polaris%5C%22%3A%7B%5C%22ms_triggered%5C%22%3Atrue%7D%7D%22%2C%22dealsId%22%3A%22%22%2C%22query%22%3A%22pet%20food%22%2C%22nudgeContext%22%3A%22%22%2C%22page%22%3A1%2C%22prg%22%3A%22desktop%22%2C%22catId%22%3A%22%22%2C%22facet%22%3A%22%22%2C%22sort%22%3A%22best_match%22%2C%22rawFacet%22%3A%22%22%2C%22seoPath%22%3A%22%22%2C%22ps%22%3A40%2C%22limit%22%3A40%2C%22ptss%22%3A%22%22%2C%22trsp%22%3A%22%22%2C%22beShelfId%22%3A%22%22%2C%22recall_set%22%3A%22%22%2C%22module_search%22%3A%22%22%2C%22min_price%22%3A%22%22%2C%22max_price%22%3A%22%22%2C%22storeSlotBooked%22%3A%22%22%2C%22additionalQueryParams%22%3A%7B%22hidden_facet%22%3Anull%2C%22translation%22%3Anull%2C%22isMoreOptionsTileEnabled%22%3Atrue%2C%22isGenAiEnabled%22%3Atrue%2C%22rootDimension%22%3A%22%22%2C%22altQuery%22%3A%22%22%2C%22selectedFilter%22%3A%22%22%2C%22neuralSearchSeeAll%22%3Afalse%2C%22isModuleArrayReq%22%3Afalse%2C%22isLMPBrowsePage%22%3Afalse%7D%2C%22searchArgs%22%3A%7B%22query%22%3A%22pet%20food%22%2C%22cat_id%22%3A%22%22%2C%22prg%22%3A%22desktop%22%2C%22facet%22%3A%22%22%7D%2C%22ffAwareSearchOptOut%22%3Afalse%2C%22enableDesktopHighlights%22%3Afalse%2C%22enableVolumePricing%22%3Afalse%2C%22enableCopyBlock%22%3Atrue%2C%22enableVariantCount%22%3Afalse%2C%22enableSlaBadgeV2%22%3Afalse%2C%22cat_id%22%3A%22%22%2C%22_be_shelf_id%22%3A%22%22%7D%2C%22enableFashionTopNav%22%3Afalse%2C%22enableUnifiedSchema%22%3Afalse%2C%22version%22%3A%22v1%22%2C%22enableRelatedSearches%22%3Atrue%2C%22enablePortableFacets%22%3Atrue%2C%22enableFacetCount%22%3Atrue%2C%22fetchMarquee%22%3Atrue%2C%22fetchSkyline%22%3Atrue%2C%22fetchGallery%22%3Afalse%2C%22fetchSbaTop%22%3Atrue%2C%22fetchSBAV1%22%3Atrue%2C%22fungibilityEnabled%22%3Afalse%2C%22enableAdsPromoData%22%3Afalse%2C%22fetchDac%22%3Atrue%2C%22tenant%22%3A%22WM_GLASS%22%2C%22enableMultiSave%22%3Afalse%2C%22enableInStoreShelfMessage%22%3Afalse%2C%22enableSellerType%22%3Afalse%2C%22enableItemRank%22%3Afalse%2C%22enableOptimisticWeightUpdate%22%3Afalse%2C%22enableAdditionalSearchDepartmentAnalytics%22%3Atrue%2C%22enableFulfillmentTagsEnhacements%22%3Afalse%2C%22enableRxDrugScheduleModal%22%3Afalse%2C%22enablePromoData%22%3Atrue%2C%22enableSignInToSeePrice%22%3Afalse%2C%22enablePromotionMessages%22%3Afalse%2C%22enableDebugAnalyticsTags%22%3Afalse%2C%22enableItemLimits%22%3Afalse%2C%22enableCanAddToList%22%3Afalse%2C%22enableIsFreeWarranty%22%3Afalse%2C%22enableShopSimilarBottomSheet%22%3Afalse%2C%22adsParams%22%3A%7B%22fungibilityEnabled%22%3Afalse%7D%2C%22pageType%22%3A%22SearchPage%22%7D"

# # # payload = {}
# # # headers = {
# # #   'accept': 'application/json',
# # #   'accept-language': 'en-US',
# # #   'baggage': 'trafficType=customer,deviceType=desktop,renderScope=CSR,webRequestSource=Browser,pageName=searchResults,isomorphicSessionId=_-ALQLHfNx_NK8kMMpO6c,renderViewId=ef27f11a-3073-4d65-bb7a-b1eda8ff8985,requestTs=1771433766403,tpid=00-189565a0058a895b21f96d17b87831aa-39372f97d885c03e-00',
# # #   'content-type': 'application/json',
# # #   'dnt': '1',
# # #   'downlink': '10',
# # #   'dpr': '1',
# # #   'priority': 'u=1, i',
# # #   'referer': 'https://www.walmart.com/search?q=pet+food&page=1&affinityOverride=store_led',
# # #   'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
# # #   'sec-ch-ua-mobile': '?0',
# # #   'sec-ch-ua-platform': '"Windows"',
# # #   'sec-fetch-dest': 'empty',
# # #   'sec-fetch-mode': 'cors',
# # #   'sec-fetch-site': 'same-origin',
# # #   'tenant-id': 'elh9ie',
# # #   'traceparent': '00-189565a0058a895b21f96d17b87831aa-39372f97d885c03e-00',
# # #   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
# # #   'wm-client-traceid': '189561f34ec1ff5b2a3638eaef262443',
# # #   'wm_mp': 'true',
# # #   'wm_page_url': 'https://www.walmart.com/search?q=pet+food&page=1&affinityOverride=store_led',
# # #   'wm_qos.correlation_id': 'GCiKf5SD_WrS1Emrit4t2_lvuy7PBAjdm0Sc',
# # #   'x-apollo-operation-name': 'Search',
# # #   'x-enable-server-timing': '1',
# # #   'x-latency-trace': '1',
# # #   'x-o-bu': 'WALMART-US',
# # #   'x-o-ccm': 'server',
# # #   'x-o-correlation-id': 'GCiKf5SD_WrS1Emrit4t2_lvuy7PBAjdm0Sc',
# # #   'x-o-gql-query': 'query Search',
# # #   'x-o-mart': 'B2C',
# # #   'x-o-platform': 'rweb',
# # #   'x-o-platform-version': 'usweb-1.243.0-e08504e6f3bae36004c6a52bd1f73b0e76117f34-2171124r',
# # #   'x-o-segment': 'oaoh',
# # #   'Cookie': 'AID=wmlspartner=0:reflectorid=0000000000000000000000:lastupd=1765172170119; ACID=9d5b5e21-1f58-44b3-a57b-18fc9d0e8c4f; _m=9; hasACID=true; vtc=R7hZFM0JVruNRuFxQqj7mM; _pxhd=7f5441c867b511fe5651ddb6523ccb6611e27f35f4f356da86146e88089c41da:cd2679db-d3f7-11f0-af50-b81033491302; _pxvid=cd2679db-d3f7-11f0-af50-b81033491302; io_id=c49fd620-105b-4c8f-b72d-a8ea57355522; salsify_session_id=ec114256-b5c4-4d5e-bb0e-9cce4b95eeeb; dimensionData=628; assortmentStoreId=3081; hasLocData=1; abqme=true; adblocked=false; userAppVersion=usweb-1.243.0-e08504e6f3bae36004c6a52bd1f73b0e76117f34-2171124r; _intlbu=false; _shcc=US; bstc=SaPvHKbG_wF6GEFpwAsykg; xpth=x-o-mart%2BB2C~x-o-mverified%2Bfalse; xpa=0vKCf|3nZb8|4TT24|93YCK|CrRLy|DjPz2|E1bBU|HREf9|IWkmD|LL5Fh|R4YzC|TbgEV|Y5AMR|YAB9Q|_qtkl|d7Ltn|fdm-7|i9ziz|jM1ax|kWy4U|p0puX|sii4U|yhZMg; exp-ck=3nZb814TT24193YCK2CrRLy1E1bBU1HREf91IWkmD1LL5Fh2TbgEV1Y5AMR1_qtkl2d7Ltn1fdm-71kWy4U3; isoLoc=ID_AC_t3; _astc=073edc8d343eb9a5ff70d6f43fc9ad5b; pxcts=5855c8e1-0ce1-11f1-a541-6a66d64d5b43; locGuestData=eyJpbnRlbnQiOiJTSElQUElORyIsImlzRXhwbGljaXQiOmZhbHNlLCJzdG9yZUludGVudCI6IlBJQ0tVUCIsIm1lcmdlRmxhZyI6ZmFsc2UsImlzRGVmYXVsdGVkIjp0cnVlLCJwaWNrdXAiOnsibm9kZUlkIjoiMzA4MSIsInRpbWVzdGFtcCI6MTc2NTE3MjE3MDE1Miwic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCJ9LCJzaGlwcGluZ0FkZHJlc3MiOnsidGltZXN0YW1wIjoxNzY1MTcyMTcwMTUyLCJ0eXBlIjoicGFydGlhbC1sb2NhdGlvbiIsImdpZnRBZGRyZXNzIjpmYWxzZSwicG9zdGFsQ29kZSI6Ijk1ODI5IiwiZGVsaXZlcnlTdG9yZUxpc3QiOlt7Im5vZGVJZCI6IjMwODEiLCJ0eXBlIjoiREVMSVZFUlkiLCJ0aW1lc3RhbXAiOjE3NzEyODQ3MjE0NTksImRlbGl2ZXJ5VGllciI6bnVsbCwic2VsZWN0aW9uVHlwZSI6IkxTX1NFTEVDVEVEIiwic2VsZWN0aW9uU291cmNlIjpudWxsfV0sImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSJ9LCJwb3N0YWxDb2RlIjp7InRpbWVzdGFtcCI6MTc2NTE3MjE3MDE1MiwiYmFzZSI6Ijk1ODI5In0sIm1wIjpbXSwibXNwIjp7Im5vZGVJZHMiOltdLCJ0aW1lc3RhbXAiOm51bGx9LCJtcHMiOlsiMTUyNDA1OSIsIjE1MjE5OTAiLCIxNTIxOTg1IiwiMTUyNDE1MCIsIjE1MjE5NTgiLCIxNTI0NzYzIiwiMTUyNTQ0NSJdLCJtcERlbFN0b3JlQ291bnQiOjQsInNob3dMb2NhbEV4cGVyaWVuY2UiOmZhbHNlLCJzaG93TE1QRW50cnlQb2ludCI6ZmFsc2UsIm1wVW5pcXVlU2VsbGVyQ291bnQiOjAsInZhbGlkYXRlS2V5IjoicHJvZDp2Mjo5ZDViNWUyMS0xZjU4LTQ0YjMtYTU3Yi0xOGZjOWQwZThjNGYifQ%3D%3D; if_id=FMEZARSFXbVmJL4MYhAHD/tj6W1GTkUlFdLhPj+f4OP7V40MqsBJ1V9ui9sRH3tjfI3H08wDUWQ+EUb8kpCLSSwtv99qxphVekIIfob8PdyA51uV595mMapgfle1tiSBTcDUcR3GbDIPzxtl8jHRXWZktaJqG/ttGzgdn6P4gdZfCb05Dqoqf5agq8WBpIomiGETnFfxxDCqQVrcQxNkYzoYon0+9NleQytK4fjaYQGPqKnbzDWdSjlNYeDR99CJYXCFQ3E2VErehXQ14L82NxL23mOfNJz023g3Qzw+B93q8iRQtLrV3GRCb9ParE11RBz6OQV6gDdXznshki2a; TS016ef4c8=019bfcce3e9730cea1c4cb3e5f4b6288eeeefdc93383e6d00500c1fa6bfb0532fe1ae7728e6a183686b5f17f5a7094e2d9f9093469; TS01f89308=019bfcce3e9730cea1c4cb3e5f4b6288eeeefdc93383e6d00500c1fa6bfb0532fe1ae7728e6a183686b5f17f5a7094e2d9f9093469; TS8cb5a80e027=0845315512ab200081c113bc06653dbb0dbea5d28c94b536fa5cbf794c68a51b2969f3b6ead41dd0086ff4719e113000e1b21d1be51abc00fd6db975d15e17feb072aa4dcd6690b7a1e5982afdb078bc479f19a54a2393be069dcb2c8fc8cc6f; bm_mi=58BCD2C9EF4C3E8F1183F06984CDA5F6~YAAQziR9chGHT2ecAQAAqIyhcR6igfLASye0P14WcdZEvXdIQBosSWxEfebeg5ITVK+m/B1Uvkjp7KQSJsgZiofUwvZIO75v0FPxxKnkE+gw5kw4021lruECGjPgzeC4T9q0d8h+XdYU+mlqtzsgbh7ft8QtzQDqGxbQpaX5OHiG5n6GyjWdO5T9efis3wC7EMucMujaKp8fg3NFZ09Wl1ohiHvBvMnHehCydzVspyH4I3CiXL3unLaPuhDFNVA8W+0+rzCNKtSGpKDwBQiBcjVn+Ltwd/804exLrFpRk+/NwRa8ObpJtvGEPVEZjMa6klMlPg==~1; bm_sv=F7FF5AAA89A3F011FE3958419CC0AE2C~YAAQziR9chKIT2ecAQAAXMahcR6WoASAtvjdqiKCSe8IfUmz2RVi8usax1EElnPLVPCqH86A5LWgGn/wOPGMJzqRsScGHaS2Pb7l8+7dIkHDTV1Wo+k/o6upcFpOS57HGpi4XCpoL0YDXO7DgY0NkWe7u5Wmol8eBf6KRvoTQ9hE/lsEvP+d+vUvDzy1v+XgqHUzwbbS30vfuiKWFHaaicNzba0YzQZReyo6itza01FWYe2+v6/rUw15FWJGPce/Ga4=~1; locDataV3=eyJhc3NvcnRtZW50Ijp7Im5vZGVJZCI6IjMwODEiLCJkaXNwbGF5TmFtZSI6IlNhY3JhbWVudG8gU3VwZXJjZW50ZXIiLCJpbnRlbnQiOiJQSUNLVVAifSwiZGVsaXZlcnkiOnsibm9kZUlkIjoiMzA4MSIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsImFkZHJlc3MiOnsicG9zdGFsQ29kZSI6Ijk1ODI5IiwiYWRkcmVzc0xpbmUxIjoiODkxNSBHRVJCRVIgUk9BRCIsImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSIsImNvdW50cnkiOiJVUyJ9LCJnZW9Qb2ludCI6eyJsYXRpdHVkZSI6MzguNDgyNjc3LCJsb25naXR1ZGUiOi0xMjEuMzY5MDI2fSwidHlwZSI6IkRFTElWRVJZIiwic2NoZWR1bGVkRW5hYmxlZCI6ZmFsc2UsInVuU2NoZWR1bGVkRW5hYmxlZCI6ZmFsc2UsImFjY2Vzc1BvaW50cyI6W3siYWNjZXNzVHlwZSI6IkRFTElWRVJZX0FERFJFU1MifV0sImlzRXhwcmVzc0RlbGl2ZXJ5T25seSI6ZmFsc2UsImFsbG93ZWRXSUNBZ2VuY2llcyI6WyJDQSJdLCJzdXBwb3J0ZWRBY2Nlc3NUeXBlcyI6WyJERUxJVkVSWV9BRERSRVNTIl0sInRpbWVab25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsInN0b3JlQnJhbmRGb3JtYXQiOiJXYWxtYXJ0IFN1cGVyY2VudGVyIiwic2VsZWN0aW9uVHlwZSI6IkxTX1NFTEVDVEVEIn0sImluc3RvcmUiOmZhbHNlLCJpbnRlbnQiOiJTSElQUElORyIsImlzRGVmYXVsdGVkIjp0cnVlLCJpc0V4cGxpY2l0IjpmYWxzZSwiaXNnZW9JbnRsVXNlciI6ZmFsc2UsInBpY2t1cCI6W3sibm9kZUlkIjoiMzA4MSIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsImFkZHJlc3MiOnsicG9zdGFsQ29kZSI6Ijk1ODI5IiwiYWRkcmVzc0xpbmUxIjoiODkxNSBHRVJCRVIgUk9BRCIsImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSIsImNvdW50cnkiOiJVUyJ9LCJnZW9Qb2ludCI6eyJsYXRpdHVkZSI6MzguNDgyNjc3LCJsb25naXR1ZGUiOi0xMjEuMzY5MDI2fSwic2NoZWR1bGVkRW5hYmxlZCI6dHJ1ZSwidW5TY2hlZHVsZWRFbmFibGVkIjp0cnVlLCJzdG9yZUhycyI6IjA2OjAwLTIzOjAwIiwiYWxsb3dlZFdJQ0FnZW5jaWVzIjpbIkNBIl0sInN1cHBvcnRlZEFjY2Vzc1R5cGVzIjpbIlBJQ0tVUF9TUEVDSUFMX0VWRU5UIiwiUElDS1VQX0lOU1RPUkUiLCJQSUNLVVBfQ1VSQlNJREUiXSwidGltZVpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwic3RvcmVCcmFuZEZvcm1hdCI6IldhbG1hcnQgU3VwZXJjZW50ZXIiLCJzZWxlY3Rpb25UeXBlIjoiREVGQVVMVEVEIn1dLCJzaGlwcGluZ0FkZHJlc3MiOnsibGF0aXR1ZGUiOjM4LjQ4NzU2NzcsImxvbmdpdHVkZSI6LTEyMS4zNDI3MjYyLCJwb3N0YWxDb2RlIjoiOTU4MjkiLCJjaXR5IjoiU2FjcmFtZW50byIsInN0YXRlIjoiQ0EiLCJjb3VudHJ5Q29kZSI6IlVTQSIsImdpZnRBZGRyZXNzIjpmYWxzZSwidGltZVpvbmUiOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwiYWxsb3dlZFdJQ0FnZW5jaWVzIjpbIkNBIl19LCJtcHMiOlsiMTUyNDA1OSIsIjE1MjE5OTAiLCIxNTIxOTg1IiwiMTUyNDE1MCIsIjE1MjE5NTgiLCIxNTI0NzYzIiwiMTUyNTQ0NSJdLCJtcERlbFN0b3JlQ291bnQiOjQsInJlZnJlc2hBdCI6MTc3MTQ1NDU1ODQ3OSwidmFsaWRhdGVLZXkiOiJwcm9kOnYyOjlkNWI1ZTIxLTFmNTgtNDRiMy1hNTdiLTE4ZmM5ZDBlOGM0ZiJ9; xptwj=uz:f9ccab35953d6cbb90d8:2w9RCvRNlwmdg6n6DXfF81JUWb3+csHOc3X3siY5g2t7F+f33a3dedBu3Myzlyv576r5V96c+0oh29M5/mqbDix4BBeVXEaERaol4j5eq8fp7xSNmjqsETAtmYxs90kD6nDkqSgUMTFjwoTRJiC+uYaiixIREqG1q7f7aZQNFR8ALP5YXSxJC1E/qqLN+iALOBjcva5cV/1bCTzPYJws+A==; akavpau_p2=1771433560~id=78483bffa1970e4aedef07a75e996889; ak_bmsc=C899C70AF6F91B6E66BFE241E7E0993E~000000000000000000000000000000~YAAQziR9ctqIT2ecAQAACuChcR4n6SXV9kikdIKHO27AbartqOupPiwcDI5Fvais83xEexA6Mb+spewR+Um0YtIS+qDpMzzQuSV5DGoTT1wHKQwgvYE/kXo+GtiDHzY6oUmCX32v+KiJplBTno47Ajq9+j0sTMa47GMEtwwVewd1YWwj0+uPR/yNCFrBhrGaGdte2YIJpAgC1E0hAiij945rlFYSA2YhOpMe/xW6L213JueUv/fYATbeCmGTjeeSGt8q4ddC4jRP5xKd+g2OhnIupHubN+G2vI4ZDw48WJqLtc/u1KVpqaugFrgg/FfJgFCSMShuUTkDP4UYFEvF+FE2EnWmCwO1/v7VmTvv713AF7/VQAkZfNM9pNDDaM5Tjc0spMzJDWzDMu54zZB7BYesJBCKGJvic0ZTDPRuHCKCYNY0VQ==; com.wm.reflector="reflectorid:0000000000000000000000^@lastupd:1771433765000^@firstcreate:1765172170119"; xptc=_m%2B9~assortmentStoreId%2B3081; xpm=0%2B1771433765%2BR7hZFM0JVruNRuFxQqj7mM~%2B0; xptwg=490583940:62F60CAFC833D0:EFF035:5A474076:7C227A33:2E42A889:; TS01a90220=019c9c570f9523a0db5397c3ab5e95a49b0bf4736ef190c1450fdc9d0bdb06b60306f2057c9657c59450673774a748cc0a310a289e; TS012768cf=01a0d573a9ee818ffc384fdc8f0f8d4e95eee744b274e0faf283da4d1cc23405a9ae94a12f92d93f6d856a9411f58cceedbd7337bd; TS2a5e0c5c027=088e9971c7ab20008282975cc1a4340cc94a1594768e682b93a992e9caed46626d4ca2b5c052934308f18d01141130005c7376b64218cbeebcce928a0cf7e4627ad1f343920af42919d306d3df48da22d6716cc40376583962308ce06eeb1e73; TS01a90220=0119f68bc43ed596e69abb65b9fc7a6b6a239cab757133fe3ee010f8e8b29eca018eac58e3079e01608ccbda857915a06285db4e17; bm_sv=F7FF5AAA89A3F011FE3958419CC0AE2C~YAAQ6MgwF5fb+2qcAQAATtipcR6Y9dp5+Ot+C8yr9WT6VtH8Pkpmv80lAcgrkkUk1Ez/H2gQTpRHhhBbB5C5b2KbTPLYHXFpqZd3NrIalD7SBQKlp2kOklFMMnhVuaDljLjFZEfpuaeu/yCLnf6Ng52rbvnbLIjICVxJ3qdzVukoP7//zgXpbrxKGr3McCGu9YkY88d2AEQ9+ofChLxPqs18E9AYbblGnQlTTy3foT317DRAimXlo8nH1Bl/fu/D9eI=~1; bstc=SaPvHKbG_wF6GEFpwAsykg; com.wm.reflector="reflectorid:0000000000000000000000@lastupd:1771433482000@firstcreate:1765172170119"; exp-ck=3nZb814TT24193YCK2CrRLy1E1bBU1HREf91IWkmD1LL5Fh2TbgEV1Y5AMR1_qtkl2d7Ltn1fdm-71kWy4U3; vtc=R7hZFM0JVruNRuFxQqj7mM; xpa=0vKCf|3nZb8|4TT24|93YCK|CrRLy|DjPz2|E1bBU|HREf9|IWkmD|LL5Fh|R4YzC|TbgEV|Y5AMR|YAB9Q|_qtkl|d7Ltn|fdm-7|i9ziz|jM1ax|kWy4U|p0puX|sii4U|yhZMg; xpm=0%2B1771433480%2BR7hZFM0JVruNRuFxQqj7mM~%2B0; xptc=assortmentStoreId%2B3081~_m%2B9; xpth=x-o-mart%2BB2C~x-o-mverified%2Bfalse; xptwg=3052595809:5869764C418730:D65C73:AFB0DB96:C3067555:DBA0E7BB:; xptwj=uz:c46ef1f918a28a8af62d:HpBaekOvbwjp1RjvepdC5CbecbG/Ut0qLbO/Sd3JTtqvAb+ZhuOFaW9AjOur1mT9XjjIfPCjAkZnNAIYQs+eSn0t5OMUFl31CynJ2/npbGbutvfs95ot9FdidHLeDQvtISDgqYJXE681uW4KbLeFAO2+Qv0zrlDcBN7cpgiGk3QfoDHTG07Yns8Jwl/htj9kB8xIf6FBJyn9jK22n4HV2w==; TS012768cf=0119f68bc43ed596e69abb65b9fc7a6b6a239cab757133fe3ee010f8e8b29eca018eac58e3079e01608ccbda857915a06285db4e17; TS2a5e0c5c027=08dbd8a4e0ab200037d97dbbec0a2c47eb7291081effb368f3d147b900f378b8852989d7c8f5e30508e32e8e00113000fbc78229b4820c0451190621ba8a4f2777f6470c525001a80604fd7b7b4bc6a7e56fd6e8d06200f606f1f6aed78a696c; _m=9; abqme=true; akavpau_p2=1771434082~id=09c815a0cac16b2b7af9c411c17bee6f; isoLoc=ID_AC_t3'
# # # }

# # # response = requests.request("GET", url, headers=headers, data=payload)

# # # # print(response.text)
# # # # ... kode request kamu ...
# # # response = requests.request("GET", url, headers=headers, data=payload)

# # # # 1. Pastikan request berhasil (status code 200)
# # # if response.status_code == 200:
# # #     # 2. Ubah response menjadi dictionary/list Python
# # #     data_json = response.json()

# # #     # 3. Simpan ke file bernama 'data.json'
# # #     with open('data.json', 'w', encoding='utf-8') as f:
# # #         json.dump(data_json, f, ensure_ascii=False, indent=4)
    
# # #     print("Data berhasil disimpan ke data.json!")
# # # else:
# # #     print(f"Gagal mengambil data. Status code: {response.status_code}")


# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.chrome.options import Options
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC

# # # Setup Chrome Options agar tidak terlalu terlihat seperti bot
# # chrome_options = Options()
# # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# # chrome_options.add_experimental_option('useAutomationExtension', False)

# # # Inisialisasi Driver
# # driver = webdriver.Chrome(options=chrome_options)

# # try:
# #     url = "https://www.walmart.com/search?q=pet+food"
# #     driver.get(url)

# #     # Menunggu sampai elemen section muncul (timeout 10 detik)
# #     wait = WebDriverWait(driver, 10)
    
# #     # Selector ini mencari tag <a> yang berada di dalam item-stack di section tersebut
# #     # Kita gunakan data-testid="item-stack" karena itu identitas yang stabil di Walmart
# #     product_links = wait.until(EC.presence_of_all_elements_located(
# #         (By.CSS_SELECTOR, 'div[data-testid="item-stack"] a[link-identifier]')
# #     ))

# #     print(f"Ditemukan {len(product_links)} produk.\n")

# #     for index, link in enumerate(product_links):
# #         href = link.get_attribute('href')
# #         # Kita ambil teks judulnya juga jika ada di dalam span/h3
# #         title = link.text.split('$')[0].strip() 
        
# #         print(f"{index + 1}. Judul: {title}")
# #         print(f"   URL: {href}\n")

# # finally:
# #     # Jangan lupa tutup browser
# #     # driver.quit()
# #     pass


# from seleniumbase import Driver
# import json
# import time
# import random

# def scrape_walmart_final():
#     # Menggunakan uc=True dan incognito=False agar lebih terlihat seperti user biasa
#     driver = Driver(uc=True, headless=False, incognito=False)
    
#     try:
#         url = "https://www.walmart.com/search?q=pet+food"
#         print("Membuka Walmart...")
        
#         # Buka dengan proteksi UC
#         driver.uc_open_with_reconnect(url, reconnect_time=5)
        
#         # Penanganan Captcha 'Press and Hold'
#         for i in range(3): # Coba cek captcha 3 kali
#             if "Robot or human?" in driver.get_page_source():
#                 print(f"Percobaan bypass ke-{i+1}...")
#                 driver.uc_gui_click_captcha() # Mencoba klik otomatis pada area tombol
#                 time.sleep(5)
#             else:
#                 break

#         # Tunggu manual jika bypass otomatis gagal
#         if "Robot or human?" in driver.get_page_source():
#             print("\a") # Bunyi Beep untuk memberi tahu kamu
#             print("!!! BYPASS GAGAL !!!")
#             print("Silakan TEKAN DAN TAHAN tombol di browser secara MANUAL dalam 15 detik.")
#             time.sleep(15)

#         # Verifikasi apakah elemen produk sudah muncul
#         selector = 'div[data-testid="item-stack"] a[link-identifier]'
#         try:
#             driver.wait_for_element(selector, timeout=20)
#             print("Berhasil mendarat di halaman produk!")
#         except Exception:
#             print("Masih tertahan atau halaman tidak memuat produk.")
#             return

#         # --- EKSTRAKSI DATA ---
#         # Scroll perlahan agar semua item ter-render (simulate human)
#         for _ in range(3):
#             driver.execute_script(f"window.scrollBy(0, {random.randint(400, 700)});")
#             time.sleep(1)

#         elements = driver.find_elements(selector)
#         product_data = []

#         for el in elements:
#             try:
#                 # Ambil href dan title
#                 href = el.get_attribute('href')
#                 title = el.get_attribute('aria-label')
                
#                 # Bersihkan URL dari parameter tracking jika perlu
#                 if href and "walmart.com" in href:
#                     clean_url = href.split('?')[0] if '?' in href else href
#                     product_data.append({
#                         "title": title if title else "No Title",
#                         "url": clean_url
#                     })
#             except:
#                 continue

#         # Simpan ke JSON
#         with open('walmart_pet_food.json', 'w', encoding='utf-8') as f:
#             json.dump(product_data, f, indent=4, ensure_ascii=False)
            
#         print(f"Sukses! {len(product_data)} produk disimpan ke walmart_pet_food.json")

#     except Exception as e:
#         print(f"Terjadi kesalahan fatal: {e}")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     scrape_walmart_final()


from seleniumbase import Driver
import csv
import time
import random

def scrape_walmart_to_csv():
    # Inisialisasi Driver UC Mode
    driver = Driver(uc=True, headless=False)
    
    # Nama file CSV
    filename = 'walmart_pet_food.csv'
    
    # Menyiapkan file CSV dan menulis Header
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'URL']) # Header kolom

    try:
        # Loop dari halaman 1 sampai 25
        for page in range(1, 26):
            url = f"https://www.walmart.com/search?q=pet+food&page={page}&affinityOverride=store_led"
            print(f"\n--- Mengambil Halaman {page} ---")
            
            # Membuka halaman dengan proteksi UC
            driver.uc_open_with_reconnect(url, reconnect_time=5)
            
            # Cek jika ada captcha 'Press and Hold'
            if "Robot or human?" in driver.get_page_source():
                print(f"Halaman {page} tertahan captcha. Mencoba bypass otomatis...")
                driver.uc_gui_click_captcha()
                time.sleep(5)
            
            # Beri waktu tambahan agar konten benar-benar muncul
            selector = 'div[data-testid="item-stack"] a[link-identifier]'
            try:
                driver.wait_for_element(selector, timeout=15)
            except:
                print(f"Halaman {page} tidak memuat produk atau terblokir. Lewati...")
                continue

            # Scroll pelan-pelan (simulasi manusia membaca)
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(random.uniform(1, 2))

            # Ambil semua produk di halaman ini
            elements = driver.find_elements(selector)
            page_data = []

            for el in elements:
                try:
                    title = el.get_attribute('aria-label')
                    href = el.get_attribute('href')
                    if href:
                        # Bersihkan URL tracking
                        clean_url = href.split('?')[0] if '?' in href else href
                        page_data.append([title if title else "No Title", clean_url])
                except:
                    continue

            # Simpan data halaman ini ke CSV (append mode)
            with open(filename, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(page_data)

            print(f"Berhasil menyimpan {len(page_data)} produk dari halaman {page}.")

            # Jeda random antar halaman agar tidak terdeteksi sebagai bot (PENTING)
            jeda = random.uniform(3, 7)
            print(f"Menunggu {jeda:.2f} detik sebelum ke halaman berikutnya...")
            time.sleep(jeda)

        print(f"\nSelesai! Semua data (Halaman 1-25) tersimpan di {filename}")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_walmart_to_csv()