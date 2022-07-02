from typing import Mapping

import requests

from steamcom.login import LoginExecutor
from steamcom.confirmations import ConfirmationExecutor
from steamcom.utils import login_required
from steamcom.models import SteamUrl
from steamcom.exceptions import LoginFailed, SessionIsInvalid


class SteamClient:

    def __init__(self, username: str = '', password: str = '',
                 shared_secret: str = '', identity_secret: str = '') -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.identity_secret = identity_secret
        self.session = requests.Session()
        self.steam_id = ''  # will be added after login
        self.was_login_executed = False

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
            self.username, self.password, self.shared_secret)
        self.session, self.steam_id = login_executor.login()
        self._change_login_executed_fields(True)

    @login_required
    def extract_session(self) -> dict[str, str]:
        cookies = self.session.cookies.get_dict()
        extracted_session = {
            'steamid': self.steam_id,
            'sessionid': cookies['sessionid'],
            'steamLogin': cookies['steamLogin'],
            'steamLoginSecure': cookies['steamLoginSecure']
        }
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
            elif unformatted_key == 'sessionid':
                set_cookie('sessionid', value, domain=community_url)
                set_cookie('sessionid', value, domain=store_url)
            elif unformatted_key == 'steamlogin':
                set_cookie('steamLogin', value, domain=community_url)
                set_cookie('steamLogin', value, domain=store_url)
            elif unformatted_key == 'steamloginsecure':
                set_cookie('steamLoginSecure', value, domain=community_url)
                set_cookie('steamLoginSecure', value, domain=store_url)

    def _change_login_executed_fields(self, status: bool) -> None:
        if status:
            self.confirmations = ConfirmationExecutor(
                self.identity_secret, self.steam_id, self.session)
            self.confirmations.was_login_executed = True
        else:
            self.confirmations = None
        self.was_login_executed = status
