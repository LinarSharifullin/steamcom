import rsa

import requests

from steamcom.models import SteamUrl



class LoginExecutor:

    def __init__(self, username: str, password: str, shared_secret: str,
            session: requests.Session) -> None:
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.session = session