import copy
import re
from typing import List
from datetime import datetime
from urllib.parse import unquote

from bs4 import BeautifulSoup, Tag

from steamcom.models import HistoryStatus
from steamcom.exceptions import LoginRequired


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if self.was_login_executed is False:
            raise LoginRequired('Use LoginExecutor.login method first')
        else:
            return func(self, *args, **kwargs)
    return func_wrapper


def merge_items_with_descriptions_from_inventory(inventory_response: dict,
                                                 context_id: str) -> dict:
    inventory = inventory_response.get('assets', [])
    if not inventory:
        return {}
    descriptions = {}
    for description in inventory_response['descriptions']:
        descriptions[get_description_key(description)] = description
    return merge_items(inventory, descriptions, context_id=context_id)


def merge_items_with_descriptions_from_listing(
        listings: dict, ids_to_assets_address: dict,
        descriptions: dict) -> dict:
    for listing_id, listing in listings.get('sell_listings').items():
        ad = ids_to_assets_address[listing_id]  # ad = asset_description
        description = descriptions[ad[0]][ad[1]][ad[2]]
        listing['description'] = description
    return listings


def merge_items(items: List[dict], descriptions: dict, **kwargs) -> dict:
    merged_items = {}
    for item in items:
        description_key = get_description_key(item)
        description = copy.copy(descriptions[description_key])
        item_id = item.get('id') or item['assetid']
        description['contextid'] = item.get('contextid')\
            or kwargs['context_id']
        description['id'] = item_id
        description['amount'] = item['amount']
        merged_items[item_id] = description
    return merged_items


def get_description_key(item: dict) -> str:
    return item['classid'] + '_' + item['instanceid']


def parse_price(price: str) -> float:
    pattern = '\\D?(\\d*)(\\.|,)?(\\d*)'
    tokens = re.search(pattern, price, re.UNICODE)
    decimal_str = tokens.group(1) + '.' + tokens.group(3)
    return float(decimal_str)


def text_between(text: str, begin: str, end: str) -> str:
    start = text.index(begin) + len(begin)
    end = text.index(end, start)
    return text[start:end]


def get_listing_id_to_assets_address_from_html(html: str) -> dict:
    listing_id_to_assets_address = {}
    regex = "CreateItemHoverFromContainer\\( [\\w]+, 'mylisting_([\\d]+)"
    regex += "_[\\w]+', ([\\d]+), '([\\d]+)', '([\\d]+)', [\\d]+ \\);"
    for match in re.findall(regex, html):
        listing_id_to_assets_address[match[0]] = [
            str(match[1]), match[2], match[3]]
    return listing_id_to_assets_address


def get_market_listings_from_html(html: str) -> dict:
    document = BeautifulSoup(html, 'html.parser')
    nodes = document.select('div[id=myListings]')[0].findAll(
        'div', {'class': 'market_home_listing_table'})
    sell_listings_dict = {}
    buy_orders_dict = {}
    for node in nodes:
        if 'My sell listings' in node.text:
            sell_listings_dict = get_sell_listings_from_node(node)
        elif 'My listings awaiting confirmation' in node.text:
            sell_listings_awaiting_conf = get_sell_listings_from_node(node)
            for listing in sell_listings_awaiting_conf.values():
                listing['need_confirmation'] = True
            sell_listings_dict.update(sell_listings_awaiting_conf)
        elif 'My buy orders' in node.text:
            buy_orders_dict = get_buy_orders_from_node(node)
    return {'buy_orders': buy_orders_dict, 'sell_listings': sell_listings_dict}


def get_market_sell_listings_from_api(html: str) -> dict:
    document = BeautifulSoup(html, 'html.parser')
    sell_listings_dict = get_sell_listings_from_node(document)
    return {'sell_listings': sell_listings_dict}


