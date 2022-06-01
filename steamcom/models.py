import enum


class SteamUrl:
    API_URL = 'https://api.steampowered.com'
    COMMUNITY_URL = 'https://steamcommunity.com'
    STORE_URL = 'https://store.steampowered.com'


class Confirmation:
    def __init__(self, conf_id, conf_type, data_accept, creator, key, title,
            receiving, time, icon) -> None:
        self.conf_id = conf_id
        self.conf_type = conf_type
        self.data_accept = data_accept
        self.creator = creator
        self.key = key
        self.title = title
        self.receiving = receiving
        self.time = time
        self.icon = icon


class Tag(enum.Enum):
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'
