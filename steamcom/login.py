import base64
import json
import rsa
import time
from binascii import hexlify
from Cryptodome.Hash import SHA1
from os import urandom

import requests

from steamcom.exceptions import LoginFailed
from steamcom.guard import generate_one_time_code
from steamcom.models import SteamUrl
from steamcom.utils import api_request


class LoginExecutor:

    def __init__(self, username: str, password: str,
                 shared_secret: str, session: requests.Session) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.steam_id = ''  # will be added after login requests
        self.session = session

    def login(self) -> str:
        login_response = self._send_login_requests()
        self._check_for_captcha(login_response)
        self._assert_valid_credentials(login_response)
        self.steam_id = login_response['transfer_parameters']['steamid']
        return self.steam_id

    def _send_login_requests(self) -> dict:
        self._set_mobile_cookies()
        rsa_key, rsa_timestamp = self._fetch_rsa_params()
        encrypted_password = self._encrypt_password(rsa_key)
        request_data = self._prepare_login_request_data(
            encrypted_password, rsa_timestamp)
        url = SteamUrl.COMMUNITY + '/login/dologin'
        response = api_request(self.session, url, data=request_data)
        self._delete_mobile_cookies()
        return response

    def _fetch_rsa_params(self) -> dict:
        service = 'IAuthenticationService'
        endpoint = 'GetPasswordRSAPublicKey'
        version = 'v1'
        url = f'{SteamUrl.API}/{service}/{endpoint}/{version}'
        # all requests from the login page use the same "Referer" and "Origin"
        headers = {
            "Referer": SteamUrl.COMMUNITY + '/',
            "Origin": SteamUrl.COMMUNITY
        }
        params = {'account_name': self.username}
        key_response = api_request(self.session, url, params, headers)
        rsa_mod = int(key_response['response']['publickey_mod'], 16)
        rsa_exp = int(key_response['response']['publickey_exp'], 16)
        rsa_timestamp = key_response['response']['timestamp']
        return rsa.PublicKey(rsa_mod, rsa_exp), rsa_timestamp

    def _encrypt_password(self, rsa_key: rsa.key.PublicKey)\
            -> bytes:
        encoded_password = self.password.encode('utf-8')
        encrypted_rsa = rsa.encrypt(encoded_password, rsa_key)
        return base64.b64encode(encrypted_rsa)

    def _prepare_login_request_data(
            self, encrypted_password: bytes, rsa_timestamp: str)\
            -> dict[str, str]:
        login_request_data = {
            'password': encrypted_password,
            'username': self.username,
            'twofactorcode': generate_one_time_code(self.shared_secret),
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'rsatimestamp': rsa_timestamp,
            'remember_login': 'true',
            'donotcache': str(int(time.time() * 1000)),
            "oauth_client_id": "DE45CD61",
            "oauth_scope": "read_profile write_profile read_client'\
                            + 'write_client",
        }
        return login_request_data

    def _set_mobile_cookies(self) -> None:
        self.session.cookies.set('mobileClientVersion', '0 (2.1.3)')
        self.session.cookies.set('mobileClient', 'android')

    def _delete_mobile_cookies(self) -> None:
        self.session.cookies.pop('mobileClientVersion', None)
        self.session.cookies.pop('mobileClient', None)

    @staticmethod
    def _check_for_captcha(login_response: dict) -> None:
        if login_response.get('captcha_needed', False):
            raise LoginFailed('Captcha required')

    @staticmethod
    def _assert_valid_credentials(login_response: dict) -> None:
        if not login_response['success']:
            message = login_response['message']
            raise LoginFailed(f'{message}')

    def _set_cookies(self, wg_token: str, wg_token_secure: str) -> None:
        session_id = self._generate_session_id()
        set_cookie = self.session.cookies.set
        steam_login = self.steam_id + "%7C%7C" + wg_token
        steam_login_secure = self.steam_id + "%7C%7C" + wg_token_secure
        for domain in (SteamUrl.COMMUNITY[8:], SteamUrl.STORE[8:]):
            set_cookie('sessionid', session_id, domain=domain)
            set_cookie('steamLogin',  steam_login, domain=domain)
            set_cookie('steamLoginSecure', steam_login_secure, domain=domain,
                       secure=True)

    @staticmethod
    def _generate_session_id() -> str:
        sha1_hash = SHA1.new(urandom(32)).digest()
        return hexlify(sha1_hash)[:32].decode('ascii')
