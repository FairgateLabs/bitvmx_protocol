import hashlib
from typing import Optional

from bitcoinutils.keys import PrivateKey

from bitvmx_protocol_library.winternitz_keys_handling.functions.signature_functions import (
    hex_hash160,
    hex_ripemd160,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.compute_max_checksum_service import (
    ComputeMaxChecksumService,
)


class GenerateWinternitzKeysNibblesService:

    def __init__(self, private_key: PrivateKey, bits_per_digit_checksum: Optional[int] = 4):
        self.private_key = private_key.to_bytes().hex()
        self.bits_per_digit_checksum = bits_per_digit_checksum
        self.d0 = 2**4
        self.compute_max_checksum_service = ComputeMaxChecksumService()

    def __call__(self, step: int, case: int, n0: int):
        hex_step = format(step, "04x") + format(case, "04x")
        current_private_key = hashlib.sha256(
            bytes.fromhex(self.private_key + hashlib.sha256(bytes.fromhex(hex_step)).hexdigest())
        ).hexdigest()

        d1, n1, _ = self.compute_max_checksum_service(self.d0, n0, self.bits_per_digit_checksum)

        public_keys = []

        for i in range(n1):
            current_derived_private_key = hashlib.sha256(
                bytes.fromhex(
                    current_private_key
                    + hashlib.sha256(bytes.fromhex(format(n0 + n1 - i - 1, "04x"))).hexdigest()
                )
            ).hexdigest()
            signatures = [hex_ripemd160(current_derived_private_key)]
            for _ in range(d1):
                signatures.append(hex_hash160(signatures[-1]))

            public_keys.append(signatures)

        for i in range(n1, n0 + n1, 1):
            current_derived_private_key = hashlib.sha256(
                bytes.fromhex(
                    current_private_key
                    + hashlib.sha256(bytes.fromhex(format(n0 + n1 - i - 1, "04x"))).hexdigest()
                )
            ).hexdigest()
            signatures = [hex_ripemd160(current_derived_private_key)]
            for _ in range(self.d0):
                signatures.append(hex_hash160(signatures[-1]))

            public_keys.append(signatures)

        return public_keys
