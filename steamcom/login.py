import rsa
import base64
import time

import requests

from steamcom.models import SteamUrl
from guard import generate_one_time_code



class LoginExecutor:

    def __init__(self, username: str, password: str, shared_secret: str,
            session: requests.Session) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.session = session

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
