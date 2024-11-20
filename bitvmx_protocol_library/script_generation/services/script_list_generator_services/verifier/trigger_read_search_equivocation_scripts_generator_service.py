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
        choice_search_prover_public_keys_list: List[List[List[str]]],
        choice_read_search_prover_public_keys_list: List[List[List[str]]],
    ):
        pass
