from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class TriggerWrongHaltStepChallengeScriptGeneratorService:
    def __call__(
        self,
        signature_public_keys: List[str],
        trace_words_lengths: List[int],
        halt_step_public_keys: List[str],
        choice_search_prover_public_keys_list: List[List[List[str]]],
        trace_prover_public_keys: List[List[str]],
        amount_of_bits_per_digit_checksum: int,
    ):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )
        # script.append("OP_DROP")
        script.append(1)
        return script
