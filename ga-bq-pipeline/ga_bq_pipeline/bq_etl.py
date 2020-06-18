import urllib.parse as parse_qs
from urllib3.util import parse_url as parse
from datetime import timedelta, date
import re
from google.api_core.exceptions import NotFound
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import jsonlines
import json
from user_agents import parse as ua_parse
from google.oauth2 import service_account
from ga_bq_pipeline.schema.tables import export_schema
from ga_bq_pipeline.schema.array_fields import *
from ga_bq_pipeline.ETL import *


# UPDATE THESE
CUSTOM_DEFINITION_OFFSET = 100
USER_AGENT_CD = '30'
#Social Source Regex
socialRe = 'fb|facebook|t.co|twitter|pinterest|linkedin|linked.in|insta|ig|vsco|reddit|digg|myspace'
##YOU CAN STOP NOW

APP_NAME = 'ga_bq_pipeline'

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# env config path directory
CONF_FILE_PATH = os.path.join(MODULE_PATH, 'conf')

# arguments file path definition
ARGS_FILE_NAME = os.path.join(CONF_FILE_PATH, 'args.yaml')

# logger name
LOGGER_NAME = __name__

PYTHON_MIN_VERSION = (3, 6)

job_config = bigquery.LoadJobConfig(
    schema=export_schema,
    source_format='NEWLINE_DELIMITED_JSON'
)



