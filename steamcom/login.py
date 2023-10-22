import base64
import rsa

import requests

from steamcom.guard import generate_one_time_code
from steamcom.models import SteamUrl, IAuthenticationServiceEndpoint
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
        self.session.post(SteamUrl.COMMUNITY)  # to get a cookies
        rsa_key, rsa_timestamp = self._fetch_rsa_params()
        encrypted_password = self._encrypt_password(rsa_key)
        client_id, request_id = self._request_auth(encrypted_password,
                                                   rsa_timestamp)
        self._send_steam_guard_code(client_id)
        refresh_token = self._request_refresh_token(client_id, request_id)
        finalize_response = self._finalize_login(refresh_token)
        self._send_transfer_info(finalize_response)
        return self.steam_id

    def _fetch_rsa_params(self) -> tuple[rsa.PublicKey, str]:
        url = IAuthenticationServiceEndpoint.GetPasswordRSAPublicKey
        params = {'account_name': self.username}
        key_response = api_request(self.session, url, params)
        rsa_mod = int(key_response['response']['publickey_mod'], 16)
        rsa_exp = int(key_response['response']['publickey_exp'], 16)
        rsa_timestamp = key_response['response']['timestamp']
        return rsa.PublicKey(rsa_mod, rsa_exp), rsa_timestamp

    def _encrypt_password(self, rsa_key: rsa.PublicKey) -> bytes:
        encoded_password = self.password.encode('utf-8')
        encrypted_rsa = rsa.encrypt(encoded_password, rsa_key)
        return base64.b64encode(encrypted_rsa)

    def _request_auth(self, encrypted_password: bytes, rsa_timestamp: str)\
            -> tuple[str, str]:
        url = IAuthenticationServiceEndpoint.BeginAuthSessionViaCredentials
        request_auth_data = {
            'persistence': '1',
            'encrypted_password': encrypted_password,
            'account_name': self.username,
            'encryption_timestamp': rsa_timestamp
        }
        request_auth_response = api_request(self.session, url,
                                            data=request_auth_data)
        client_id = request_auth_response['response']['client_id']
        self.steam_id = request_auth_response['response']['steamid']
        request_id = request_auth_response['response']['request_id']
        return client_id, request_id

    def _send_steam_guard_code(self, client_id: str) -> None:
        url =\
            IAuthenticationServiceEndpoint.UpdateAuthSessionWithSteamGuardCode
        update_data = {
            'client_id': client_id,
            'steamid': self.steam_id,
            'code_type': 3,
            'code': generate_one_time_code(self.shared_secret)
        }
        api_request(self.session, url, data=update_data)

    def _request_refresh_token(self, client_id: str, request_id: str) -> str:
        url = IAuthenticationServiceEndpoint.PollAuthSessionStatus
        pool_data = {
            'client_id': client_id,
            'request_id': request_id,
        }
        poll_response = api_request(self.session, url, data=pool_data)
        refresh_token = poll_response['response']['refresh_token']
        return refresh_token

    def _finalize_login(self, refresh_token: str) -> dict:
        redir_url = SteamUrl.COMMUNITY + '/login/home/?goto='
        finalize_url = SteamUrl.LOGIN + '/jwt/finalizelogin'
        finalize_data = {
            'nonce': refresh_token,
            'sessionid': self.session.cookies['sessionid'],
            'redir': redir_url
        }
        finalize_response = api_request(self.session, finalize_url,
                                        data=finalize_data)
        return finalize_response

    def _send_transfer_info(self, finalize_response: dict) -> None:
        parameters = finalize_response['transfer_info']
        for pass_data in parameters:
            pass_data['params']['steamID'] = finalize_response['steamID']
            api_request(self.session, pass_data['url'],
                        data=pass_data['params'])
