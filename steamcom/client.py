from steamcom.login import LoginExecutor
from steamcom.confirmations import ConfirmationExecutor


class SteamClient:

    def __init__(self) -> None:
        self.username = ''
        self.password = ''
        self.shared_secret = ''
        self.identity_secret = ''
        self.session = None # will be added after login
        self.steam_id = '' # will be added after login
        self.confirmations = None # will be added after login
        self.was_login_executed = False
    
    def __str__(self) -> str:
        if self.was_login_executed == True:
            return f'Account: {self.username}'
        else:
            return 'Empty SteamClient object'
    
    def __repr__(self) -> str:
        if self.was_login_executed == True:
            return f'Account: {self.username}'
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
        self.was_login_executed = True
