from typing import List, Optional

from scripts.bitcoin_script import BitcoinScript
from scripts.services.confirm_single_word_script_generator_service import (
    ConfirmSingleWordScriptGeneratorService,
)
from winternitz_keys_handling.scripts.verify_digit_signature_nibble_service import (
    VerifyDigitSignatureNibbleService,
)
from winternitz_keys_handling.scripts.verify_digit_signature_service import (
    VerifyDigitSignatureService,
)


class CommitSearchHashesScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibbleService()
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureService()
        self.confirm_single_word_script_generator_service = (
            ConfirmSingleWordScriptGeneratorService()
        )

    def __call__(
        self,
        public_keys,
        n0,
        bits_per_digit_checksum,
        amount_of_bits_choice: Optional[int] = None,
        prover_choice_public_keys: Optional[List[str]] = None,
        verifier_choice_public_keys: Optional[List[str]] = None,
    ):
        script = BitcoinScript()

        for i in range(len(public_keys)):
            self.verify_input_nibble_message_from_public_keys(
                script,
                public_keys[i],
                n0,
                bits_per_digit_checksum,
                to_alt_stack=True,
            )
        if (
            amount_of_bits_choice is not None
            and prover_choice_public_keys is not None
            and verifier_choice_public_keys is not None
        ):
            self.confirm_single_word_script_generator_service(
                script,
                amount_of_bits_choice,
                prover_choice_public_keys,
                verifier_choice_public_keys,
            )
        return script
