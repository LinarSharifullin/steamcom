import requests
import json
import time
import urllib.parse
from decimal import Decimal

from steamcom.utils import (login_required, text_between,
                            get_listing_id_to_assets_address_from_html,
                            get_market_listings_from_html,
                            merge_items_with_descriptions_from_listing,
                            get_market_sell_listings_from_api)
from steamcom.models import SteamUrl, Result
from steamcom.exceptions import ApiException


class SteamMarket:

    def __init__(self, steam_id: str = '', currency_id: int = None,
                 session: requests.Session = requests.Session()) -> None:
        self.steam_id = steam_id
        self.currency_id = currency_id
        self.session = session
        self.was_login_executed = False

    @login_required
    def get_price_history(self, app_id: str, market_hash_name: str) -> dict:
        url = SteamUrl.COMMUNITY + '/market/pricehistory/'
        params = {'appid': app_id,
                  'market_hash_name': market_hash_name}
        response = self.session.get(url, params=params).json()
        if not response.get("success"):
            text = 'Problem getting price history the order. success: '
            raise ApiException(text + str(response.get("success")))
        return self._parse_graph(response['prices'])

    def _parse_graph(self, graph):
        parsed_graph = {}
        for dot in reversed(graph):
            date = dot[0][:11]
            time = dot[0][12:14]
            price = dot[1]
            value = int(dot[2])
            if date not in parsed_graph:
                parsed_graph[date] = {'dots': {}}
            parsed_graph[date]['dots'][time] = {'price': price,
                                                'sales': value}
        return parsed_graph

    def get_orders_histogram(self, item_name_id: str) -> dict:
        url = SteamUrl.COMMUNITY + '/market/itemordershistogram/'
        params = {
            'currency': self.currency_id,
            'language': 'en',
            'item_nameid': item_name_id
        }
        response = self.session.get(url, params=params)
        return self._parse_orders_histogram(response.json())

    def _parse_orders_histogram(self, histogram: dict) -> dict:
        orders = []
        listings = []
        previous_value = 0
        for order in histogram['buy_order_graph']:
            price = order[0]
            value = order[1] - previous_value
            previous_value = order[1]
            orders.append({'price': price, 'value': value})
        previous_value = 0
        for listing in histogram['sell_order_graph']:
            price = listing[0]
            value = listing[1] - previous_value
            previous_value = listing[1]
            listings.append({'price': price, 'value': value})
        parsed_histogram = {
            'buy_order_graph': orders,
            'sell_order_graph': listings
        }
        return parsed_histogram

    @login_required
    def get_my_market_listings(self, delay: int = 3) -> dict:
        response = self.session.get(SteamUrl.COMMUNITY + '/market')
        if response.status_code != 200:
            text = 'Problem getting the listings. http code: {}'
            raise ApiException(text.format(response.status_code))
        assets_descriptions = json.loads(
            text_between(response.text, 'var g_rgAssets = ', ';\r\n'))
        listing_id_to_assets_address = \
            get_listing_id_to_assets_address_from_html(response.text)
        listings = get_market_listings_from_html(response.text)
        listings = merge_items_with_descriptions_from_listing(
            listings, listing_id_to_assets_address, assets_descriptions)
        listings_end = '<span id="tabContentsMyActiveMarketListings_end">'
        listings_total = '<span id="tabContentsMyActiveMarketListings_total">'
        if listings_end in response.text:
            n_showing = int(text_between(response.text,
                                         listings_end, '</span>'))
            n_total = int(text_between(
                response.text, listings_total, '</span>').replace(',', ''))
            if n_showing < n_total < 1000:
                listings_2 = self._parse_listings(n_showing, -1)
                listings['sell_listings']\
                    = listings['sell_listings'] | listings_2
            else:
                for i in range(0, n_total, 100):
                    time.sleep(delay)
                    listings_2 = self._parse_listings(n_showing + i, 100)
                    listings['sell_listings']\
                        = listings['sell_listings'] | listings_2
        return listings

    def _parse_listings(self, start: int, count: int) -> dict:
        url = '{}/market/mylistings/render/?query=&start={}&count={}'\
            .format(SteamUrl.COMMUNITY, start, count)
        response = self.session.get(url)
        if response.status_code != 200:
            text = 'Problem getting the listings. http code: {}'
            raise ApiException(text.format(response.status_code))
        jresp = response.json()
        listing_id_to_assets_address =\
            get_listing_id_to_assets_address_from_html(
                jresp.get('hovers'))
        listings_2 = get_market_sell_listings_from_api(
            jresp.get('results_html'))
        listings_2 = merge_items_with_descriptions_from_listing(
            listings_2, listing_id_to_assets_address,
            jresp.get('assets'))
        return listings_2['sell_listings']

    @login_required
    def create_buy_order(self, app_id: str, market_hash_name: str,
                         price_single_item: str, quantity: int) -> dict:
        data = {
            'sessionid': self.session.cookies.get_dict()['sessionid'],
            'currency': self.currency_id,
            'appid': app_id,
            'market_hash_name': market_hash_name,
            'price_total': str(Decimal(price_single_item) * Decimal(quantity)),
            'quantity': quantity
        }
        url_name = urllib.parse.quote(market_hash_name)
        referer = f'{SteamUrl.COMMUNITY}/market/listings/{app_id}/{url_name}'
        headers = {'Referer': referer}
        response = self.session.post(
            SteamUrl.COMMUNITY + "/market/createbuyorder/", data,
            headers=headers).json()
        return response

    @login_required
    def create_sell_order(self, asset_id: str, app_id: str, context_id: str,
                          money_to_receive: str) -> dict:
        data = {
            'assetid': asset_id,
            'sessionid': self.session.cookies.get_dict()['sessionid'],
            'contextid': context_id,
            'appid': app_id,
            'amount': 1,
            'price': money_to_receive
        }
        referer = f'{SteamUrl.COMMUNITY}/profiles/{self.steam_id}/inventory'
        headers = {'Referer': referer}
        response = self.session.post(SteamUrl.COMMUNITY + "/market/sellitem/",
                                     data, headers=headers).json()
        return response

    @login_required
    def cancel_sell_order(self, sell_listing_id: str) -> None:
        url = f'{SteamUrl.COMMUNITY}/market/removelisting/{sell_listing_id}'
        data = {'sessionid': self.session.cookies.get_dict()['sessionid']}
        headers = {'Referer': SteamUrl.COMMUNITY + '/market/'}
        response = self.session.post(url, data=data, headers=headers)
        if not response.ok:
            text = 'Problem removing the listing. http code: '
            raise ApiException(text + response.status_code)

    @login_required
    def cancel_buy_order(self, buy_order_id: str) -> dict:
        data = {
            'sessionid': self.session.cookies.get_dict()['sessionid'],
            'buy_orderid': buy_order_id
        }
        headers = {'Referer': SteamUrl.COMMUNITY + '/market'}
        response = self.session.post(
            SteamUrl.COMMUNITY + '/market/cancelbuyorder/',
            data, headers=headers).json()
        if response.get("success") != Result.OK.value:
            text = 'Problem canceling the order. success: '
            raise ApiException(text + str(response.get("success")))
        return response

    @login_required
    def check_placed_buy_order(self, app_id: str,
                               market_hash_name: str) -> None | dict:
        url = SteamUrl.COMMUNITY + '/market/listings/{}/{}'
        response = self.session.get(url.format(app_id, market_hash_name)).text
        if 'my_market_header_active' not in response:
            raise ApiException('No one is selling this item')
        if 'mbuyorder' in response:
            buy_orders = get_market_listings_from_html(response)['buy_orders']
            first_buy_order = list(buy_orders.keys())[0]
            return buy_orders[first_buy_order]
        else:
            return None

    def get_market_history_page(self, start: int = 0, count: int = 0) -> dict:
        url = SteamUrl.COMMUNITY + '/market/myhistory/render/'
        params = {
            'start': start,
            'count': count,
            'norender': 1
        }
        response = self.session.get(url, params=params).json()
        return response
