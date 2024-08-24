from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.confirm_nibbles_script_generator_service import (
    ConfirmNibblesScriptGeneratorService,
)


class TriggerGenericChallengeScriptGeneratorService:
    def __init__(self):
        self.confirm_nibbles_script_generator_service = ConfirmNibblesScriptGeneratorService()

    def __call__(
        self,
        prover_trace_public_keys,
        verifier_trace_public_keys,
        signature_public_keys,
        trace_words_lengths,
        bits_per_digit_checksum,
    ):

        script = BitcoinScript()

        assert len(prover_trace_public_keys) == len(verifier_trace_public_keys)
        assert len(prover_trace_public_keys) == len(trace_words_lengths)
        for i in range(len(prover_trace_public_keys)):
            self.confirm_nibbles_script_generator_service(
                script,
                prover_trace_public_keys[i],
                verifier_trace_public_keys[i],
                trace_words_lengths[i],
                bits_per_digit_checksum,
            )

        # script.append("OP_CODESEPARATOR")

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return script
