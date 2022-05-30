import rsa
import base64
import time

import requests

from steamcom.models import SteamUrl
from steamcom.guard import generate_one_time_code
from steamcom.exceptions import CaptchaRequired, InvalidCredentials
from steamcom.utils import generate_session_id



class LoginExecutor:

    def __init__(self, username: str, password: str, shared_secret: str,
            session: requests.Session) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.session = session

    def _send_login_request(self) -> requests.Response:
        rsa_params = self._fetch_rsa_params()
        encrypted_password = self._encrypt_password(rsa_params)
        rsa_timestamp = rsa_params['rsa_timestamp']
        request_data = self._prepare_login_request_data(encrypted_password, 
            rsa_timestamp)
        self._set_mobile_cookies()
        url = SteamUrl.COMMUNITY_URL + '/login/dologin'
        response = self.session.post(url, data=request_data)
        self._delete_mobile_cookies()
        return response

    def _fetch_rsa_params(self) -> dict:
        key_response = self.session.post(SteamUrl.COMMUNITY_URL
            + '/login/getrsakey/', data={'username': self.username}).json()
        rsa_mod = int(key_response['publickey_mod'], 16)
        rsa_exp = int(key_response['publickey_exp'], 16)
        rsa_timestamp = key_response['timestamp']
        return {'rsa_key': rsa.PublicKey(rsa_mod, rsa_exp),
            'rsa_timestamp': rsa_timestamp}

    def _encrypt_password(self, rsa_params: dict) -> str:
        encoded_password = self.password.encode('utf-8')
        encrypted_rsa = rsa.encrypt(encoded_password, rsa_params['rsa_key'])
        return base64.b64encode(encrypted_rsa)
    
    def _prepare_login_request_data(self, encrypted_password: str, 
            rsa_timestamp: str) -> dict:
        return {
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
            "oauth_scope": "read_profile write_profile read_client write_client",
        }
    
    def _set_mobile_cookies(self) -> None:
        self.session.cookies.set('mobileClientVersion', '0 (2.1.3)')
        self.session.cookies.set('mobileClient', 'android')

    def _delete_mobile_cookies(self) -> None:
        self.session.cookies.pop('mobileClientVersion', None)
        self.session.cookies.pop('mobileClient', None)

    @staticmethod
    def _check_for_captcha(login_response: requests.Response) -> None:
        if login_response.json().get('captcha_needed', False):
            raise CaptchaRequired('Captcha required')

    @staticmethod
    def _assert_valid_credentials(login_response: requests.Response) -> None:
        if not login_response.json()['success']:
            raise InvalidCredentials(login_response.json()['message'])

    def _set_sessionid_cookies(self) -> None:
        session_id = generate_session_id()
        community_domain = SteamUrl.COMMUNITY_URL[8:]
        store_domain = SteamUrl.STORE_URL[8:]
        self.session.cookies.set('sessionid', session_id, community_domain)
        self.session.cookies.set('sessionid', session_id, store_domain)

