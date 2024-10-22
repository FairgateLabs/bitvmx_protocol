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


class ExecutionTraceScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.confirm_single_word_script_generator_service = (
            ConfirmSingleWordScriptGeneratorService()
        )

    def __call__(
        self,
        signature_public_keys,
        public_keys,
        trace_words_lengths,
        bits_per_digit_checksum,
        amount_of_bits_choice,
        prover_choice_public_keys,
        verifier_choice_public_keys,
    ):
        script = BitcoinScript()

        for i in range(len(public_keys)):
            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=public_keys[i],
                n0=trace_words_lengths[i],
                bits_per_digit_checksum=bits_per_digit_checksum,
                to_alt_stack=True,
            )

        self.confirm_single_word_script_generator_service(
            script=script,
            amount_of_bits_choice=amount_of_bits_choice,
            prover_choice_public_keys=prover_choice_public_keys,
            verifier_choice_public_keys=verifier_choice_public_keys,
        )

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return script
