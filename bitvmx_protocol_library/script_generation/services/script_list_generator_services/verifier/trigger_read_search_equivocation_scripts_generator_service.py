from typing import List

from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_read_search_equivocation_script_generator_service import (
    TriggerReadSearchEquivocationScriptGeneratorService,
)


class TriggerReadSearchEquivocationScriptsGeneratorService:
    def __init__(self):
        self.trigger_read_search_equivocation_script_generator_service = (
            TriggerReadSearchEquivocationScriptGeneratorService()
        )

    def __call__(
        self,
        signature_public_keys: List[str],
        hash_search_prover_public_keys_list: List[List[List[str]]],
        hash_read_search_prover_public_keys_list: List[List[List[str]]],
        amount_of_nibbles_hash: int,
        choice_search_prover_public_keys_list: List[List[List[str]]],
        choice_read_search_prover_public_keys_list: List[List[List[str]]],
        amount_of_bits_wrong_step_search: int,
        bits_per_digit_checksum: int,
    ):
        trigger_read_search_equivocation_scripts_list = []
        for i in range(1, len(hash_search_prover_public_keys_list)):
            current_script = self.trigger_read_search_equivocation_script_generator_service(
                signature_public_keys=signature_public_keys,
                hash_search_prover_public_keys=hash_search_prover_public_keys_list[i],
                hash_read_search_prover_public_keys=hash_read_search_prover_public_keys_list[i - 1],
                amount_of_nibbles_hash=amount_of_nibbles_hash,
                choice_search_prover_public_keys=choice_search_prover_public_keys_list[:i],
                choice_read_search_prover_public_keys=choice_read_search_prover_public_keys_list[
                    :i
                ],
                amount_of_bits_wrong_step_search=amount_of_bits_wrong_step_search,
                bits_per_digit_checksum=bits_per_digit_checksum,
            )
            trigger_read_search_equivocation_scripts_list.append(current_script)
        return trigger_read_search_equivocation_scripts_list
