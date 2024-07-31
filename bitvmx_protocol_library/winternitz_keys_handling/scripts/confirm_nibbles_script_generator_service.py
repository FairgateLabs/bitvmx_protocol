from typing import List

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


class ConfirmNibblesScriptGeneratorService:
    def __init__(self):
        self.verify_input_nibbles_message_from_public_keys = VerifyDigitSignatureNibblesService()

    def __call__(
        self,
        script: BitcoinScript,
        prover_public_keys: List[str],
        verifier_public_keys: List[str],
        n0: int,
        bits_per_digit_checksum: int,
    ):

        self.verify_input_nibbles_message_from_public_keys(
            script,
            verifier_public_keys,
            n0,
            bits_per_digit_checksum,
            to_alt_stack=True,
        )

        self.verify_input_nibbles_message_from_public_keys(
            script,
            prover_public_keys,
            n0,
            bits_per_digit_checksum,
            to_alt_stack=False,
        )

        for i in reversed(range(1, n0)):
            script.extend(["OP_FROMALTSTACK", i + 1, "OP_ROLL", "OP_EQUALVERIFY"])
        script.extend(["OP_FROMALTSTACK", "OP_EQUALVERIFY"])
