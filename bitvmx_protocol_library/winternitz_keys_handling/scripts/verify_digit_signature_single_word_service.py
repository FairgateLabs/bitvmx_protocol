import math
from typing import List, Optional

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.compute_max_checksum_service import (
    ComputeMaxChecksumService,
)


class VerifyDigitSignatureSingleWordService:
    def __init__(self):
        self.compute_max_checksum_service = ComputeMaxChecksumService()

    def __call__(
        self,
        script: BitcoinScript,
        public_keys: List[str],
        amount_of_bits: int,
        to_alt_stack: Optional[bool] = False,
    ):
        d0 = 2**amount_of_bits
        n0 = 1
        bits_per_digit_checksum = amount_of_bits

        d1, n1, max_checksum_value = self.compute_max_checksum_service(
            d0, n0, bits_per_digit_checksum
        )

        assert d0 == d1

        for i in range(len(public_keys)):
            self.verify_digit_signature(script, public_keys[i], d0)

        self.verify_checksum(script, 1, 1, max_checksum_value, amount_of_bits)

        if to_alt_stack:
            for i in range(n0):
                script.append("OP_TOALTSTACK")

        return 2

    @staticmethod
    def verify_digit_signature(script: BitcoinScript, public_key: str, d: int):
        script.extend([d - 1, "OP_MIN", "OP_DUP", "OP_TOALTSTACK", "OP_TOALTSTACK"])

        for _ in range(d):
            script.extend(["OP_DUP", "OP_HASH160"])

        script.extend(["OP_FROMALTSTACK", "OP_ROLL", public_key, "OP_EQUALVERIFY"])

        for _ in range(math.floor(d / 2)):
            script.append("OP_2DROP")
        if d % 2 == 1:
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
