from bitcoinutils.keys import PublicKey

from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_service import (
    VerifyDigitSignatureService,
)


class CommitSearchChoiceScriptGeneratorService:
    def __init__(self):
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureService()

    def __call__(self, signature_public_keys, public_keys, amount_of_bits):
        script = BitcoinScript()

        self.verify_input_single_word_from_public_keys(
            script, public_keys, amount_of_bits, to_alt_stack=True
        )

        # script.append("OP_CODESEPARATOR")

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return script
