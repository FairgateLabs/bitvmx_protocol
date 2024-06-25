from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_nibble_service import (
    VerifyDigitSignatureNibbleService,
)


class HashResultScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibbleService()

    def __call__(self, signature_public_keys, public_keys, n0, bits_per_digit_checksum):
        script = BitcoinScript()

        for signature_public_key in signature_public_keys:
            script.extend([signature_public_key.to_x_only_hex(), "OP_CHECKSIGVERIFY"])
        # first_script.extend(
        #     [first_public_key_bob.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        # )

        self.verify_input_nibble_message_from_public_keys(
            script,
            public_keys,
            n0,
            bits_per_digit_checksum,
            to_alt_stack=True,
        )
        script.append(1)
        return script
