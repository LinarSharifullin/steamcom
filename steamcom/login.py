import rsa
import base64

import requests

from steamcom.models import SteamUrl



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