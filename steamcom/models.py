import enum
from typing import NamedTuple


class SteamUrl:
    API = 'https://api.steampowered.com'
    COMMUNITY = 'https://steamcommunity.com'
    STORE = 'https://store.steampowered.com'


class ConfirmationTag:
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'


class ConfirmationType(enum.IntEnum):
    TRADE = 2  # Send offer and accept
    CREATE_LISTING = 3
    CHANGE_PHONE_NUMBER = 5
    CONFIRM = 6  # I saw in the mail change


class Confirmation(NamedTuple):
    conf_id: str
    conf_type: ConfirmationType
    data_accept: str
    creator: str
    key: str
    title: str
    receiving: str
    time: str
    icon: str

    def __str__(self) -> str:
        return f'Confirmation: {self.title}'

    def __repr__(self) -> str:
        return f'Confirmation: {self.title}'
