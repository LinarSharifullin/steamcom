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
        self._was_login_executed = True
        self.confirmations._was_login_executed = True

    @login_required
    def is_session_alive(self):
        steam_login = self.username
        main_page_response = self.session.get(SteamUrl.COMMUNITY_URL)
        return steam_login.lower() in main_page_response.text.lower()
