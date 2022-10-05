import requests
import json

from steamcom.utils import (login_required, text_between,
                            get_listing_id_to_assets_address_from_html,
                            get_market_listings_from_html,
                            merge_items_with_descriptions_from_listing,
                            get_market_sell_listings_from_api)
from steamcom.models import SteamUrl
from steamcom.exceptions import ApiException


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

    @login_required
    def get_my_market_listings(self) -> dict:
        response = self.session.get('%s/market' % SteamUrl.COMMUNITY)
        if response.status_code != 200:
            text = 'Problem getting the listings. http code: {}'
            raise ApiException(text.format(response.status_code))
        assets_descriptions = json.loads(
            text_between(response.text, 'var g_rgAssets = ', ';\r\n'))
        listing_id_to_assets_address = \
            get_listing_id_to_assets_address_from_html(response.text)
        listings = get_market_listings_from_html(response.text)
        listings = merge_items_with_descriptions_from_listing(
            listings, listing_id_to_assets_address, assets_descriptions)
        listings_end = '<span id="tabContentsMyActiveMarketListings_end">'
        listings_total = '<span id="tabContentsMyActiveMarketListings_total">'
        if listings_end in response.text:
            n_showing = int(text_between(response.text,
                                         listings_end, '</span>'))
            n_total = int(text_between(
                response.text, listings_total, '</span>').replace(',', ''))
            if n_showing < n_total < 1000:
                url = '{}/market/mylistings/render/?query=&start={}&count={}'\
                    .format(SteamUrl.COMMUNITY, n_showing, -1)
                response = self._session.get(url)
                if response.status_code != 200:
                    text = 'Problem getting the listings. http code: {}'
                    raise ApiException(text.format(response.status_code))
                jresp = response.json()
                listing_id_to_assets_address =\
                    get_listing_id_to_assets_address_from_html(
                        jresp.get('hovers'))
                listings_2 = get_market_sell_listings_from_api(
                    jresp.get('results_html'))
                listings_2 = merge_items_with_descriptions_from_listing(
                    listings_2, listing_id_to_assets_address,
                    jresp.get('assets'))
                listings['sell_listings'] = {**listings['sell_listings'],
                                             **listings_2['sell_listings']}
            else:
                for i in range(0, n_total, 100):
                    url = '{}/market/mylistings/?query=&start={}&count={}'\
                        .format(SteamUrl.COMMUNITY, n_showing + i, 100)
                    response = self._session.get(url)
                    if response.status_code != 200:
                        text = 'Problem getting the listings. http code: {}'
                        raise ApiException(text.format(response.status_code))
                    jresp = response.json()
                    listing_id_to_assets_address =\
                        get_listing_id_to_assets_address_from_html(
                            jresp.get('hovers'))
                    listings_2 = get_market_sell_listings_from_api(
                        jresp.get('results_html'))
                    listings_2 = merge_items_with_descriptions_from_listing(
                        listings_2, listing_id_to_assets_address,
                        jresp.get('assets'))
                    listings['sell_listings'] = {
                        **listings['sell_listings'],
                        **listings_2['sell_listings']}
        return listings
