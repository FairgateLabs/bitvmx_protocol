from winternitz_keys_handling.scripts.verify_digit_signature_single_word_service import (
    VerifyDigitSignatureSingleWordService,
)


class ConfirmSingleWordScriptGeneratorService:

    def __init__(self):
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()

    def __call__(
        self, script, amount_of_bits_choice, prover_choice_public_keys, verifier_choice_public_keys
    ):
        self.verify_input_single_word_from_public_keys(
            script, prover_choice_public_keys, amount_of_bits_choice, to_alt_stack=True
        )
        self.verify_input_single_word_from_public_keys(
            script, verifier_choice_public_keys, amount_of_bits_choice, to_alt_stack=False
        )
        script.extend(["OP_FROMALTSTACK", "OP_EQUALVERIFY"])
