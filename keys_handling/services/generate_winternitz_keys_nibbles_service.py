import hashlib
import math

from bitcoinutils.keys import PrivateKey
from typing import Optional

from keys_handling.functions.signature_functions import hex_ripemd160, hex_hash160


def compute_max_checksum(d0, n0, bits_per_digit_checksum):
    max_checksum_value = n0 * (d0 - 1)
    max_checksum_binary_representation = bin(max_checksum_value)[2:]
    n1 = math.ceil(len(max_checksum_binary_representation) / bits_per_digit_checksum)
    if n1 > 1:
        d1 = 2**bits_per_digit_checksum
    else:
        d1 = max_checksum_value + 1
    return d1, n1, max_checksum_value


class GenerateWinternitzKeysNibblesService:

    def __init__(self, private_key: PrivateKey, bits_per_digit_checksum: Optional[int] = 4):
        self.private_key = private_key.to_bytes().hex()
        self.bits_per_digit_checksum = bits_per_digit_checksum
        self.d0 = 2 ** 4

    def __call__(self, step: int, n0: int, gap: Optional[int] = 0):
        hex_step = format(step, "04x")
        current_private_key = hashlib.sha256(
            bytes.fromhex(self.private_key + hashlib.sha256(bytes.fromhex(hex_step)).hexdigest())
        ).hexdigest()

        d1, n1, max_checksum_value = compute_max_checksum(self.d0, n0, self.bits_per_digit_checksum)

        public_keys = []

        for i in range(n1):
            current_derived_private_key = hashlib.sha256(
                bytes.fromhex(current_private_key + hashlib.sha256(bytes.fromhex(format(i, "04x"))).hexdigest())
            ).hexdigest()
            signatures = [
                hex_ripemd160(current_derived_private_key)
            ]
            for _ in range(d1):
                signatures.append(hex_hash160(signatures[-1]))

            public_keys.append(signatures)

        for i in range(n1, n0 + n1, 1):
            current_derived_private_key = hashlib.sha256(
                bytes.fromhex(current_private_key + hashlib.sha256(bytes.fromhex(format(i, "04x"))).hexdigest())
            ).hexdigest()
            signatures = [
                hex_ripemd160(current_derived_private_key)
            ]
            for _ in range(self.d0):
                signatures.append(hex_hash160(signatures[-1]))

            public_keys.append(signatures)

        return public_keys




