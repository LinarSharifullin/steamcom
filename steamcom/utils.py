
from binascii import hexlify
from steam.core.crypto import sha1_hash, random_bytes


def generate_session_id() -> str:
    return hexlify(sha1_hash(random_bytes(32)))[:32].decode('ascii')
