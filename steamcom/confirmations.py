import requests
import time
from typing import List

from bs4 import BeautifulSoup

from steamcom.guard import generate_confirmation_key, generate_device_id
from steamcom.models import Tag, Confirmation


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self, identity_secret: str, steam_id: str,
            session: requests.Session) -> None:
        self.steam_id = steam_id
        self.identity_secret = identity_secret
        self.session = session

    def get_confirmations(self) -> List[Confirmation]:
        confirmations = []
        confirmations_page = self._fetch_confirmations_page()
        soup = BeautifulSoup(confirmations_page.text, 'html.parser')
        if soup.select('#mobileconf_empty'):
            return confirmations
        container = soup.find(id="mobileconf_list")
        entries = container.find_all(class_="mobileconf_list_entry")
        for entry in entries:
            description = entry.select(
                ".mobileconf_list_entry_description > div")
            img = entry.select(".mobileconf_list_entry_icon img")[0]
            confirmations.append(Confirmation(
                conf_id = entry['data-confid'],
                conf_type = entry['data-type'],
                data_accept = entry['data-accept'],
                creator = entry['data-creator'],
                key = entry['data-key'],
                title = description[0].string,
                receiving = description[1].string,
                time = description[2].string,
                icon = img['src'] if len(img['src']) > 0 else "",
            ))
        return confirmations

    def _fetch_confirmations_page(self) -> requests.Response:
        tag = Tag.CONF.value
        params = self._create_confirmation_params(tag)
        response = self.session.get(self.CONF_URL + '/conf', params=params)
        return response

    def _create_confirmation_params(self, tag_string: str) -> dict:
        timestamp = int(time.time())
        confirmation_key = generate_confirmation_key(self._identity_secret, 
            tag_string, timestamp)
        android_id = generate_device_id(self._my_steam_id)
        params = {
            'p': android_id,
            'a': self._my_steam_id,
            'k': confirmation_key,
            't': timestamp,
            'm': 'android',
            'tag': tag_string
        }
        return params
