import time
from typing import Iterable

import requests

from steamcom.guard import generate_confirmation_key, generate_device_id
from steamcom.models import (ConfirmationTag, Confirmation, ConfirmationType,
                             SteamUrl)
from steamcom.utils import login_required, api_request


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
        params['ck'] = confirmation.nonce
        params['cid'] = confirmation.id
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
        params['ck[]'] = [i.nonce for i in confirmations]
        params['cid[]'] = [i.id for i in confirmations]
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
        for conf in confirmations_page['conf']:
            confirmations.append(Confirmation(
                type=ConfirmationType(int(conf['type'])),
                type_name=conf['type_name'],
                id=conf['id'],
                creator_id=conf['creator_id'],
                nonce=conf['nonce'],
                creation_time=conf['creation_time'],
                cancel=conf['cancel'],
                accept=conf['accept'],
                icon=conf['icon'],
                multi=conf['multi'],
                headline=conf['headline'],
                summary=conf['summary'],
                warn=conf['warn']
            ))
        return confirmations

    def _fetch_confirmations_page(self) -> requests.Response:
        url = self.CONF_URL + '/getlist'
        tag = ConfirmationTag.CONF
        params = self._create_confirmation_params(tag)
        return api_request(self.session, url, params=params)

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
            if confirmation.type in types:
                selected_confirmations.append(confirmation)
        self.respond_to_confirmations(selected_confirmations)
