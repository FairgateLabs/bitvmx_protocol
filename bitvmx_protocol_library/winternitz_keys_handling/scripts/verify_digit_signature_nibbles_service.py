import math
from typing import List, Optional

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.compute_max_checksum_service import (
    ComputeMaxChecksumService,
)


class VerifyDigitSignatureNibblesService:

    def __init__(self):
        self.compute_max_checksum_service = ComputeMaxChecksumService()
        self.d0 = 2**4

    def __call__(
        self,
        script: BitcoinScript,
        public_keys: List[str],
        n0: int,
        bits_per_digit_checksum: int,
        to_alt_stack: Optional[bool] = False,
    ):
        d1, n1, max_checksum_value = self.compute_max_checksum_service(
            self.d0, n0, bits_per_digit_checksum
        )

        i = 0
        while i < n1:
            self.verify_digit_signature_nibble(script, public_keys[i], d1)
            i += 1

        while i < n0 + n1:
            self.verify_digit_signature_nibble(script, public_keys[i], self.d0)
            i += 1

        self.verify_checksum(script, n0, n1, max_checksum_value, bits_per_digit_checksum)

        if to_alt_stack:
            for i in range(n0):
                script.append("OP_TOALTSTACK")

        return n0 + n1

    @staticmethod
    def verify_digit_signature_nibble(script: BitcoinScript, public_key: str, d: int):
        script.extend([d - 1, "OP_MIN", "OP_DUP", "OP_TOALTSTACK", "OP_TOALTSTACK"])

        for _ in range(d):
            script.extend(["OP_DUP", "OP_HASH160"])

        script.extend(["OP_FROMALTSTACK", "OP_PICK", public_key, "OP_EQUALVERIFY"])

        for _ in range(math.floor(d / 2)):
            script.append("OP_2DROP")
        script.append("OP_DROP")

    @staticmethod
    def verify_checksum(
        script: BitcoinScript,
        n0: int,
        n1: int,
        max_checksum_value: int,
        bits_per_digit_checksum: int,
    ):
        script.extend(["OP_FROMALTSTACK", "OP_DUP", "OP_NEGATE"])
        for _ in range(n0 - 1):
            script.extend(["OP_FROMALTSTACK", "OP_TUCK", "OP_SUB"])

        script.extend([max_checksum_value, "OP_ADD"])
        for i in range(n1 - 1, -1, -1):
            script.append("OP_FROMALTSTACK")
            for _ in range(bits_per_digit_checksum * i):
                script.extend(["OP_DUP", "OP_ADD"])
            if i < n1 - 1:
                script.append("OP_ADD")
        script.append("OP_EQUALVERIFY")
