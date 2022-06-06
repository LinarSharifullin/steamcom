# steamcom
At the moment `steamcom` can only login into Steam web version and work with confirmations: receive and  responsible for them

# Credits
* [bukson](https://github.com/bukson) for the [steampy](https://github.com/bukson/steampy) library, in fact, I took more than 50% of the code from him
* [rossengeorgiev](https://github.com/rossengeorgiev) for the [steam](https://github.com/ValvePython/steam) library, in it I looked at how to implement a mobile web session
* [melvyn2](https://github.com/melvyn2) for the [PySteamAuth](https://github.com/melvyn2/PySteamAuth) program, his code helped me implement multiple confirmations

# Installation
```console
pip install git+https://github.com/LinarSharifullin/steamcom
```

# SteamClient Methods
**login() -> None**
```python
from steamcom.client import SteamClient


username = 'GabeNewell'
password = '124567'
shared_secret = 'zu+yLsdfjJRbg2FP+vsW+oNE='
identity_secret = 'U+Rs50612sdflkHlZ86ffPzgs='

steam_client = SteamClient(username, password, shared_secret, identity_secret)
steam_client.login()
print(steam_client.was_login_executed) # True
print(steam_client) # SteamClient: GabeNewell
```

**extract_session() -> dict**
Needed to save the session, you can save it from json or txt and use it in the future
```python
extracted_session = steam_client.extract_session()
print(extracted_session) # {'steam_id': '76...82', 'sessionid': '4f...90', 'steamLogin': '76...85', 'steamLoginSecure': '76...52'}
```

**load_session(extracted_session: dict) -> None**
```python
from steamcom.client import SteamClient


steam_client = SteamClient(username, passowrd, shared_secret, identity_secret)
steam_client.load_session(extracted_session)

```

**is_session_alive() -> bool**

# ConfirmationExecutor Methods
**get_confirmations() -> List[Confirmation]**
```python
confirmations = steam_client.confirmations.get_confirmations()
print(confirmations) # [Confirmation: Sell - IDF, Confirmation: Sell - SWAT]
```

From Confirmation class you can get various details:
```python
first_confirmation = confirmations[0]
print(first_confirmation.conf_id) # 11360346824
print(first_confirmation.conf_type) # 3
print(first_confirmation.data_accept) # Create Listing
print(first_confirmation.creator) # 3792607079523295593
print(first_confirmation.key) # 9359661368473990051
print(first_confirmation.title) # Sell - IDF
print(first_confirmation.receiving) # 200 pуб. (173,92 pуб.)
print(first_confirmation.time) # Just now
print(first_confirmation.icon) # https://community.akamai.steamstatic.com/economy/image/Iz...fKf/32fx32f

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
```python
from steamcom.guard import generate_one_time_code


secret_code = generate_one_time_code(shared_secret)
print(secret_code) # KPI21
```

**generate_confirmation_key(identity_secret: str, tag: str) -> bytes**

**generate_device_id(steam_id: str) -> str**