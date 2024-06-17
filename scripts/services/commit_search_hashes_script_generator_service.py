from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_nibble_service import VerifyDigitSignatureNibbleService


class CommitSearchHashesScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibbleService()

    def __call__(self, public_keys, n0, bits_per_digit_checksum):
        script = BitcoinScript()

        # third_script.extend(
        #     [third_public_key_alice.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        # )
        # third_script.extend(
        #     [third_public_key_bob.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        # )

        for i in range(len(public_keys)):
            self.verify_input_nibble_message_from_public_keys(
                script,
                public_keys[i],
                n0,
                bits_per_digit_checksum,
                to_alt_stack=True,
            )
        script.append(1)
        return script
