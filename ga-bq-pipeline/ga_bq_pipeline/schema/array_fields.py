hitType = {'pageview': 'PAGE', 'transaction': 'TRANSACTION', 'event': 'EVENT', 'screenview': 'APPVIEW',
           'social': 'SOCIAL', 'exception': 'EXCEPTION', 'item': 'ITEM', 'timing': 'TIMING'}

totals_order = ['hits', 'pageViews', 'timeOnSite', 'bounces', 'totalTransactionRevenue', 'transactions']

traffic_source_order = ["referralPath", 'campaign', 'source', 'medium', 'keyword', 'adContent', 'adwordsClickInfo']

geo_network_order = ['continent', 'subContinent', 'region', 'metro', 'city', 'cityId', 'latitude', 'longitude',
                     'networkDomain', 'networkLocation']

device_order = ['browser', 'browserVersion', 'browserSize', 'operatingSystem', 'isMobile', 'mobileDeviceBranding',
                'mobileDeviceModel', 'mobileDeviceInfo', 'language', 'screenResolution', 'deviceCategory']

session_order = ['clientId', 'fullVisitorId', 'visitId', 'visitStartTime', 'date', 'totals', 'trafficSource', 'device',
                 'customDimensions', 'customMetrics', 'geoNetwork', 'hits', 'channelGrouping']

hits_page_order = ['pagePath', 'hostname', 'pageTitle', 'pagePathLevel1', 'pagePathLevel2', 'pagePathLevel3',
                   'pagePathLevel4', 'searchKeyword']

hits_latency_tracking_order = ['pageLoadSample', 'pageLoadTime', 'pageDownloadTime',
                               'redirectionTime', 'speedMetricsSample', 'domainLookupTime', 'serverConnectionTime',
                               'serverResponseTime', 'domLatencyMetricsSample', 'domInteractiveTime',
                               'domContentLoadedTime', 'userTimingValue', 'userTimingSample', 'userTimingVariable',
                               'userTimingCategory', 'userTimingLabel']

hits_transaction_order = ['transactionId', 'transactionRevenue', 'transactionTax', 'transactionShipping', 'affiliation',
                          'currencyCode']

hits_content_order = ['contentGroup1', 'contentGroup2', 'contentGroup3', 'contentGroup4', 'contentGroup5',
                      'previousContentGroup1', 'previousContentGroup2', 'previousContentGroup3',
                      'previousContentGroup4', 'previousContentGroup5']

hits_experiment_order = ['experimentId', 'experimentVariant']

hits_ecommerce_action_order = ['action_type', 'option', 'step']

ecommerce_action_type = {'click': '1', 'detail': '2', 'add': '3', 'remove': '4', 'checkout': '5', 'purchase': '6',
                         'refund': '7', 'checkout_option': '8'}

hits_promotion_order = ['promoCreative', 'promoId', 'promoName', 'promoPosition', 'promotionActionInfo']

promotion_action_order = ['promoIsView', 'promoIsClick']

hits_product_order = ['productSKU', 'v2ProductName', 'v2ProductCategory', 'productVariant', 'productBrand',
                      'productRevenue', 'productPrice', 'productQuantity', 'isImpression', 'isClick',
                      'customDimensions', 'customMetrics', 'productListName', 'productListPosition']

hits_social_order = ['socialInteractionNetwork', 'socialInteractionAction', 'socialInteractions',
                     'socialInteractionTarget', 'socialNetwork', 'uniqueSocialInteractions', 'hasSocialSourceReferral',
                     'socialInteractionNetworkAction']

hits_order = ['hitNumber', 'time', 'hour', 'minute', 'isInteraction', 'isEntrance', 'isExit', 'referrer', 'type',
              'page', 'transaction', 'eventInfo', 'product', 'promotion', 'eCommerceAction', 'experiment',
              'customDimensions', 'customMetrics', 'social', 'latencyTracking', 'contentGroup', 'datasource']

custom_order = ['index', 'value']

empty_product = {k: None for k in hits_product_order}
empty_cmd = [{k: None for k in custom_order}]
empty_product['customDimensions'] = empty_cmd
empty_product['customMetrics'] = empty_cmd
geo_network = {k: None for k in geo_network_order}
latency = {k: None for k in hits_latency_tracking_order}
promo_action = {k: None for k in promotion_action_order}
hits_promo = {k: None for k in hits_promotion_order}
hits_promo['promotionActionInfo'] = promo_action
hits_social = {k: None for k in hits_social_order}
empty_device = {'screenResolution': None,
                   'browserSize': None,
                   'language': None,
                   'browser': None,
                   'browserVersion': None,
                   'deviceCategory': None,
                   'operatingSystem': None,
                   'isMobile': False,
                   'mobileDeviceModel': '',
                   'mobileDeviceBranding': None,
                   'mobileDeviceInfo': None
                   }