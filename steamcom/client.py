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

