from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_service import (
    VerifyDigitSignatureService,
)


class CommitSearchChoiceScriptGeneratorService:
    def __init__(self):
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureService()

    def __call__(self, public_keys, amount_of_bits):
        script = BitcoinScript()

        # script.extend(
        #     [third_public_key_alice.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        # )
        # script.extend(
        #     [third_public_key_bob.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        # )

        self.verify_input_single_word_from_public_keys(
            script,
            public_keys,
            amount_of_bits,
            to_alt_stack=True
        )
        script.append(1)
        return script
