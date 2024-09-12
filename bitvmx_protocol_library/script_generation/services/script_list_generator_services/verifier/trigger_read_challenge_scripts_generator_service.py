from typing import List

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)


class TriggerReadChallengeScriptsGeneratorService:

    def __init__(self):
        pass

    def __call__(
        self,
        signature_public_keys: List[str],
        write_trace_words_lengths: List[int],
        read_trace_prover_public_keys: List[List[str]],
        amount_of_bits_wrong_step_search: int,
        hash_read_search_public_keys_list: List[List[List[str]]],
        choice_read_search_prover_public_keys_list: List[List[List[str]]],
        amount_of_nibbles_hash: int,
        amount_of_bits_per_digit_checksum: int,
    ) -> BitcoinScriptList:
        hash_challenge_script = BitcoinScript()
        hash_challenge_script.append(1)

        equality_last_step_1_challenge_script = BitcoinScript()
        equality_last_step_1_challenge_script.append(1)

        equality_more_recent_last_step_1_challenge_script = BitcoinScript()
        equality_more_recent_last_step_1_challenge_script.append(1)

        equality_last_step_2_challenge_script = BitcoinScript()
        equality_last_step_2_challenge_script.append(1)

        equality_more_recent_last_step_2_challenge_script = BitcoinScript()
        equality_more_recent_last_step_2_challenge_script.append(1)

        return BitcoinScriptList(
            [
                hash_challenge_script,
                equality_last_step_1_challenge_script,
                equality_more_recent_last_step_1_challenge_script,
                equality_last_step_2_challenge_script,
                equality_more_recent_last_step_2_challenge_script,
            ]
        )
