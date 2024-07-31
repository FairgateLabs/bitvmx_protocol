from typing import List

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_single_word_service import (
    VerifyDigitSignatureSingleWordService,
)


class ConfirmSingleWordScriptGeneratorService:

    def __init__(self):
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()

    def __call__(
        self,
        script: BitcoinScript,
        amount_of_bits_choice: int,
        prover_choice_public_keys: List[str],
        verifier_choice_public_keys: List[str],
    ):
        self.verify_input_single_word_from_public_keys(
            script, prover_choice_public_keys, amount_of_bits_choice, to_alt_stack=True
        )
        self.verify_input_single_word_from_public_keys(
            script, verifier_choice_public_keys, amount_of_bits_choice, to_alt_stack=False
        )
        script.extend(["OP_FROMALTSTACK", "OP_EQUALVERIFY"])
