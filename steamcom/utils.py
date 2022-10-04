import copy
import re
from typing import List

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
    pattern = '\D?(\\d*)(\\.|,)?(\\d*)'
    tokens = re.search(pattern, price, re.UNICODE)
    decimal_str = tokens.group(1) + '.' + tokens.group(3)
    return float(decimal_str)
