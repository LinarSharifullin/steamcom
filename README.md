# Credits
* [bukson](https://github.com/bukson) for the [steampy](https://github.com/bukson/steampy) library, in fact, I took more than 50% of the code from him
* [rossengeorgiev](https://github.com/rossengeorgiev) for the [steam](https://github.com/ValvePython/steam) library, in it I looked at how to implement a mobile web session
* [melvyn2](https://github.com/melvyn2) for the [PySteamAuth](https://github.com/melvyn2/PySteamAuth) program, his code helped me implement multiple confirmations

# Installation
```console
pip install git+https://github.com/LinarSharifullin/steamcom
```

# SteamClient Methods
## login() -> None
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

## extract_session() -> dict[str, str]
Needed to save the session, you can save it from json or txt and use it in the future
```python
extracted_session = steam_client.extract_session()
print(extracted_session) # {'steam_id': '76...82', 'sessionid': '4f...90', 'steamLogin': '76...85', 'steamLoginSecure': '76...52'}
```

## load_session(extracted_session: Mapping[str, str]) -> None
```python
from steamcom.client import SteamClient


steam_client = SteamClient(username, passowrd, shared_secret, identity_secret)
steam_client.load_session(extracted_session)
```

## is_session_alive() -> bool

## get_partner_inventory(partner_steam_id: str, app_id: str, context_id: str, delay: int = 3) -> dict:
Return parsed inventory:
```python
{'assets': {'12176056772': {'actions': ...,
                            'amount': '1',
                            'appid': 440,
                            'background_color': '3C352E',
                            'classid': '2569645959',
                            'commodity': 0,
                            'contextid': '2',
                            'currency': 0,
                            'descriptions': ...,
                            'icon_url': ...,
                            'icon_url_large': ...,
                            'id': '12176056772',
                            'instanceid': '5020381097',
                            'market_actions': ...,
                            'market_hash_name': 'Civic Duty Mk.II War Paint '
                                                '(Field-Tested)',
                            'market_marketable_restriction': 0,
                            'market_name': 'Civic Duty Mk.II War Paint '
                                           '(Field-Tested)',
                            'market_tradable_restriction': 7,
                            'marketable': 1,
                            'name': 'Civic Duty Mk.II War Paint',
                            'name_color': 'FAFAFA',
                            'tags': ...
                            'tradable': 0,
                            'type': ''}},
 'total_inventory_count': 1}
```

## get_my_inventory(app_id: str, context_id: str, delay: int = 3) -> dict:
The response is the same as get_partner_inventory

## get_wallet_balance() -> float

# ConfirmationExecutor Methods
## get_confirmations() -> list[Confirmation]
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

## respond_to_confirmations(confirmations: Iterable[Confirmation], cancel: bool = False) -> bool
```python
status = steam_client.confirmations.respond_to_confirmations(confirmations)
print(status) # True
```

## respond_to_confirmation(confirmation: Confirmation, cancel: bool = False) -> bool
```python
first_confirmation = confirmations[0]
status = steam_client.confirmations.respond_to_confirmation(first_confirmation)
print(status) # True
```

# guard module functions
## generate_one_time_code(shared_secret: str) -> str
```python
from steamcom.guard import generate_one_time_code


secret_code = generate_one_time_code(shared_secret)
print(secret_code) # KPI21
```

## generate_confirmation_key(identity_secret: str, tag: str) -> bytes

## generate_device_id(steam_id: str) -> str


# market module functions
## get_price_history(app_id: str, market_hash_name: str) -> dict
Return parsed graph dots:
```python
{'Oct 05 2022': {'dots': {'21': {'price': 99.435, 'sales': 43},
                          '22': {'price': 139.317, 'sales': 270},
                          '23': {'price': 162.369, 'sales': 480}}},
 'Oct 06 2022': {'dots': {'00': {'price': 136.98, 'sales': 1591},
                          '01': {'price': 95.765, 'sales': 2486},
                          '02': {'price': 128.912, 'sales': 1166},
                          '03': {'price': 79.4, 'sales': 3488},
                          '04': {'price': 64.853, 'sales': 3509},
                          '05': {'price': 48.488, 'sales': 3615},
                          '06': {'price': 38.628, 'sales': 4189},
                          '07': {'price': 19.867, 'sales': 5858},
                          '08': {'price': 14.915, 'sales': 4695},
                          '09': {'price': 17.805, 'sales': 3632},
                          '10': {'price': 36.602, 'sales': 2347},
                          '11': {'price': 39.764, 'sales': 2222},
                          '12': {'price': 38.924, 'sales': 2625},
                          '13': {'price': 29.821, 'sales': 2613},
                          '14': {'price': 29.942, 'sales': 1829},
                          '15': {'price': 41.774, 'sales': 1553},
                          '16': {'price': 54.72, 'sales': 1312},
                          '17': {'price': 77.849, 'sales': 725},
                          '18': {'price': 93.34, 'sales': 584},
                          '19': {'price': 85.461, 'sales': 668},
                          '20': {'price': 87.43, 'sales': 747},
                          '21': {'price': 89.098, 'sales': 744},
                          '22': {'price': 98.189, 'sales': 1210},
                          '23': {'price': 58.792, 'sales': 2255}}},
 'Oct 07 2022': {'dots': {'00': {'price': 53.943, 'sales': 3456},
                          '01': {'price': 48.988, 'sales': 3294},
                          '02': {'price': 44.246, 'sales': 3292},
                          '03': {'price': 44.246, 'sales': 3058},
                          '04': {'price': 47.308, 'sales': 2573},
                          '05': {'price': 30.305, 'sales': 3619},
                          '06': {'price': 18.789, 'sales': 5698}}}}
```

## get_orders_histogram(item_name_id: str) -> dict
Return parsed histogram dots:
```python
{'buy_order_graph': [{'price': 2.67, 'value': 1},
                     {'price': 2.66, 'value': 1},
                     {'price': 2.6, 'value': 4},
                     {'price': 2.57, 'value': 23},
                     {'price': 2.54, 'value': 20},
                     {'price': 2.5, 'value': 1},
                     {'price': 2.49, 'value': 1},
                     {'price': 2.02, 'value': 3},
                     {'price': 1.92, 'value': 9},
                     {'price': 1.74, 'value': 15},
                     {'price': 1.65, 'value': 1},
                     {'price': 1.53, 'value': 2},
                     {'price': 1.4, 'value': 1},
                     {'price': 1.3, 'value': 9},
                     {'price': 1.24, 'value': 1},
                     {'price': 1, 'value': 15},
                     {'price': 0.87, 'value': 97}],
 'sell_order_graph': [{'price': 3.24, 'value': 1},
                      {'price': 3.25, 'value': 1},
                      {'price': 3.27, 'value': 1},
                      {'price': 3.28, 'value': 4},
                      {'price': 3.29, 'value': 2},
                      {'price': 3.3, 'value': 15},
                      {'price': 3.33, 'value': 1},
                      {'price': 3.34, 'value': 3},
                      {'price': 3.35, 'value': 1},
                      {'price': 3.36, 'value': 2},
                      {'price': 3.38, 'value': 1},
                      {'price': 3.41, 'value': 4},
                      {'price': 3.42, 'value': 1},
                      {'price': 3.45, 'value': 36},
                      {'price': 3.49, 'value': 2},
                      {'price': 3.5, 'value': 1},
                      {'price': 3.52, 'value': 1},
                      {'price': 3.56, 'value': 2}]}
```
