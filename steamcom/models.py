import enum


class SteamUrl:
    API = 'https://api.steampowered.com'
    COMMUNITY = 'https://steamcommunity.com'
    STORE = 'https://store.steampowered.com'


class Confirmation:
    def __init__(self, conf_id: str, conf_type: str, data_accept: str, 
            creator, key: str, title: str, receiving: str, time: str, 
            icon: str) -> None:
        self.conf_id = conf_id
        self.conf_type = conf_type
        self.data_accept = data_accept
        self.creator = creator
        self.key = key
        self.title = title
        self.receiving = receiving
        self.time = time
        self.icon = icon
    
    def __str__(self) -> str:
        return f'Confirmation: {self.title}'
    
    def __repr__(self) -> str:
        return f'Confirmation: {self.title}'


class ConfirmationType(enum.Enum):
    trade = '2' # Send offer and accept
    create_listing = '3'
    confirm = '6' # I saw in the mail change


class Tag(enum.Enum):
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'