def get_sell_listings_from_node(node: Tag) -> dict:
    sell_listings_raw = node.findAll('div',
                                     {'id': re.compile('mylisting_\\d+')})
    sell_listings_dict = {}
    for listing_raw in sell_listings_raw:
        spans = listing_raw.select('span[title]')
        if 'Sold!' in spans[0].text:
            continue
        created_date = listing_raw.findAll(
                'div', {'class': 'market_listing_listed_date'})[0]
        created_on = created_date.text.strip()
        created_datetime = datetime.strptime(created_on, '%d %b')
        datetime_now = datetime.now()
        if created_datetime.month > datetime_now.month\
            or (created_datetime.month == datetime_now.month
                and created_datetime.day > datetime_now.day):
            created_datetime = created_datetime.replace(
                year=datetime.now().year-1)
        else:
            created_datetime = created_datetime.replace(
                year=datetime.now().year)
        timestamp = created_datetime.timestamp()
        listing = {
            'listing_id': listing_raw.attrs['id'].replace('mylisting_', ''),
            'buyer_pay': parse_price(spans[0].text.strip()),
            'you_receive': parse_price(spans[1].text.strip()[1:-1]),
            'created_on': created_on,
            'created_timestamp': int(timestamp),
            'need_confirmation': False
        }
        sell_listings_dict[listing['listing_id']] = listing
    return sell_listings_dict


def get_buy_orders_from_node(node: Tag) -> dict:
    buy_orders_raw = node.findAll('div', {'id': re.compile('mybuyorder_\\d+')})
    buy_orders_dict = {}
    for order in buy_orders_raw:
        qnt_price_raw = order.select('span[class=market_listing_price]')[0]\
            .text.split("@")
        regex = 'a[class=market_listing_item_name_link]'
        item_link = order.select(regex)[0]['href']
        order = {
            'order_id': order.attrs['id'].replace('mybuyorder_', ''),
            'quantity': int(qnt_price_raw[0].strip()),
            'price': parse_price(qnt_price_raw[1].strip()),
            'item_name': order.a.text,
            'item_link': item_link,
            'market_hash_name': unquote(item_link.split('/')[-1],
                                        encoding='utf-8', errors='replace')
        }
        buy_orders_dict[order['order_id']] = order
    return buy_orders_dict


def parse_history(history):
    unowned_ids = {}
    for app_id, app_data in history['assets'].items():
        for context_id, context_data in app_data.items():
            for asset, asset_data in context_data.items():
                unowned_ids[asset_data['unowned_id']] = asset

    for event in history['events']:
        if event['event_type'] == HistoryStatus.LISTED.value\
                or event['event_type'] == HistoryStatus.CANCELED.value:
            listing = history['listings'][event['listingid']]
            price = listing['original_price'] / 100
            currency_id = listing['currencyid']
            asset_id = listing['asset']['id']
            app_id = str(listing['asset']['appid'])
            context_id = listing['asset']['contextid']
            asset = history['assets'][app_id][context_id][asset_id]
            event.update({'price': price, 'currency_id': currency_id,
                         'asset': asset})
        else:
            purchase_id = event['listingid'] + '_' + event['purchaseid']
            purchase = history['purchases'][purchase_id]
            if event['event_type'] == HistoryStatus.PURCHASED:
                currency_id = purchase['received_currencyid']
                partner_currency_id = purchase['currencyid']
                price = (purchase['paid_amount'] + purchase['paid_fee']) / 100
            else:
                currency_id = purchase['currencyid']
                partner_currency_id = purchase['received_currencyid']
                price = purchase['received_amount'] / 100
            asset_id = purchase['asset']['id']
            app_id = str(purchase['asset']['appid'])
            context_id = purchase['asset']['contextid']
            new_asset_id = purchase['asset']['new_id']
            original_id = unowned_ids[asset_id]
            asset = history['assets'][app_id][context_id][original_id]
            event.update({
                'price': price,
                'currency_id': currency_id,
                'partner_currency_id': partner_currency_id,
                'new_asset_id': new_asset_id,
                'asset': asset
            })
    return history['events']
