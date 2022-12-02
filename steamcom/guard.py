import base64
import hmac
import time
import struct
from hashlib import sha1


def generate_one_time_code(shared_secret: str) -> str:
    timestamp = int(time.time())
    time_buffer = struct.pack('>Q', timestamp // 30)
    time_hmac = hmac.new(
        base64.b64decode(shared_secret), time_buffer, digestmod=sha1).digest()
    begin = ord(time_hmac[19:20]) & 0xf
    full_code = struct.unpack('>I', time_hmac[begin:begin + 4])[0]\
        & 0x7fffffff
    chars = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''

    for _ in range(5):
        full_code, i = divmod(full_code, len(chars))
        code += chars[i]

    return code


def generate_confirmation_key(identity_secret: str, tag: str) -> bytes:
    timestamp = int(time.time())
    buffer = struct.pack('>Q', timestamp) + tag.encode('ascii')
    base64_identity_secret = base64.b64decode(identity_secret + '=')
    hmac_identity_secret = hmac.new(
        base64_identity_secret, buffer, digestmod=sha1)
    return base64.b64encode(hmac_identity_secret.digest())


def generate_device_id(steam_id: str) -> str:
    """It works, however it's different that one generated from mobile app"""
    hexed_steam_id = sha1(steam_id.encode('ascii')).hexdigest()
    device_id = 'android:' + '-'.join([
        hexed_steam_id[:8],
        hexed_steam_id[8:12],
        hexed_steam_id[12:16],
        hexed_steam_id[16:20],
        hexed_steam_id[20:32]
    ])
    return device_id
