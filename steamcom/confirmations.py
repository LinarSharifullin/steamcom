import time
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from steamcom.guard import generate_confirmation_key, generate_device_id
from steamcom.models import ConfirmationTag, Confirmation, ConfirmationType
from steamcom.utils import login_required, api_request
from steamcom.exceptions import ApiException


class ConfirmationExecutor:
    CONF_URL = SteamUrl.COMMUNITY + '/mobileconf'

    def __init__(self, identity_secret: str, steam_id: str,
                 session: requests.Session) -> None:
        self.steam_id = steam_id
        self.identity_secret = identity_secret
        self.session = session
        self.was_login_executed = False

    @login_required
    def respond_to_confirmation(self, confirmation: Confirmation,
                                cancel: bool = False) -> bool:
        tag = ConfirmationTag.ALLOW if cancel is False\
            else ConfirmationTag.CANCEL
        params = self._create_confirmation_params(tag)
        params['op'] = tag
        params['ck'] = confirmation.key
        params['cid'] = confirmation.conf_id
        url = self.CONF_URL + '/ajaxop'
        response = api_request(self.session, url, params)
        try:
            status = response['success']
        except requests.exceptions.JSONDecodeError:
            status = False
        return status

    @login_required
    def respond_to_confirmations(self, confirmations: Iterable[Confirmation],
                                 cancel: bool = False) -> bool:
        tag = ConfirmationTag.ALLOW if cancel is False\
            else ConfirmationTag.CANCEL
        params = self._create_confirmation_params(tag)
        params['op'] = tag
        params['ck[]'] = [i.key for i in confirmations]
        params['cid[]'] = [i.conf_id for i in confirmations]
        response = self.session.post(
            self.CONF_URL + '/multiajaxop', data=params)
        try:
            status = response.json()['success']
        except requests.exceptions.JSONDecodeError:
            status = False
        return status

    @login_required
    def get_confirmations(self) -> list[Confirmation]:
        confirmations: list[Confirmation] = []
        confirmations_page = self._fetch_confirmations_page()
        soup = BeautifulSoup(confirmations_page.text, 'html.parser')
        if soup.select('#mobileconf_empty'):
            return confirmations
        container = soup.find(id="mobileconf_list")
        if not container:
            raise ApiException('An empty response returned')
        entries = container.find_all(class_="mobileconf_list_entry")
        for entry in entries:
            description = entry.select(
                ".mobileconf_list_entry_description > div")
            img_list = entry.select(".mobileconf_list_entry_icon img")
            img = img_list[0] if img_list else None
            confirmations.append(Confirmation(
                conf_id=entry['data-confid'],
                conf_type=ConfirmationType(int(entry['data-type'])),
                data_accept=entry['data-accept'],
                creator=entry['data-creator'],
                key=entry['data-key'],
                title=description[0].string,
                receiving=description[1].string,
                time=description[2].string,
                icon=img['src'] if img and img['src'] else "",
            ))
        return confirmations

    def _fetch_confirmations_page(self) -> requests.Response:
        tag = ConfirmationTag.CONF
        params = self._create_confirmation_params(tag)
        response = self.session.get(self.CONF_URL + '/getlist', params=params)
        return response

    def _create_confirmation_params(self, tag: str) -> dict[str, str]:
        timestamp = int(time.time())
        confirmation_key = generate_confirmation_key(
            self.identity_secret, tag)
        android_id = generate_device_id(self.steam_id)
        params = {
            'p': android_id,
            'a': self.steam_id,
            'k': confirmation_key,
            't': timestamp,
            'm': 'react',
            'tag': tag
        }
        return params

    @login_required
    def allow_all_confirmations(self, types: Iterable[ConfirmationType])\
            -> None:
        confirmations = self.get_confirmations()
        selected_confirmations = []
        for confirmation in confirmations:
            if confirmation.conf_type in types:
                selected_confirmations.append(confirmation)
        self.respond_to_confirmations(selected_confirmations)
