from typing import List

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitvmx_wrong_hash_script_list import (
    BitVMXWrongHashScriptList,
)


class TriggerReadChallengeScriptsGeneratorService:

    def __init__(self):
        pass

    def __call__(
        self,
        signature_public_keys: List[str],
        trace_prover_public_keys: List[List[str]],
        read_trace_prover_public_keys: List[List[str]],
        trace_words_lengths: List[int],
        write_trace_words_lengths: List[int],
        amount_of_bits_wrong_step_search: int,
        hash_read_search_public_keys_list: List[List[List[str]]],
        choice_read_search_prover_public_keys_list: List[List[List[str]]],
        hash_result_public_keys: List[str],
        amount_of_nibbles_hash: int,
        amount_of_bits_per_digit_checksum: int,
    ) -> BitcoinScriptList:
        hash_challenge_script_list = BitVMXWrongHashScriptList(
            signature_public_keys=signature_public_keys,
            trace_words_lengths=write_trace_words_lengths,
            amount_of_bits_wrong_step_search=amount_of_bits_wrong_step_search,
            hash_search_public_keys_list=hash_read_search_public_keys_list,
            choice_search_prover_public_keys_list=choice_read_search_prover_public_keys_list,
            trace_prover_public_keys=read_trace_prover_public_keys,
            hash_result_public_keys=hash_result_public_keys,
            amount_of_nibbles_hash=amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

        equality_last_step_1_challenge_script = BitcoinScript()
        equality_last_step_1_challenge_script.append(1)

        equality_more_recent_last_step_1_challenge_script = BitcoinScript()
        equality_more_recent_last_step_1_challenge_script.append(1)

        equality_last_step_2_challenge_script = BitcoinScript()
        equality_last_step_2_challenge_script.append(1)

        equality_more_recent_last_step_2_challenge_script = BitcoinScript()
        equality_more_recent_last_step_2_challenge_script.append(1)

        return hash_challenge_script_list.script_list() + BitcoinScriptList(
            [
                equality_last_step_1_challenge_script,
                equality_more_recent_last_step_1_challenge_script,
                equality_last_step_2_challenge_script,
                equality_more_recent_last_step_2_challenge_script,
            ]
        )
