# Steamcom
At the moment `steamcom` can only login into Steam web version and work with confirmations: receive and  responsible for them

## Credits
* [bukson](https://github.com/bukson) for the [steampy](https://github.com/bukson/steampy) library, in fact, I took more than 50% of the code from him
* [rossengeorgiev](https://github.com/rossengeorgiev) for the [steam](https://github.com/ValvePython/steam) library, in it I looked at how to implement a mobile web session
* [melvyn2](https://github.com/melvyn2) for the [PySteamAuth](https://github.com/melvyn2/PySteamAuth) program, his code helped me implement multiple confirmations

# Installation
```console
pip install git+https://github.com/LinarSharifullin/steamcom
```

# SteamClient Methods
**login(username: str, password: str, shared_secret: str, identity_secret: str) -> None**
```python
from steamcom.client import SteamClient

username = 'GabeNewell'
password = '124567'
shared_secret = 'zu+yLsdfjJRbg2FP+vsW+oNE='
identity_secret = 'U+Rs50612sdflkHlZ86ffPzgs='

steam_client = SteamClient()
steam_client.login(username, password, shared_secret, identity_secret)
print(steam_client) # SteamClient: GabeNewell
```

**is_session_alive() -> bool**

# ConfirmationExecutor Methods
**get_confirmations() -> List[Confirmation]**
```python
confirmations = steam_client.confirmations.get_confirmations()
print(confirmations) # [Confirmation: Sell - IDF, Confirmation: Sell - SWAT]
```

**respond_to_confirmations(confirmations: List[Confirmation], cancel: bool = False) -> bool**
```python
status = steam_client.confirmations.respond_to_confirmations(confirmations)
print(status) # True
```

**respond_to_confirmation(confirmation: Confirmation, cancel: bool = False) -> bool**
```python
first_confirmation = confirmations[0]
status = steam_client.confirmations.respond_to_confirmation(first_confirmation)
print(status) # True
```

# guard module functions
**generate_one_time_code(shared_secret: str) -> str**

**generate_confirmation_key(identity_secret: str, tag: str) -> bytes**

**generate_device_id(steam_id: str) -> str**