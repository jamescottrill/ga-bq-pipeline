from google.cloud import bigquery
export_schema = [
    bigquery.SchemaField("clientId", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("fullVisitorId", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("visitId", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("visitStartTime", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("totals", "RECORD", mode="REPEATED",
                         fields=[
                             bigquery.SchemaField("hits", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("pageviews", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("timeOnSite", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("bounces", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("transactions", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("totalTransactionRevenue", "INTEGER", mode="NULLABLE"),
                         ]
                         ),
    bigquery.SchemaField("trafficSource", "RECORD", mode="REPEATED",
                         fields=[
                             bigquery.SchemaField("referralPath", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("campaign", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("medium", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("keyword", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("adcontent", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("adwordsClickInfo", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("gclid", "STRING", mode="NULLABLE")
                                                  ]
                                                  ),

                             bigquery.SchemaField("isTrueDirect", "BOOLEAN", mode="NULLABLE")
                         ]
                         ),
    bigquery.SchemaField("channelGrouping", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("device", "RECORD", mode="NULLABLE",
                         fields=[
                             bigquery.SchemaField("browser", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("browserVersion", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("browserSize", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("operatingSystem", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("isMobile", "BOOLEAN", mode="NULLABLE"),
                             bigquery.SchemaField("mobileDeviceBranding", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("mobileDeviceModel", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("mobileDeviceInfo", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("language", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("screenResolution", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("deviceCategory", "STRING", mode="NULLABLE")
                         ],
                         ),
    bigquery.SchemaField("customDimensions", "RECORD", mode="REPEATED",
                         fields=[
                             bigquery.SchemaField("index", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("value", "STRING", mode="NULLABLE")
                         ]
                         ),
    bigquery.SchemaField("customMetrics", "RECORD", mode="REPEATED",
                         fields=[
                             bigquery.SchemaField("index", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("value", "STRING", mode="NULLABLE")
                         ]
                         ),
    bigquery.SchemaField("geoNetwork", "RECORD", mode="NULLABLE",
                         fields=[
                             bigquery.SchemaField("continent", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("subContinent", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("region", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("metro", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("cityId", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("latitude", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("longitude", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("networkDomain", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("networkLocation", "STRING", mode="NULLABLE")
                         ]
                         ),
    bigquery.SchemaField("hits", "RECORD", mode="REPEATED",
                         fields=[
                             bigquery.SchemaField("hitNumber", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("time", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("hour", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("minute", "INTEGER", mode="NULLABLE"),
                             bigquery.SchemaField("isInteraction", "BOOLEAN", mode="NULLABLE"),
                             bigquery.SchemaField("isEntrance", "BOOLEAN", mode="NULLABLE"),
                             bigquery.SchemaField("isExit", "BOOLEAN", mode="NULLABLE"),
                             bigquery.SchemaField("referrer", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("type", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("page", "RECORD", mode="NULLABLE",
                                                  fields=[
                                                      bigquery.SchemaField("pagePath", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("hostname", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("pageTitle", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("pagePathLevel1", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("pagePathLevel2", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("pagePathLevel3", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("pagePathLevel4", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("searchKeyword", "STRING", mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("transaction", "RECORD", mode="NULLABLE",
                                                  fields=[
                                                      bigquery.SchemaField("transactionId", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("transactionRevenue", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("transactionTax", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("transactionShipping", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("affiliation", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("currencyCode", "STRING", mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("eventInfo", "RECORD", mode="NULLABLE",
                                                  fields=[
                                                      bigquery.SchemaField("eventCategory", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("eventAction", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("eventLabel", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("eventValue", "INTEGER", mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("product", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("productSKU", "STRING", mode="NULLABLE"),

                                                      bigquery.SchemaField("v2ProductName", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("v2ProductCategory", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("productVariant", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("productBrand", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("productRevenue", "INTEGER", mode="NULLABLE"),
                                                      bigquery.SchemaField("productPrice", "INTEGER", mode="NULLABLE"),
                                                      bigquery.SchemaField("productQuantity", "INTEGER", mode="NULLABLE"),
                                                      bigquery.SchemaField("isImpression", "BOOLEAN", mode="NULLABLE"),
                                                      bigquery.SchemaField("isClick", "BOOLEAN", mode="NULLABLE"),
                                                      bigquery.SchemaField("customDimensions", "RECORD",
                                                                           mode="REPEATED",
                                                                           fields=[
                                                                               bigquery.SchemaField("index", "INTEGER",
                                                                                                    mode="NULLABLE"),
                                                                               bigquery.SchemaField("value", "STRING",
                                                                                                    mode="NULLABLE")
                                                                           ]
                                                                           ),
                                                      bigquery.SchemaField("customMetrics", "RECORD", mode="REPEATED",
                                                                           fields=[
                                                                               bigquery.SchemaField("index", "INTEGER",
                                                                                                    mode="NULLABLE"),
                                                                               bigquery.SchemaField("value", "STRING",
                                                                                                    mode="NULLABLE")
                                                                           ]
                                                                           ),
                                                      bigquery.SchemaField("productListName", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("productListPosition", "INTEGER",
                                                                           mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("promotion", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("promoCreative", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("promoId", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("promoName", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("promoPosition", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("promotionActionInfo", "RECORD",
                                                                           mode="NULLABLE",
                                                                           fields=[
                                                                               bigquery.SchemaField("promoIsView",
                                                                                                    "BOOLEAN",
                                                                                                    mode="NULLABLE"),
                                                                               bigquery.SchemaField("promoIsClick",
                                                                                                    "BOOLEAN",
                                                                                                    mode="NULLABLE")
                                                                           ]
                                                                           )
                                                  ]
                                                  ),
                             bigquery.SchemaField("eCommerceAction", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("action_type", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("option", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("step", "INTEGER", mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("experiment", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("experimentId", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("experimentVariant", "STRING",
                                                                           mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("customDimensions", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("index", "INTEGER", mode="NULLABLE"),
                                                      bigquery.SchemaField("value", "STRING", mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("customMetrics", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("index", "INTEGER", mode="NULLABLE"),
                                                      bigquery.SchemaField("value", "STRING", mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("social", "RECORD", mode="REPEATED",
                                                  fields=[
                                                      bigquery.SchemaField("socialInteractionNetwork", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("socialInteractionAction", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("socialInteractions", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("socialInteractionTarget", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("socialNetwork", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("uniqueSocialInteractions", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("hasSocialSourceReferral", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("socialInteractionNetworkAction", "STRING",
                                                                           mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("latencyTracking", "RECORD", mode="NULLABLE",
                                                  fields=[
                                                      bigquery.SchemaField("pageLoadSample", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("pageLoadTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("pageDownloadTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("redirectionTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("speedMetricsSample", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("domainLookupTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("serverConnectionTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("serverResponseTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("domLatencyMetricsSample", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("domInteractiveTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("domContentLoadedTime", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("userTimingValue", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("userTimingSample", "INTEGER",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("userTimingVariable", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("userTimingCategory", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("userTimingLabel", "STRING",
                                                                           mode="NULLABLE")
                                                  ]
                                                  ),
                             bigquery.SchemaField("contentGroup", "RECORD", mode="NULLABLE",
                                                  fields=[
                                                      bigquery.SchemaField("contentGroup1", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("contentGroup2", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("contentGroup3", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("contentGroup4", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("contentGroup5", "STRING", mode="NULLABLE"),
                                                      bigquery.SchemaField("previousContentGroup1", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("previousContentGroup2", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("previousContentGroup3", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("previousContentGroup4", "STRING",
                                                                           mode="NULLABLE"),
                                                      bigquery.SchemaField("previousContentGroup5", "STRING",
                                                                           mode="NULLABLE")
                                                  ]
                                                  ),
                              bigquery.SchemaField("datasource", "STRING", mode="NULLABLE")
                             ]
                         )
]
