from typing import List

from bitcoinutils.keys import P2trAddress, PublicKey
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
from bitvmx_protocol_library.script_generation.entities.business_objects.bitvmx_wrong_hash_script_list import (
    BitVMXWrongHashScriptList,
)


class BitVMXBitcoinScriptsDTO(BaseModel):
    hash_result_script: BitcoinScript
    trigger_protocol_script: BitcoinScript
    hash_search_scripts: List[BitcoinScript]
    choice_search_scripts: List[BitcoinScript]
    trace_script: BitcoinScript
    trigger_challenge_scripts: BitcoinScriptList
    execution_challenge_script_list: BitVMXExecutionScriptList
    wrong_hash_challenge_script_list: BitVMXWrongHashScriptList

    class Config:
        arbitrary_types_allowed = True

    @property
    def trigger_challenge_scripts_list(self) -> BitcoinScriptList:
        return self.trigger_challenge_scripts + self.wrong_hash_challenge_script_list.script_list()

    def trigger_challenge_address(self, destroyed_public_key: PublicKey) -> P2trAddress:
        return self.trigger_challenge_scripts_list.get_taproot_address(
            public_key=destroyed_public_key
        )

    def trigger_challenge_taptree(self):
        return self.trigger_challenge_scripts_list.to_scripts_tree()

    def trigger_challenge_index(self, index: int) -> int:
        return index

    def trigger_wrong_hash_challenge_index(self, choice: int) -> int:
        return len(
            self.trigger_challenge_scripts
        ) + self.wrong_hash_challenge_script_list.list_index_from_choice(choice=choice)
