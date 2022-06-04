class SteamClient:
    def __init__(self, username: str, password: str, shared_secret: str, identity_secret: str) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.identity_secret = identity_secret
        self.session = None # will be added after login
        self.steam_id = '' # will be added after login
        self.confirmations = None # will be added after login
        self.was_login_executed = False
