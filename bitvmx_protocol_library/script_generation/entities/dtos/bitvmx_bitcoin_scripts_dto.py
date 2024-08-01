from typing import List

from pydantic import BaseModel

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitvmx_execution_script_list import (
    BitVMXExecutionScriptList,
)


class BitVMXBitcoinScriptsDTO(BaseModel):
    hash_result_script: BitcoinScript
    trigger_protocol_script: BitcoinScript
    hash_search_scripts: List[BitcoinScript]
    choice_search_scripts: List[BitcoinScript]
    trace_script: BitcoinScript
    trigger_challenge_scripts: BitcoinScriptList
    execution_challenge_script_list: BitVMXExecutionScriptList

    class Config:
        arbitrary_types_allowed = True
