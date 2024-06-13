import hashlib


def byte_hash160(data: bytes) -> bytes:
    """sha256 followed by ripemd160"""
    hash_1 = hashlib.sha256(data).digest()
    hash_2 = hashlib.new("ripemd160", hash_1).digest()
    return hash_2


def byte_ripemd160(data: bytes) -> bytes:
    return hashlib.new("ripemd160", data).digest()


def byte_sha256(data: bytes) -> bytes:
    """One round of SHA256"""
    return hashlib.sha256(data).digest()


def hex_ripemd160(data: str) -> str:
    return byte_ripemd160(bytes.fromhex(data)).hex()


def hex_hash160(data: str) -> str:
    return byte_hash160(bytes.fromhex(data)).hex()
