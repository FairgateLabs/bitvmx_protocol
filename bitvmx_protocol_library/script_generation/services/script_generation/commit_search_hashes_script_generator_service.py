from typing import List, Optional

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.confirm_single_word_script_generator_service import (
    ConfirmSingleWordScriptGeneratorService,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_single_word_service import (
    VerifyDigitSignatureSingleWordService,
)


class CommitSearchHashesScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()
        self.confirm_single_word_script_generator_service = (
            ConfirmSingleWordScriptGeneratorService()
        )

    def __call__(
        self,
        signature_public_keys,
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

        # script.append("OP_CODESEPARATOR")

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return script