class PIPELINE(ETL):

    def pre_execution_checks(self):
        """
        1. Check that the target dataset and table exists, if not create it.
        2. Check that the cloud storage bucket exists, if not, create it.
        """
        self.check_create_tables()
        self.check_create_bucket()

    def pipeline(self):
        """
        1. Fetch the data from BigQuery
        2. Combine the data into dataframes grouped by session Id
        3. Process each session into the output format.
        4. Upload
        """
        data = self.get_data()
        grouped_sessions, session_ids = self.prepare_data(data)
        results = self.process_data(grouped_sessions, session_ids)
        self.upload_to_cloud(results)

    def post_execution(self):
        """
        1. If the JSON file has been created, upload it to cloud storage.
        """
        file = 'output{}.jsonl'.format(self.args['date'])
        if file in os.listdir():
            self.upload_to_gs(file)
            os.remove(file)

    def check_create_tables(self):
        bq = self.bq_client
        dataset = bigquery.Dataset('{}.{}'.format(self.bigquery['project'], self.bigquery['dataset']))
        dataset.location = 'EU'
        try:
            bq.get_dataset(dataset)
        except NotFound:
            bq.create_dataset(dataset)
        table = dataset.table(self.bigquery['table'])
        try:
            bq.get_table(table)
        except NotFound:
            table = bigquery.Table(table, schema=export_schema)
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="date"
            )
            bq.create_table(table)
        return

    def check_create_bucket(self):
        gs = self.gs_client
        bucket = storage.Bucket(client=gs, name=self.storage['bucket'])
        bucket.location = 'EU'
        try:
            gs.get_bucket(bucket)
        except NotFound:
            gs.create_bucket(bucket)
        return

    def query_data(self):
        """
        This queries the BigQuery table to get all the hits from the relevant date. This may need to be updated
        depending on how your hits are ingested into BigQuery
        """
        query = 'SELECT jsonPayload.*, timestamp FROM {project}.{dataset}.{table} WHERE jsonPayload.t !=\'timing\' ' \
                'AND jsonPayload.t != \'adtiming\' ORDER BY timestamp'.format(project=self.bigquery['source_project'],
                                                                              dataset=self.bigquery['source_dataset'],
                                                                              table=self.bigquery['source_table'] +
                                                                                    self.args['date'])
        query_req = self.bq_client.query(query)
        rows = query_req.result()
        df = bigquery.table.RowIterator.to_dataframe(rows)
        df = df.applymap(lambda x: parse_qs.unquote(x) if isinstance(x, str) else x)
        return df

    @staticmethod
    def collapse_session_cdm(cdm):
        """
        @param cdm: An array of Custom Dimensions or Metrics in the form {index: x, value: y}
        @return: A formatted array of Custom Dimensions or Metrics
        """
        values = list(map(lambda x: {x.get('index'): x.get('value')}, cdm))
        values = list(filter(lambda x: x != {None: None}, values))
        obj = {}
        arr = []
        for item in values:
            for k, v in item.items():
                obj[k] = v
        for k, v in obj.items():
            arr.append({'index': k, 'value': v})
        return arr if len(arr) > 0 else empty_cmd

    # noinspection PyBroadException
    @staticmethod
    def retrieve_value(obj, key, index, default=None):
        """
        Get the specific key
        @param obj: The session object
        @param key: The column name (GA Hit Key)
        @param index: The hit number
        @param default: value to return if none found.
        @return: The value found at the specified index
        """
        try:
            return obj.get(key).iloc[index]
        except Exception:
            return default

    def custom_definition(self, obj, key, limit, y, def_type, scope):
        """
        @param obj: The Session object
        @param key: The key that assigns to the custom definition
        @param limit: The number of custom dimensions to look through
        @param y: The hit number
        @param def_type: is this a dimension or metric?
        @param scope: The scope of the custom dimension/metric.
        @return: An array containing an index and value column.
        """
        df = []
        for i in range(1, limit + 1):
            result = {}
            var = key + str(i)
            var_s = key + str(i + CUSTOM_DEFINITION_OFFSET)
            try:
                if obj.get(var).iloc[y] is not None:
                    if obj.get(var_s).iloc[y] in scope:
                        result['index'] = i
                        value = self.retrieve_value(obj, var, y)
                        result['value'] = int(value) if def_type == 'metric' else value
                        df.append(result.copy())
            except (KeyError, AttributeError):
                pass
        return df if df != [] else empty_cmd

    def get_hit_time(self, session, index):
        """
        @param session: The session object
        @param index: The hit number
        @return: Timestamp for the hit
        """
        return self.retrieve_value(session, 'timestamp', index)

    @staticmethod
    def get_page_path_level(url, index):
        """
        @param url: The full page URL
        @param index: Page Path level index
        @return: Single level of the page path
        """
        try:
            path = url.path.split('/')[index]
            path = '/' + path + ('/' if path != '' else '')
        except IndexError:
            path = ''
        return path

    def product_obj(self, session_obj, i, n, position, is_impression, is_click):
        """
        This creates a formatted product object
        @param session_obj: Session Array
        @param i: Product Index
        @param n: Hit Number
        @param position: Product Position
        @param is_impression: If the event is a product impression
        @param is_click: If the event is a product click
        @return: A single product object
        """
        i = str(i)
        obj = {
            'productSKU': self.retrieve_value(session_obj, 'pr' + i + 'id', n),
            'productListPosition': position,
            'productBrand': self.retrieve_value(session_obj, 'pr' + i + 'br', n),
            'productPrice': int(float(self.retrieve_value(session_obj, 'pr' + i + 'pr', n, 0)) * (10 ** 6)),
            'productVariant': self.retrieve_value(session_obj, 'pr' + i + 'va', n),
            'v2ProductName': self.retrieve_value(session_obj, 'pr' + i + 'id', n),
            'v2ProductCategory': self.retrieve_value(session_obj, 'pr' + i + 'ca,', n),
            'productListName': self.retrieve_value(session_obj, 'pr' + i + 'nm', n),
            'isImpression': is_impression,
            'isClick': is_click,
            'customDimensions': self.custom_definition(session_obj, 'pr1cd', 20, n, 'dimension', ['P']),
            'customMetrics': self.custom_definition(session_obj, 'pr1cm', 20, n, 'dimension', ['P'])
        }
        return obj

    def product_func(self, session_obj, n):
        """
        Process the product values for the hit, equates to the 'hits.products' record
        @param session_obj: Session object
        @param n: hit index
        @return: The product object
        """
        click_id = self.retrieve_value(session_obj, 'pr1id', n) if session_obj.get('pa').iloc[n] == 'click' else None
        products = []
        product_impression_click = False

        if session_obj.get('pa').iloc[n] == 'click' or session_obj.get('pa').iloc[n] is None:
            lists = session_obj.filter(regex='il\d+nm').iloc[n].dropna()
            list_keys = list(lists.index.map(lambda x: str(re.search('il(\d+)nm', x).group(1))))
            for key in list_keys:
                impressions = session_obj.filter(regex='il' + key + 'pi\d+id').iloc[n].dropna()
                impression_keys = list(impressions.index.map(lambda x: str(re.search('il\d+pi(\d+)id', x).group(1))))
                if len(impression_keys) > 0:
                    impression_keys.sort()
                    for i in impression_keys:
                        i = str(i)
                        product_id = self.retrieve_value(session_obj, 'il' + key + 'pi' + i + 'id', n)
                        is_click = True if (product_id == click_id and product_id is not None) else None
                        if is_click:
                            product_impression_click = True
                        hits_product = {
                            'productSKU': self.retrieve_value(session_obj, 'il' + key + 'pi' + i + 'id', n),
                            'productListPosition': int(i),
                            'productBrand': self.retrieve_value(session_obj, 'il' + key + 'pi' + i + 'br', n),
                            'productPrice': int(
                                float(self.retrieve_value(session_obj, 'il' + key + 'pi' + i + 'pr', n)) *
                                (10 ** 6)),
                            'productVariant': self.retrieve_value(session_obj, 'il' + key + 'pi' + i + 'va', n),
                            'v2ProductName': self.retrieve_value(session_obj, 'il' + key + 'pi' + i + 'nm', n),
                            'v2ProductCategory': self.retrieve_value(session_obj, 'il' + key + 'pi' + i + 'ca', n),
                            'productListName': self.retrieve_value(session_obj, 'il' + str(key) + 'nm', n),
                            'isImpression': True,
                            'isClick': is_click,
                            'customDimensions': self.custom_definition(session_obj, 'il' + key + 'pi' + i + 'cd', 20, n,
                                                                       'dimension', ['P']),
                            'customMetrics': self.custom_definition(session_obj, 'il' + key + 'pi  ' + i + 'cm', 20, n,
                                                                    'metric',
                                                                    ['P'])
                        }
                        # Product Custom Dimensions
                        hits_product = {k: hits_product.get(k) for k in hits_product_order}
                        products.append(hits_product.copy())

        if (session_obj.get('pa').iloc[n] == 'click' and not product_impression_click) or \
                session_obj.get('pa').iloc[n] in ['detail', 'add', 'remove']:
            is_click = True if session_obj.get('pa').iloc[n] == 'click' else None
            position = self.retrieve_value(session_obj, 'pr1ps', n)
            hits_product_action = self.product_obj(session_obj, 1, n, position, is_impression=None, is_click=is_click)
            hits_product_action = {k: hits_product_action.get(k) for k in hits_product_order}
            products.append(hits_product_action.copy())

        if session_obj.get('pa').iloc[n] in ['checkout', 'purchase']:
            prods = session_obj.filter(regex='pr\d+(id|nm)').iloc[n].dropna()
            product_keys = list(set(list(prods.index.map(lambda x: int(re.search('pr(\d+)(id|nm)', x).group(1))))))
            product_keys.sort()
            for i in product_keys:
                i = str(i)
                hits_product_check = self.product_obj(session_obj, i, n, position=None, is_impression=None,
                                                      is_click=None)
                hits_product_check = {k: hits_product_check.get(k) for k in hits_product_order}
                products.append(hits_product_check.copy())
        if len(products) == 0:
            products.append(empty_product)
        return products

    def process_hit(self, session, i):
        """
        Overall function called on each hit, equates to the 'hits' record
        @param session: The Session object
        @param i: Hit Index
        @return: The processed hit row
        """
        output = {'customDimensions': [], 'customMetrics': [], 'product': [], 'isExit': ''}
        hitsContentGroup = {}
        hitsPage = {}
        hits_transaction = {}

        expRe = '(.*)\.(\d+)'

        first_hit = self.get_hit_time(session, 0)

        # Declare Variables
        hit_time = self.get_hit_time(session, i)
        url = session.get('dl').iloc[i]
        groups = parse(url)

        # Hit Values
        output['hitNumber'] = int(i + 1)
        try:
            output['type'] = hitType.get(session.get('t').iloc[i]) or session.get('t').iloc[i]
        except AttributeError:
            output['type'] = None
        output['time'] = int(round(timedelta.total_seconds(hit_time - first_hit) * 1000))
        output['hour'] = int(hit_time.time().hour)
        output['minute'] = int(hit_time.time().minute)
        if i == 0:
            output['isEntrance'] = str('true')
        else:
            output['isEntrance'] = None
        j = len(session)
        while j > 0:
            if session.get('ni').iloc[j - 1] != '1':
                if i == (j - 1):
                    output['isExit'] = str('true')
                    break
                else:
                    output['isExit'] = None
            else:
                output['isExit'] = None
            j -= 1
        if session['ni'].iloc[i] == '1':
            output['isInteraction'] = str('false')
        else:
            output['isInteraction'] = str('true')
        # Event Values

        hitsEventInfo = {'eventCategory': self.retrieve_value(session, 'ec', i),
                         'eventAction': self.retrieve_value(session, 'ea', i),
                         'eventLabel': self.retrieve_value(session, 'el', i),
                         'eventValue': int(self.retrieve_value(session, 'ev', i)) if self.retrieve_value(session, 'ev',
                                                                                                         i) else None}

        output['eventInfo'] = hitsEventInfo.copy()

        output['customDimensions'] = self.custom_definition(session, 'cd', 20, i, 'dimension', ['H'])
        output['customMetrics'] = self.custom_definition(session, 'cm', 20, i, 'metric', ['H'])

        # Hit Content Groups
        for k in range(1, 6):
            hitsContentGroup['contentGroup' + str(k)] = self.retrieve_value(session, 'cg' + str(k), i) or '(not set)'
        # Previous Content Group
        if i == 0:
            hitsContentGroup['previousContentGroup1'] = '(entrance)'
            hitsContentGroup['previousContentGroup2'] = '(entrance)'
            hitsContentGroup['previousContentGroup3'] = '(entrance)'
            hitsContentGroup['previousContentGroup4'] = '(entrance)'
            hitsContentGroup['previousContentGroup5'] = '(entrance)'
        else:
            for k in range(1, 6):
                hitsContentGroup['previousContentGroup' + str(k)] = self.retrieve_value(session, 'cg' + str(k),
                                                                                        i - 1) or '(not set)'
        output['contentGroup'] = {k: hitsContentGroup.get(k) for k in hits_content_order}

        # Page Details
        hitsPage['pageTitle'] = session.get('dt').iloc[i]
        hitsPage['hostname'] = groups.host
        hitsPage['pagePath'] = groups.path

        hitsPage['pagePathLevel1'] = self.get_page_path_level(groups, 1)
        hitsPage['pagePathLevel2'] = self.get_page_path_level(groups, 2)
        hitsPage['pagePathLevel3'] = self.get_page_path_level(groups, 3)
        hitsPage['pagePathLevel4'] = self.get_page_path_level(groups, 4)
        output['page'] = {k: hitsPage.get(k) for k in hits_page_order}

        # Optimize Experiments
        eid = session.get('exp').iloc[i] or ''
        expParts = re.search(expRe, eid)
        if expParts:
            hits_experiment = {'experimentId': str(expParts.group(1)), 'experimentVariant': str(expParts.group(2))}
        else:
            hits_experiment = {'experimentId': None, 'experimentVariant': None}
        output['experiment'] = hits_experiment

        # Enhanced Ecommerce
        output['product'] = self.product_func(session, i)

        # eCommerceAction
        output['eCommerceAction'] = {
            'action_type': ecommerce_action_type.get(self.retrieve_value(session, 'pa', i), '0'),
            'option': self.retrieve_value(session, 'col', i),
            'step': int(self.retrieve_value(session, 'cos', i)) if self.retrieve_value(session, 'cos',
                                                                                       i) else None}

        # Transaction DataFrame
        if session['pa'].iloc[i] == 'purchase':
            hits_transaction = {'transactionId': self.retrieve_value(session, 'ti', i),
                                'affiliation': self.retrieve_value(session, 'ta', i),
                                'transaction': self.retrieve_value(session, 'tr', i),
                                'transactionTax': self.retrieve_value(session, 'tt', i),
                                'transactionShipping': self.retrieve_value(session, 'ts', i),
                                'transactionCoupon': self.retrieve_value(session, 'tc', i),
                                'currencyCode': self.retrieve_value(session, 'cu', i)
                                }

        output['transaction'] = {k: hits_transaction.get(k) for k in hits_transaction_order}

        output['promotion'] = hits_promo
        # Add hit to list of hits
        return {k: output.get(k) for k in hits_order}

    def device_func(self, obj):
        """
        Reformat the device format. In this, values have been sent with the hits, but if User Agent has been saved
        this could be parsed in a similar way. This equates to the 'deviceInformation' record.
        @param obj: Session object
        @return: The device information
        """
        user_agent = self.retrieve_value(obj, 'cd'+USER_AGENT_CD, 0)
        if user_agent:
            ua = ua_parse(user_agent)
            if ua.is_pc:
                device = 'desktop'
            elif ua.is_tablet:
                device = 'tablet'
            else:
                device = 'mobile'
            dev = {'screenResolution': self.retrieve_value(obj, 'sr', 0),
                   'browserSize': self.retrieve_value(obj, 'vp', 0),
                   'language': self.retrieve_value(obj, 'ul', 0),
                   'browser': ua.browser.family,
                   'browserVersion': ua.browser.version_string,
                   'deviceCategory': device,
                   'operatingSystem': ua.os.family + " " + ua.os.version_string,
                   'isMobile': False if ua.is_pc else True,
                   'mobileDeviceModel': None if ua.is_pc else ua.device.model,
                   'mobileDeviceBranding': None if ua.is_pc else ua.device.brand,
                   'mobileDeviceInfo': None if ua.is_pc else ua.device.brand + " " + ua.device.family + " " \
                                                             + ua.device.model
                   }
        else:
            dev = empty_device
        return {k: dev.get(k) for k in device_order}

    @staticmethod
    def query_string(url):
        """
        Extract specific querystring parameters from the URL
        @param url: The page URL
        @return: an array of querystring parameters and the values.
        """
        queryStringKeys = {'utm_source': 'cs', 'utm_medium': 'cm', 'utm_campaign': 'cn', 'utm_keyword': 'ck',
                           'utm_term': 'ck', 'utm_content': 'ct', 'gclid': 'gclid', 'fbclid': 'fbclid'}
        try:
            querystring = parse(url).query
        except IndexError:
            return {}
        ts = {}
        if querystring is not None:
            qs = list(map(lambda x: x.split('='), querystring.split('&')))
            for string in qs:
                if len(string) == 2:
                    k, v = string
                    if queryStringKeys.get(k):
                        ts[queryStringKeys.get(k)] = v
        return ts

    def traffic_func(self, obj):
        """
        Get the traffic source information. equates to the 'trafficSource' record
        @param obj: Session object
        @return: Array containing the traffic source.
        """
        trafficSource = {'adwordsClickInfo': {'gclid': None}}
        tsAdwordsClickInfo = {}
        tsSocial = {}
        landingUrl = self.retrieve_value(obj, 'dl', 0)
        ts = self.query_string(landingUrl)
        tsAdwordsClickInfo['gclid'] = ts.get('gclid')
        if ts.get('gclid'):
            trafficSource['source'] = str('google')
            trafficSource['medium'] = str('cpc')
        else:
            trafficSource['source'] = self.retrieve_value(obj, 'cs', 0) or ts.get('cs') \
                                      or self.retrieve_value(obj, 'dr', 0) or "direct"
            trafficSource['medium'] = self.retrieve_value(obj, 'cm', 0) or ts.get('cm') or \
                                      ("referral" if self.retrieve_value(obj, 'dr', 0) else "none")
        trafficSource['referralPath'] = self.retrieve_value(obj, 'dr', 0)
        trafficSource['keyword'] = self.retrieve_value(obj, 'ck', 0) or ts.get('ck')
        trafficSource['campaign'] = self.retrieve_value(obj, 'cn', 0) or ts.get('cn')
        trafficSource['adContent'] = self.retrieve_value(obj, 'ct', 0) or ts.get('ct')

        try:
            if re.search(socialRe, self.retrieve_value(obj, 'dr', 0)):
                tsSocial['hasSocialSourceReferral'] = 'Yes'
            else:
                tsSocial['hasSocialSourceReferral'] = 'No'
        except TypeError:
            tsSocial['hasSocialSourceReferral'] = 'No'
        trafficSource['social'] = tsSocial.copy()

        return {k: trafficSource.get(k) for k in traffic_source_order}

    def total_func(self, session_obj):
        """
        Get the session total information, equates to the 'totals' record.
        @param session_obj: Session Object
        @return:
        """
        try:
            pageviews = int(session_obj.get('t').value_counts()['pageview']) or 0
        except KeyError:
            pageviews = 0

        try:
            events = int(session_obj.get('t').value_counts()['event']) or 0
        except KeyError:
            events = 0

        try:
            ni_hits = int(session_obj.get('ni').value_counts()['1']) or 0
        except KeyError:
            ni_hits = 0
        total = {'hits': pageviews + events,
                 'pageViews': pageviews}

        lastHit = self.get_hit_time(session_obj, -1)
        firstHit = self.get_hit_time(session_obj, 0)
        try:
            total['timeOnSite'] = int(timedelta.total_seconds(lastHit - firstHit))
        except KeyError:
            total['timeOnSite'] = None

        try:
            if int(session_obj['pa'].value_counts()['purchase']) > 0:
                total['transactions'] = int(session_obj['pa'].value_counts()['purchase'])
                total['totalTransactionRevenue'] = int(sum(session_obj['tr'].value_counts()) * (10 ** 6))
        except KeyError:
            total['transactions'] = None
            total['totalTransactionRevenue'] = None

        if total['hits'] - ni_hits <= 1:
            total['bounces'] = 1
        else:
            total['bounces'] = None

        return {k: total[k] for k in totals_order}

    def get_full_visitor_id(self, client_id, property_id):
        """
        Fetch the Full Visitor Id from Google Analytics. The exact hash isn't known, so this is best way to do this.
        @param client_id: Client Id
        @param property_id: Property Id
        @return: API Response
        """
        body = {'kind': 'analytics#hashClientIdRequest', 'clientId': client_id, 'webPropertyId': property_id}
        credentials = service_account.Credentials.from_service_account_file(self.service_account,
                                                                            scopes=[
                                                                                'https://www.googleapis.com/auth/analytics.edit'
                                                                            ]
                                                                            )
        api = build('analytics', 'v3', credentials=credentials)
        try:
            request = api.management().clientId().hashClientId(body=body)
            response = request.execute()
            return response
        except HttpError as ex:
            self.logger.error('{} Error: {}'.format(ex.resp.status,
                                                    json.loads(ex.content)['error']['errors'][0]['message']))
            return {"hashedClientId": ""}

    def session_func(self, obj):
        """
        Function that manages the different processes for each session, converting the hits into a single BQ row.
        @param obj: Session object
        @return:
        """
        session = {}
        # Session time values
        first_hit = self.get_hit_time(obj, 0)
        first_hit_posix = first_hit.strftime('%s')
        # Set Session values
        clientId = str(obj['cid'].iloc[0])
        propId = obj['tid'].iloc[0]
        hits = []
        fvid = self.get_full_visitor_id(clientId, propId)
        session['clientId'] = clientId
        session['fullVisitorId'] = fvid['hashedClientId']
        session['visitId'] = self.retrieve_value(obj, 'cd5', 0)
        session['visitStartTime'] = first_hit_posix
        session['date'] = first_hit.strftime('%Y-%m-%d')
        # Totals
        session['totals'] = self.total_func(obj)
        # Traffic Source
        session['trafficSource'] = self.traffic_func(obj)
        # Device Information
        session['device'] = self.device_func(obj)
        # Hit Level information
        cds = []
        cms = []
        for y in range(0, len(obj)):
            # Initiate Dicts and Lists
            hit = self.process_hit(obj, y)
            hits.append(hit.copy())
            cds += self.custom_definition(obj, 'cd', 20, y, 'dimension', ['S', 'U'])
            cms += self.custom_definition(obj, 'cm', 20, y, 'metric', ['S', 'U'])
        cds = self.collapse_session_cdm(cds)
        cms = self.collapse_session_cdm(cms)
        session['customDimensions'] = cds
        session['customMetrics'] = cms
        session['geoNetwork'] = geo_network
        h = hits[0]
        try:
            if h.get('isExit') == "true" and h.get('isEntrance') == "true":
                session['totals']['bounces'] = 1
        except KeyError:
            session['totals']['bounces'] = None
        session['hits'] = hits
        return {k: session.get(k) for k in session_order}

    def write_to_file(self, obj):
        """
        Write the session array to a jsonlines file
        @param obj: Formatted array of sessions
        @return: filename
        """
        source_file_name = 'output' + self.args['date'] + '.jsonl'
        with jsonlines.open(source_file_name, mode='w') as writer:
            writer.write_all(obj)
        return source_file_name

    def upload_to_bq(self, file):
        """
        Upload the sessions to BigQuery using the jsonl file.
        @param file: File Name
        @return: None
        """
        with open(file, 'rb') as source_file:
            job = self.bq_client.load_table_from_file(
                file_obj=source_file,
                destination='{}.{}.{}'.format(self.bigquery['project'],
                                              self.bigquery['dataset'],
                                              self.bigquery['table']),
                project=self.bigquery['project'],
                job_config=job_config,
                location='EU'
            )
        job.result()

    def upload_to_gs(self, file):
        """
        Save the jsonl file to GCS in case it's needed to reload the data in the future.
        @param file: Sessions jsonl file
        @return: None
        """
        bucket = self.gs_client.bucket(self.storage['bucket'])
        bucket.exists()
        blob = bucket.blob(file)

        with open(file, 'rb') as source_file:
            blob.upload_from_file(source_file)
            source_file.close()

    def get_data(self):
        self.logger.info("Date: {}".format(self.args['date']))
        df = self.query_data()
        return df

    @staticmethod
    def prepare_data(df):
        """
        Group hits into sessions and return the sessions and the session ids.
        @param df: The dataframe of all hits
        @return: Sessions and Session Ids
        """
        # Group hits into sessions by CD5
        dfs = dict(tuple(df.groupby('cd5')))
        sids = df.cd5.drop_duplicates()
        return dfs, sids

    def process_data(self, dfs, sids):
        """
        Create an array of sessions, with each session taking a single row
        @param dfs: The dataframe of sessions
        @param sids: The session ids
        @return:
        """
        array = []
        # Fetch the Array
        for x in range(0, len(sids)):
            # Clear Session Level Values, Dicts and Lists
            key = sids.iloc[x]
            obj = dfs[key]
            user_agent = self.retrieve_value(obj, 'cd30', 0)
            if user_agent:
                ua = ua_parse(user_agent)
                if ua.is_bot:
                    continue
            try:
                session = self.session_func(obj)
            except Exception as ex:
                self.logger.critical('There was an Execption: {}'.format(ex))
                raise Exception(ex)
            # Add session to list
            array.append(session.copy())
        return array

    def upload_to_cloud(self, array):
        """
        Write the sessions to a jsonl file and upload that to BigQuery
        @param array: The array of sessions
        @return: None
        """
        file = self.write_to_file(array)
        self.upload_to_bq(file)
        self.logger.info("Date: {} Completed".format(self.args['date']))

    def execute(self):
        """
        Execute the ETL pipeline
        """

        try:
            self.pre_execution_checks()
            self.pipeline()
        except Exception as ex:
            self.logger.critical('Pipeline Failure! {}'.format(ex))
            raise ex
        finally:
            self.post_execution()
