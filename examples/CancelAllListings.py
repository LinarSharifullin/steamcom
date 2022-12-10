import time

from steamcom.client import SteamClient
from steamcom.exceptions import ApiException


USERNAME = ''
PASSWORD = ''
SHARED_SECRET = ''
IDENTITY_SECRET = ''
DELAY = 1


steam_client = SteamClient(USERNAME, PASSWORD, SHARED_SECRET, IDENTITY_SECRET)
steam_client.login()
listings = steam_client.market.get_my_market_listings()

for listing in listings['sell_listings']:
    try:
        steam_client.market.cancel_sell_order(listing)
        print(f'{listing} canceled')
    except ApiException as e:
        print(f'ApiException when canceled {listing}: {e}')
    time.sleep(DELAY)