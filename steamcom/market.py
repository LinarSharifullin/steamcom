import requests


class SteamMarket:

    def __init__(self, steam_id: str = '',
                 session: requests.Session = requests.Session()) -> None:
        self.steam_id = steam_id
        self.session = session
        self.was_login_executed = False
