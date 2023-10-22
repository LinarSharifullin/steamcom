import re
import time
import json
from typing import Mapping
import urllib.parse as urlparse

import requests
from bs4 import BeautifulSoup

from steamcom.login import LoginExecutor
from steamcom.confirmations import ConfirmationExecutor
from steamcom.utils import (login_required, parse_price, api_request,
                            merge_items_with_descriptions_from_inventory,
                            get_key_value_from_url, account_id_to_steam_id,
                            create_offer_dict)
from steamcom.models import SteamUrl
from steamcom.exceptions import LoginFailed, SessionIsInvalid, ApiException
from steamcom.market import SteamMarket


class SteamClient:

    def __init__(self, username: str = '', password: str = '',
                 shared_secret: str = '', identity_secret: str = '',
                 session: requests.Session = requests.Session()) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.identity_secret = identity_secret
        self.session = session
        self.steam_id = ''  # will be added after login
        self.currency_id = None  # will be added after login
        self.was_login_executed = False
        self.confirmations = None
        self.market = None

    def __str__(self) -> str:
        if self.was_login_executed:
            return f'SteamClient: {self.username}'
        else:
            return 'Empty SteamClient object'

    def __repr__(self) -> str:
        if self.was_login_executed:
            return f'SteamClient: {self.username}'
        else:
            return 'Empty SteamClient object'

    def login(self) -> None:
        if self.was_login_executed:
            raise LoginFailed('You alrady have a session')
        login_executor = LoginExecutor(
            self.username, self.password, self.shared_secret, self.session)
        self.steam_id = login_executor.login()
        self.currency_id = self.get_my_currency_id()
        self._change_login_executed_fields(True)

    @login_required
    def extract_session(self) -> dict:
        cookies = self.session.cookies.get_dict()
        extracted_session = {
            'steamid': self.steam_id,
            'currencyid': self.currency_id
        }
        extracted_session.update(cookies)
        return extracted_session

    def load_session(self, extracted_session: Mapping[str, str]) -> None:
        if self.was_login_executed:
            raise LoginFailed('You alrady have a session')
        self._load_session(extracted_session)
        self._change_login_executed_fields(True)
        status = self.is_session_alive()
        if status is False:
            self._change_login_executed_fields(False)
            raise SessionIsInvalid()

    @login_required
    def is_session_alive(self) -> bool:
        steam_login = self.username
        main_page_response = self.session.get(SteamUrl.COMMUNITY)
        return steam_login.lower() in main_page_response.text.lower()

    def _load_session(self, extracted_session: Mapping[str, str]) -> None:
        community_url = SteamUrl.COMMUNITY[8:]
        store_url = SteamUrl.STORE[8:]
        set_cookie = self.session.cookies.set
        for key, value in extracted_session.items():
            unformatted_key = key.lower().replace('_', '')
            if unformatted_key == 'steamid':
                self.steam_id = value
            elif unformatted_key == 'currencyid':
                self.currency_id = value
            else:
                set_cookie(key, value, domain=community_url)
                set_cookie(key, value, domain=store_url)

    def _change_login_executed_fields(self, status: bool) -> None:
        if status:
            self.confirmations = ConfirmationExecutor(
                self.identity_secret, self.steam_id, self.session)
            self.confirmations.was_login_executed = True
            self.market = SteamMarket(self.steam_id, self.currency_id,
                                      self.session)
            self.market.was_login_executed = True
        else:
            self.confirmations = None
            self.market = None
        self.was_login_executed = status

    def get_my_currency_id(self) -> int:
        response = self.session.get(SteamUrl.COMMUNITY + '/market/')
        part_with_currency = re.search('wallet_currency":\\d+', response.text)
        return int(re.search('\\d+', part_with_currency[0])[0])

    @login_required
    def get_my_inventory(self, app_id: str, context_id: str,
                         delay: int = 3, attempts: int = 3) -> dict:
        steam_id = self.steam_id
        return self.get_partner_inventory(steam_id, app_id, context_id, delay,
                                          attempts)

    def get_partner_inventory(self, partner_steam_id: str, app_id: str,
                              context_id: str, delay: int = 3,
                              attempts: int = 3) -> dict:
        start_asset_id = None
        full_inventory = {}
        while True:
            if attempts > 0:
                try:
                    time.sleep(delay)
                    inventory = self.get_inventory_page(
                        partner_steam_id, app_id, context_id,
                        start_asset_id=start_asset_id)
                except ApiException:
                    attempts -= 1
                    continue
            else:
                time.sleep(delay)
                inventory = self.get_inventory_page(
                    partner_steam_id, app_id, context_id,
                    start_asset_id=start_asset_id)
            if not full_inventory:
                full_inventory['assets'] = inventory['assets']
                full_inventory['total_inventory_count']\
                    = inventory['total_inventory_count']
            else:
                full_inventory['assets']\
                    = full_inventory['assets'] | inventory['assets']
            if inventory['last_asset_id']:
                start_asset_id = inventory['last_asset_id']
            else:
                return full_inventory

    def get_inventory_page(self, partner_steam_id: str, app_id: str,
                           context_id: str, count: int = 5000,
                           start_asset_id: str = None) -> dict:
        url = '/'.join([SteamUrl.COMMUNITY, 'inventory', partner_steam_id,
                        app_id, context_id])
        params = {'l': 'english',
                  'count': count,
                  'start_assetid': start_asset_id}
        response_dict = api_request(self.session, url, params)
        if 'success' not in response_dict or response_dict['success'] != 1:
            raise ApiException('Success value should be 1.')
        assets = merge_items_with_descriptions_from_inventory(
            response_dict, context_id)
        more_items = response_dict['more_items']\
            if 'more_items' in response_dict else None
        last_asset_id = response_dict['last_assetid']\
            if 'last_assetid' in response_dict else None
        inventory = {
            'assets': assets,
            'more_items': more_items,
            'last_asset_id': last_asset_id,
            'total_inventory_count': response_dict['total_inventory_count']
        }
        return inventory

    @login_required
    def get_wallet_balance(self) -> float:
        main_page_response = self.session.get(SteamUrl.COMMUNITY)
        response_soup = BeautifulSoup(main_page_response.text, 'html.parser')
        balance_url = href=SteamUrl.STORE + '/account/store_transactions/'
        balance = response_soup.find(href=balance_url)
        return parse_price(balance.text)

    @login_required
    def send_offer_with_url(self, my_assets: dict, them_assets: dict,
                            trade_offer_url: str, message: str = '') -> dict:
        token = get_key_value_from_url(trade_offer_url, 'token')
        partner_account_id = get_key_value_from_url(trade_offer_url, 'partner')
        partner_steam_id = account_id_to_steam_id(partner_account_id)
        offer = create_offer_dict(my_assets, them_assets)
        session_id = self.session.cookies.get_dict()['sessionid']
        url = SteamUrl.COMMUNITY + '/tradeoffer/new/send'
        server_id = 1
        trade_offer_create_params = {'trade_offer_access_token': token}
        params = {
            'sessionid': session_id,
            'serverid': server_id,
            'partner': partner_steam_id,
            'tradeoffermessage': message,
            'json_tradeoffer': json.dumps(offer),
            'captcha': '',
            'trade_offer_create_params': json.dumps(trade_offer_create_params)
        }
        headers = {'Referer': SteamUrl.COMMUNITY\
                        + urlparse.urlparse(trade_offer_url).path,
                   'Origin': SteamUrl.COMMUNITY}
        return api_request(self.session, url, headers=headers, data=params)
