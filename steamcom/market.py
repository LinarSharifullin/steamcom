from datetime import datetime
from typing import Union
import requests
import json
import time
import urllib.parse
from decimal import Decimal

from steamcom.utils import (login_required, text_between,
                            get_listing_id_to_assets_address_from_html,
                            get_market_listings_from_html,
                            merge_items_with_descriptions_from_listing,
                            get_market_sell_listings_from_api, parse_history,
                            parse_graph, parse_orders_histogram,
                            api_request)
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
        response_json = api_request(self.session, url, params)
        if not response_json.get("success"):
            text = 'Problem getting price history the order. success: '
            raise ApiException(text + str(response_json.get("success")))
        return parse_graph(response_json['prices'])

    def get_orders_histogram(self, item_name_id: str, app_id: str,
                             market_hash_name: str,
                             currency_id: int = None) -> dict:
        url = SteamUrl.COMMUNITY + '/market/itemordershistogram'
        params = {
            'country': 'RU',
            'language': 'english',
            'currency': self.currency_id if not currency_id else currency_id,
            'item_nameid': item_name_id,
            'two_factor': 0
        }
        url_name = urllib.parse.quote(market_hash_name)
        referer = f'{SteamUrl.COMMUNITY}/market/listings/{app_id}/{url_name}'
        headers = {
            'Referer': referer
        }
        response = api_request(self.session, url, params, headers)
        if 'buy_order_graph' not in response\
                or 'sell_order_graph' not in response:
            raise ApiException('Buy or sell order graph not in body')
        return parse_orders_histogram(response)

    @login_required
    def get_my_market_listings(self, delay: int = 3) -> dict:
        response = self.session.get(SteamUrl.COMMUNITY + '/market')
        if response.status_code != 200:
            text = 'Problem getting the listings. http code: {}'
            raise ApiException(text.format(response.status_code))
        print('Received market page')
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
                print('Received listings')
                listings['sell_listings']\
                    = listings['sell_listings'] | listings_2
            else:
                for i in range(0, n_total, 100):
                    time.sleep(delay)
                    listings_2 = self._parse_listings(n_showing + i, 100)
                    print(f'Received listings {i}/{n_total}')
                    listings['sell_listings']\
                        = listings['sell_listings'] | listings_2
        return listings

    def _parse_listings(self, start: int, count: int) -> dict:
        url = '{}/market/mylistings/render/?query=&start={}&count={}'\
            .format(SteamUrl.COMMUNITY, start, count)
        jresp = api_request(self.session, url)
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
        url = SteamUrl.COMMUNITY + '/market/createbuyorder/'
        response = api_request(self.session, url, headers=headers, data=data)
        if response['success'] == Result.OK.value:
            return response
        else:
            raise ApiException(response)

    @login_required
    def create_sell_order(self, asset_id: str, app_id: str, context_id: str,
                          money_to_receive: str, amount: int = 1) -> dict:
        data = {
            'assetid': asset_id,
            'sessionid': self.session.cookies.get_dict()['sessionid'],
            'contextid': context_id,
            'appid': app_id,
            'amount': amount,
            'price': money_to_receive
        }
        referer = f'{SteamUrl.COMMUNITY}/profiles/{self.steam_id}/inventory'
        headers = {'Referer': referer}
        url = SteamUrl.COMMUNITY + '/market/sellitem/'
        response = api_request(self.session, url, headers=headers, data=data)
        if not response['success']:
            raise ApiException(response['message'])
        return response

    @login_required
    def cancel_sell_order(self, sell_listing_id: str) -> None:
        url = f'{SteamUrl.COMMUNITY}/market/removelisting/{sell_listing_id}'
        data = {'sessionid': self.session.cookies.get_dict()['sessionid']}
        headers = {'Referer': SteamUrl.COMMUNITY + '/market/'}
        response = self.session.post(url, data=data, headers=headers)
        if not response.ok:
            text = 'Problem removing the listing. http code: {}'
            raise ApiException(text.format(response.status_code))

    @login_required
    def cancel_buy_order(self, buy_order_id: str) -> dict:
        data = {
            'sessionid': self.session.cookies.get_dict()['sessionid'],
            'buy_orderid': buy_order_id
        }
        headers = {'Referer': SteamUrl.COMMUNITY + '/market'}
        url = SteamUrl.COMMUNITY + '/market/cancelbuyorder/'
        response = api_request(self.session, url, headers=headers, data=data)
        return response

    @login_required
    def check_placed_buy_order(self, app_id: str,
                               market_hash_name: str) -> Union[None, dict]:
        url = SteamUrl.COMMUNITY + '/market/listings/{}/{}'
        url_name = urllib.parse.quote(market_hash_name)
        response = self.session.get(url.format(app_id, url_name)).text
        if 'market_listing_largeimage' not in response:
            raise ApiException('No one is selling this item')
        if 'mbuyorder' in response:
            buy_orders = get_market_listings_from_html(response)['buy_orders']
            first_buy_order = list(buy_orders.keys())[0]
            return buy_orders[first_buy_order]
        else:
            return None

    def get_my_history(self, events_value: int = 5000, delay: int = 3,
                       attempts: int = 3) -> dict:
        pages = int(events_value/500)
        last_page_value = events_value % 500
        start = 0
        history = []
        while start-pages*500 < 0:
            if attempts > 0:
                try:
                    time.sleep(delay)
                    page = self._get_market_history_page(start)
                    text = 'History page {}/{} received'
                    print(text.format(int(start/500)+1,
                          pages+min(last_page_value, 1)))
                except (TypeError, ApiException) as e:
                    exc_name = type(e). __name__
                    print(f'{exc_name} during receiving the history page')
                    attempts -= 1
                    continue
            else:
                time.sleep(delay)
                page = self._get_market_history_page(start)
                text = 'History page {}/{} received'
                print(text.format(int(start/500)+1,
                      pages+min(last_page_value, 1)))
            start += 500
            for event in page:
                if event not in history:
                    history.append(event)
        else:
            if last_page_value > 0:
                while attempts > 0:
                    try:
                        time.sleep(delay)
                        page = self._get_market_history_page(
                            start, last_page_value)
                        text = 'History page {}/{} received'
                        print(text.format(int(start/500)+1,
                              pages+min(last_page_value, 1)))
                        break
                    except (TypeError, ApiException) as e:
                        exc_name = type(e). __name__
                        print(f'{exc_name} during receiving the history page')
                        attempts -= 1
                        continue
                else:
                    time.sleep(delay)
                    page = self._get_market_history_page(
                            start, last_page_value)
                    text = 'History page {}/{} received'
                    print(text.format(int(start/500)+1,
                          pages+min(last_page_value, 1)))
                for event in page:
                    if event not in history:
                        history.append(event)
        return history

    def get_my_history_up_to_date(self, date: datetime, delay: int = 3,
                                  attempts: int = 3) -> dict:
        history = []
        start = 0
        while True:
            if attempts > 0:
                try:
                    time.sleep(delay)
                    page = self._get_market_history_page(start)
                    print('History page received')
                except (TypeError, ApiException) as e:
                    exc_name = type(e). __name__
                    print(f'{exc_name} during receiving the history page')
                    attempts -= 1
                    continue
            else:
                time.sleep(delay)
                page = self._get_market_history_page(start)
                print('History page received')
            start += 500
            for event in page:
                event_time = datetime.fromtimestamp(event['time_event'])
                if event not in history:
                    if event_time >= date:
                        history.append(event)
                    else:
                        return history
        return history

    def _get_market_history_page(self, start: int = 0,
                                 count: int = 500) -> dict:
        url = SteamUrl.COMMUNITY + '/market/myhistory/render/'
        params = {
            'start': start,
            'count': count,
            'norender': 1
        }
        response = api_request(self.session, url, params)
        if not response['total_count']:
            raise ApiException('An empty response returned')
        return parse_history(response)
