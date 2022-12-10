import time

from steamcom.client import SteamClient
from steamcom.models import ConfirmationType
from steamcom.exceptions import ApiException
from steamcom import fee_counter


USERNAME = ''
PASSWORD = ''
SHARED_SECRET = ''
IDENTITY_SECRET = ''
APP_ID = '730'
CONTEXT_ID = '2'
SELL_ITEMS = {
    'Snakebite Case': {'price': 0.5, 'value': 200},
    'Chroma 3 Case': {'price': 8, 'value': 200}
}
CONFIRM_VALUE = 100
DELAY = 1


steam_client = SteamClient(USERNAME, PASSWORD, SHARED_SECRET, IDENTITY_SECRET)
steam_client.login()
inventory = steam_client.get_my_inventory(APP_ID, CONTEXT_ID)['assets']

can_sell = dict()
for asset, asset_data in inventory.items():
    if asset_data['marketable']:
            can_sell[asset] = asset_data

CONFIRM_COUNTER = 0
for asset_id, asset_data in can_sell.items():
    market_hash_name = asset_data['market_hash_name']
    if market_hash_name in SELL_ITEMS\
            and SELL_ITEMS[market_hash_name]['value'] > 0:
        price = SELL_ITEMS[market_hash_name]['price']
        seller_receive = fee_counter.count(price)['seller_receive']
        try:
            steam_client.market.create_sell_order(
                asset_id, APP_ID, CONTEXT_ID, seller_receive)
            SELL_ITEMS[market_hash_name]['value'] -= 1
            CONFIRM_COUNTER += 1
            print(f'{market_hash_name} listed')
        except ApiException as e:
            print(f'ApiException for listing {market_hash_name}: {e}')
        if CONFIRM_COUNTER >= 100:
            steam_client.confirmations.allow_all_confirmations([ConfirmationType.CREATE_LISTING])
            CONFIRM_COUNTER = 0
            print('Listings confirmed')
        time.sleep(DELAY)
steam_client.confirmations.allow_all_confirmations([ConfirmationType.CREATE_LISTING])
print('Listings confirmed')
