from steamcom.client import SteamClient
from steamcom.models import ConfirmationType


USERNAME = ''
PASSWORD = ''
SHARED_SECRET = ''
IDENTITY_SECRET = ''
APP_ID = ''
CONTEXT_ID = ''
TRADE_OFFER = ''


steam_client = SteamClient(USERNAME, PASSWORD, SHARED_SECRET, IDENTITY_SECRET)
steam_client.login()
inventory = steam_client.get_my_inventory(APP_ID, CONTEXT_ID)['assets']

can_trade = dict()
for asset, asset_data in inventory.items():
    if asset_data['tradable']:
            can_trade[asset] = asset_data

steam_client.send_offer_with_url(can_trade, dict(), TRADE_OFFER)
steam_client.confirmations.allow_all_confirmations([ConfirmationType.TRADE])
