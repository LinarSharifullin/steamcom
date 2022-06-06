from steamcom.login import LoginExecutor
from steamcom.confirmations import ConfirmationExecutor
from steamcom.utils import login_required
from steamcom.models import SteamUrl


class SteamClient:

    def __init__(self) -> None:
        self.username = ''
        self.password = ''
        self.shared_secret = ''
        self.identity_secret = ''
        self.session = None # will be added after login
        self.steam_id = '' # will be added after login
        self.confirmations = None # will be added after login
        self._was_login_executed = False
    
    def __str__(self) -> str:
        if self._was_login_executed == True:
            return f'SteamClient: {self.username}'
        else:
            return 'Empty SteamClient object'
    
    def __repr__(self) -> str:
        if self._was_login_executed == True:
            return f'SteamClient: {self.username}'
        else:
            return 'Empty SteamClient object'

    def login(self, username: str, password: str, shared_secret: str,
            identity_secret: str) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.identity_secret = identity_secret
        login_executor = LoginExecutor(username, password, shared_secret)
        self.session, self.steam_id = login_executor.login()
        self.confirmations = ConfirmationExecutor(identity_secret, 
            self.steam_id, self.session)
        self._change_login_executed_fields(True)

    @login_required
    def extract_session(self) -> dict:
        cookies = self.session.cookies.get_dict()
        extracted_session = {
            'steam_id': self.steam_id,
            'sessionid': cookies['sessionid'],
            'steamLogin': cookies['steamLogin'],
            'steamLoginSecure': cookies['steamLoginSecure']
        }
        return extracted_session

    @login_required
    def is_session_alive(self) -> bool:
        steam_login = self.username
        main_page_response = self.session.get(SteamUrl.COMMUNITY_URL)
        return steam_login.lower() in main_page_response.text.lower()

    def _change_login_executed_fields(self, status: bool) -> None:
        self._was_login_executed = status
        self.confirmations._was_login_executed = status