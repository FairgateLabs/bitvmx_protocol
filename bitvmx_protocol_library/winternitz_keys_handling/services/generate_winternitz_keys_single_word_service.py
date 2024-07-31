import hashlib

from bitcoinutils.keys import PrivateKey

from bitvmx_protocol_library.winternitz_keys_handling.functions.signature_functions import (
    hex_hash160,
    hex_ripemd160,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.compute_max_checksum_service import (
    ComputeMaxChecksumService,
)


class GenerateWinternitzKeysSingleWordService:
    def __init__(self, private_key: PrivateKey):
        self.private_key = private_key.to_bytes().hex()
        self.compute_max_checksum_service = ComputeMaxChecksumService()

    def __call__(self, step: int, case: int, amount_of_bits: int):
        d0 = 2**amount_of_bits
        n0 = 1
        bits_per_digit_checksum = amount_of_bits

        hex_step = format(step, "04x") + format(case, "04x")
        current_private_key = hashlib.sha256(
            bytes.fromhex(self.private_key + hashlib.sha256(bytes.fromhex(hex_step)).hexdigest())
        ).hexdigest()

        d1, _, _ = self.compute_max_checksum_service(d0, n0, bits_per_digit_checksum)
        public_keys = []
        checksum_derived_private_key = hashlib.sha256(
            bytes.fromhex(
                current_private_key + hashlib.sha256(bytes.fromhex(format(1, "04x"))).hexdigest()
            )
        ).hexdigest()
        signatures = [hex_ripemd160(checksum_derived_private_key)]
        for _ in range(d1):
            signatures.append(hex_hash160(signatures[-1]))
        public_keys.append(signatures)

        word_derived_private_key = hashlib.sha256(
            bytes.fromhex(
                current_private_key + hashlib.sha256(bytes.fromhex(format(0, "04x"))).hexdigest()
            )
        ).hexdigest()
        signatures = [hex_ripemd160(word_derived_private_key)]
        for _ in range(d0):
            signatures.append(hex_hash160(signatures[-1]))
        public_keys.append(signatures)

        return public_keys
