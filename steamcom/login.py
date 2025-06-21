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
        self.refresh_token =  '' # Will be added during login
        self.session = session

    def login(self) -> tuple[str, str]:
        self.session.get(SteamUrl.COMMUNITY)  # to get a cookies
        rsa_key, rsa_timestamp = self._fetch_rsa_params()
        encrypted_password = self._encrypt_password(rsa_key)
        client_id, request_id = self._request_auth(encrypted_password,
                                                   rsa_timestamp)
        self._send_steam_guard_code(client_id)
        self._request_refresh_token(client_id, request_id)
        finalize_response = self._finalize_login()
        self._send_transfer_info(finalize_response)
        self._set_sessionid_cookies()
        return self.steam_id, self.refresh_token

    def _fetch_rsa_params(self) -> tuple[rsa.PublicKey, str]:
        url = IAuthenticationServiceEndpoint.GetPasswordRSAPublicKey
        headers = {'Referer': f'{SteamUrl.COMMUNITY}/', 'Origin': SteamUrl.COMMUNITY}
        params = {'account_name': self.username}
        key_response = api_request(self.session, url, params, headers)
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
        headers = {'Referer': f'{SteamUrl.COMMUNITY}/', 'Origin': SteamUrl.COMMUNITY}
        request_auth_response = api_request(self.session, url, headers = headers,
                                            data=request_auth_data)
        client_id = request_auth_response['response']['client_id']
        self.steam_id = request_auth_response['response']['steamid']
        request_id = request_auth_response['response']['request_id']
        return client_id, request_id

    def _send_steam_guard_code(self, client_id: str) -> None:
        url =\
            IAuthenticationServiceEndpoint.UpdateAuthSessionWithSteamGuardCode
        headers = {'Referer': f'{SteamUrl.COMMUNITY}/', 'Origin': SteamUrl.COMMUNITY}
        if self.shared_secret:
            code_2fa = generate_one_time_code(self.shared_secret)
        else:
            code_2fa = input('Input 2fa code: ')
        update_data = {
            'client_id': client_id,
            'steamid': self.steam_id,
            'code_type': 3,
            'code': code_2fa
        }
        api_request(self.session, url, headers=headers, data=update_data)

    def _request_refresh_token(self, client_id: str, request_id: str) -> None:
        url = IAuthenticationServiceEndpoint.PollAuthSessionStatus
        headers = {'Referer': f'{SteamUrl.COMMUNITY}/', 'Origin': SteamUrl.COMMUNITY}
        pool_data = {
            'client_id': client_id,
            'request_id': request_id,
        }
        poll_response = api_request(self.session, url, headers=headers, data=pool_data)
        self.refresh_token = poll_response['response']['refresh_token']

    def _finalize_login(self) -> dict:
        redir_url = SteamUrl.COMMUNITY + '/login/home/?goto='
        finalize_url = SteamUrl.LOGIN + '/jwt/finalizelogin'
        finalize_data = {
            'nonce': (None, self.refresh_token),
            'sessionid': (None, self.session.cookies['sessionid']),
            'redir': (None, redir_url)
        }
        headers = {
            'Referer': redir_url,
            'Origin': SteamUrl.COMMUNITY
        }
        finalize_response = self.session.post(
            finalize_url, headers=headers,files=finalize_data).json()
        return finalize_response

    def _send_transfer_info(self, finalize_response: dict) -> None:
        parameters = finalize_response['transfer_info']
        for pass_data in parameters:
            pass_data['params'].update({'steamID': finalize_response['steamID']})
            multipart_fields = {
                key: (None, str(value))
                for key, value in pass_data['params'].items()
            }
            self.session.post(pass_data['url'], files=multipart_fields)

    def _set_sessionid_cookies(self) -> None:
        community_domain = SteamUrl.COMMUNITY[8:]
        store_domain = SteamUrl.STORE[8:]
        community_cookie_dic = self.session.cookies.get_dict(domain=community_domain)
        store_cookie_dic = self.session.cookies.get_dict(domain=store_domain)
        for name in ('steamLoginSecure', 'sessionid', 'steamRefresh_steam', 'steamCountry'):
            cookie = self.session.cookies.get_dict()[name]
            if name == "steamLoginSecure":
                store_cookie = self._create_cookie(name, store_cookie_dic[name], store_domain)
            else:
                store_cookie = self._create_cookie(name, cookie, store_domain)

            if name in ["sessionid", "steamLoginSecure"]:
                community_cookie = self._create_cookie(name, community_cookie_dic[name], community_domain)
            else:
                community_cookie = self._create_cookie(name, cookie, community_domain)

            self.session.cookies.set(**community_cookie)
            self.session.cookies.set(**store_cookie)

    def _create_cookie(self, name: str, cookie: str, domain: str) -> dict:
        return {'name': name, 'value': cookie, 'domain': domain}
