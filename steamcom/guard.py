import base64
import hmac
import time
import struct
from hashlib import sha1


def generate_one_time_code(shared_secret: str, timestamp: int = None) -> str:
    timestamp = int(time.time()) if timestamp == None else timestamp
    time_buffer = struct.pack('>Q', timestamp // 30)  # pack as Big endian, uint64
    time_hmac = hmac.new(base64.b64decode(shared_secret), time_buffer, 
        digestmod=sha1).digest()
    begin = ord(time_hmac[19:20]) & 0xf
    full_code = struct.unpack('>I', time_hmac[begin:begin + 4])[0] & 0x7fffffff  # unpack as Big endian uint32
    chars = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''

    for _ in range(5):
        full_code, i = divmod(full_code, len(chars))
        code += chars[i]

    return code


def generate_confirmation_key(identity_secret: str, tag: str,
        timestamp: int = int(time.time())) -> bytes:
    buffer = struct.pack('>Q', timestamp) + tag.encode('ascii')
    base64_identity_secret = base64.b64decode(identity_secret)
    hmac_identity_secret = hmac.new(base64_identity_secret, buffer,
        digestmod=sha1)
    return base64.b64encode(hmac_identity_secret.digest())
