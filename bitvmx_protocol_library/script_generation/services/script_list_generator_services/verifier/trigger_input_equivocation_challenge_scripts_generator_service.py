from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)


class TriggerInputEquivocationChallengeScriptsGeneratorService:
    def __init__(self):
        pass

    def __call__(self) -> BitcoinScriptList:
        dummy_script = BitcoinScript()
        dummy_script.append(1)
        return BitcoinScriptList(dummy_script)
