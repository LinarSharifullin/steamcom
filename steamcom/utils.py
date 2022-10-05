import copy
import re
from typing import List

from bs4 import BeautifulSoup, Tag

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
    pattern = r'\D?(\\d*)(\\.|,)?(\\d*)'
    tokens = re.search(pattern, price, re.UNICODE)
    decimal_str = tokens.group(1) + '.' + tokens.group(3)
    return float(decimal_str)


def text_between(text: str, begin: str, end: str) -> str:
    start = text.index(begin) + len(begin)
    end = text.index(end, start)
    return text[start:end]


def get_listing_id_to_assets_address_from_html(html: str) -> dict:
    listing_id_to_assets_address = {}
    regex = r"CreateItemHoverFromContainer\( [\w]+, 'mylisting_([\d]+)_[\w]+'"
    regex += r", ([\d]+), '([\d]+)', '([\d]+)', [\d]+ \);"
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
                                     {'id': re.compile(r'mylisting_\d+')})
    sell_listings_dict = {}
    for listing_raw in sell_listings_raw:
        spans = listing_raw.select('span[title]')
        created_date = listing_raw.findAll(
                'div', {'class': 'market_listing_listed_date'})[0]
        listing = {
            'listing_id': listing_raw.attrs['id'].replace('mylisting_', ''),
            'buyer_pay': spans[0].text.strip(),
            'you_receive': spans[1].text.strip()[1:-1],
            'created_on': created_date.text.strip(),
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
        order = {
            'order_id': order.attrs['id'].replace('mybuyorder_', ''),
            'quantity': int(qnt_price_raw[0].strip()),
            'price': qnt_price_raw[1].strip(),
            'item_name': order.a.text
        }
        buy_orders_dict[order['order_id']] = order
    return buy_orders_dict
