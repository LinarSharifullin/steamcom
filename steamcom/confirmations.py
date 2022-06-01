import requests
import time

from steamcom.guard import generate_confirmation_key, generate_device_id
from steamcom.models import Tag


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self, identity_secret: str, my_steam_id: str, 
            session: requests.Session) -> None:
        self._my_steam_id = my_steam_id
        self._identity_secret = identity_secret
        self._session = session

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

    def _fetch_confirmations_page(self) -> requests.Response:
        tag = Tag.CONF.value
        params = self._create_confirmation_params(tag)
        response = self._session.get(self.CONF_URL + '/conf', params=params)
        return response