import logging
import requests
from time import gmtime, strftime
from urllib import parse
import configparser

logger = logging.getLogger(__name__)

config_parser = configparser.ConfigParser()
# config_parser.read('etsy.conf')
config_parser.read('./private/etsy.conf')


class EtsyApi(object):

    def __init__(self, api_key_version):
        self.api_key = config_parser.get('API', api_key_version)
        self.api_en_point = config_parser.get('API', 'end_point')
        self.get_seller_taxonomy_method = config_parser.get('API_METHODS', 'getSellerTaxonomy')
        self.request_code = 0

    def get_request_code(self):
        return self.request_code

    @staticmethod
    def get_date_now():
        return strftime("%Y-%m-%d", gmtime())

    @staticmethod
    def get_date_time_now():
        return strftime("%Y-%m-%d %H:%M:%S", gmtime())

    def request_url(self, method, params=None):
        url = '{endpoint}{method}?api_key={api_key}{params}'.format(
            endpoint=self.api_en_point,
            method=method,
            api_key=self.api_key,
            params='&{}'.format(parse.urlencode(params) if params else ''),
        )
        return url

    def get(self, method, params=None, timeout=5, root=False):
        url = self.request_url(method, params)
        response = requests.get(url, timeout=timeout)
        self.request_code = response.status_code

        if response.status_code != 200:
            logger.warning('Response is not 200! reason: {}, because: {}'.format(
                response.status_code, response.text
            ))
            return False

        data = response.json()
        if root:
            return data
        return data and data['results'][0] if data['count'] == 1 else data['results']

    def get_seller_taxonomy(self):
        return self.get(self.get_seller_taxonomy_method)

    def get_listing(self, listing_id):
        return self.get(
            'listings/{}'.format(listing_id),
            {'includes': 'MainImage,Shop'},
        )

    def get_shop(self, shop_id):
        return self.get(
            'shops/{}'.format(shop_id),
            {'includes': 'About'},
        )

    def user_profile(self, user_id):
        return self.get(
            'users/{}/profile'.format(user_id)
        )

    def get_shop_listings(self, shop_id, page=1):
        return self.get(
            'shops/{}/listings/active'.format(shop_id),
            {'page': page}, root=True
        )