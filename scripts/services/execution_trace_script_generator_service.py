from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_nibble_service import (
    VerifyDigitSignatureNibbleService,
)


class ExecutionTraceScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibbleService()
        # self.verify_input_single_word_from_public_keys = VerifyDigitSignatureService()
        # self.confirm_single_word_script_generator_service = (
        #     ConfirmSingleWordScriptGeneratorService()
        # )

    def __call__(self, public_keys, trace_words_lengths, bits_per_digit_checksum):
        script = BitcoinScript()

        for i in range(len(public_keys)):
            self.verify_input_nibble_message_from_public_keys(
                script,
                public_keys[i],
                trace_words_lengths[i],
                bits_per_digit_checksum,
                to_alt_stack=True,
            )

        script.append(1)
        return script
