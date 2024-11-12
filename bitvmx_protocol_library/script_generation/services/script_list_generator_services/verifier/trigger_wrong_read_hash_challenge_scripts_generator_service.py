from typing import List

from bitvmx_protocol_library.script_generation.entities.business_objects.bitvmx_wrong_hash_script_list import (
    BitVMXWrongHashScriptList,
)


class TriggerWrongReadHashChallengeScriptsGeneratorService:

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
    ) -> BitVMXWrongHashScriptList:
        return BitVMXWrongHashScriptList(
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
