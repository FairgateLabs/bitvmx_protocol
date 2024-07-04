from bitcoinutils.keys import PublicKey

from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


class HashResultScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibbles_message_from_public_keys = VerifyDigitSignatureNibblesService()

    def __call__(self, signature_public_keys, public_keys, n0, bits_per_digit_checksum):
        script = BitcoinScript()

        self.verify_input_nibbles_message_from_public_keys(
            script,
            public_keys,
            n0,
            bits_per_digit_checksum,
            to_alt_stack=True,
        )

        # script.append("OP_CODESEPARATOR")

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return script
