import requests

from steamcom.utils import login_required
from steamcom.models import SteamUrl


class SteamMarket:

    def __init__(self, steam_id: str = '',
                 session: requests.Session = requests.Session()) -> None:
        self.steam_id = steam_id
        self.session = session
        self.was_login_executed = False

    @login_required
    def get_price_history(self, app_id: str, market_hash_name: str) -> dict:
        url = SteamUrl.COMMUNITY + '/market/pricehistory/'
        params = {'country': 'PL',
                  'appid': app_id,
                  'market_hash_name': market_hash_name}
        response = self.session.get(url, params=params)
        return response.json()
