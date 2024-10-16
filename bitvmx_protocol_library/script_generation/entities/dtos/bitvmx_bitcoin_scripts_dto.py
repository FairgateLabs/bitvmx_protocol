import json
from typing import Dict, List

from bitcoinutils.keys import P2trAddress, PublicKey
from pydantic import BaseModel, ConfigDict, Field, field_serializer

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
    input_equivocation_challenge_scripts: BitcoinScriptList
    constants_equivocation_challenge_scripts: BitcoinScriptList
    cached_trigger_challenge_address: Dict[str, str] = Field(default_factory=dict)
    hash_read_search_scripts: List[BitcoinScript]
    choice_read_search_scripts: List[BitcoinScript]
    read_trace_script: BitcoinScript
    trigger_read_challenge_scripts: BitcoinScriptList
    cached_trigger_read_challenge_address: Dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        for field_name, field_type in self.__annotations__.items():
            if field_type == BitcoinScript:
                if not isinstance(data[field_name], BitcoinScript):
                    data[field_name] = BitcoinScript(json.loads(data[field_name]))
            elif field_type == List[BitcoinScript]:
                if not isinstance(data[field_name], list) or not all(
                    isinstance(item, BitcoinScript) for item in data[field_name]
                ):
                    data[field_name] = list(
                        map(
                            lambda elem: BitcoinScript(json.loads(elem)),
                            json.loads(data[field_name]),
                        )
                    )
            elif field_type == BitcoinScriptList:
                if not isinstance(data[field_name], BitcoinScriptList):
                    data[field_name] = BitcoinScriptList(
                        list(
                            map(
                                lambda elem: BitcoinScript(json.loads(elem)),
                                json.loads(data[field_name]),
                            )
                        )
                    )
            elif field_type == BitVMXExecutionScriptList:
                if not isinstance(data[field_name], BitVMXExecutionScriptList):
                    data[field_name] = BitVMXExecutionScriptList(**data[field_name])
            elif field_type == BitVMXWrongHashScriptList:
                if not isinstance(data[field_name], BitVMXWrongHashScriptList):
                    data[field_name] = BitVMXWrongHashScriptList(**data[field_name])
            elif field_type == Dict[str, str]:
                pass
            else:
                raise TypeError(f"Unexpected type {field_type} for field {field_name}")
        super().__init__(**data)

    @property
    def trigger_challenge_scripts_list(self) -> BitcoinScriptList:
        return (
            self.trigger_challenge_scripts
            + self.wrong_hash_challenge_script_list.script_list()
            + BitcoinScriptList(self.choice_read_search_scripts[0])
        )

    def trigger_challenge_address(self, destroyed_public_key: PublicKey) -> P2trAddress:
        if destroyed_public_key.to_hex() in self.cached_trigger_challenge_address:
            return P2trAddress(self.cached_trigger_challenge_address[destroyed_public_key.to_hex()])
        trigger_challenge_address = self.trigger_challenge_scripts_list.get_taproot_address(
            public_key=destroyed_public_key
        )
        self.cached_trigger_challenge_address[destroyed_public_key.to_hex()] = (
            trigger_challenge_address.to_string()
        )
        return trigger_challenge_address

    @property
    def trigger_read_challenge_scripts_list(self) -> BitcoinScriptList:
        return self.trigger_read_challenge_scripts

    def trigger_read_challenge_address(self, destroyed_public_key: PublicKey) -> P2trAddress:
        if destroyed_public_key.to_hex() in self.cached_trigger_read_challenge_address:
            return P2trAddress(
                self.cached_trigger_read_challenge_address[destroyed_public_key.to_hex()]
            )
        trigger_read_challenge_address = (
            self.trigger_read_challenge_scripts_list.get_taproot_address(
                public_key=destroyed_public_key
            )
        )
        self.cached_trigger_read_challenge_address[destroyed_public_key.to_hex()] = (
            trigger_read_challenge_address.to_string()
        )
        return trigger_read_challenge_address

    def choice_read_search_scripts_address(
        self, destroyed_public_key: PublicKey, iteration: int
    ) -> P2trAddress:
        assert iteration > 0
        return self.choice_read_search_script_list(iteration=iteration).get_taproot_address(
            destroyed_public_key
        )

    def choice_read_search_script_index(self) -> int:
        return 0

    def choice_read_search_script_list(self, iteration: int) -> BitcoinScriptList:
        return BitcoinScriptList(self.choice_read_search_scripts[iteration])

    def trigger_challenge_taptree(self):
        return self.trigger_challenge_scripts_list.to_scripts_tree()

    def trigger_read_challenge_taptree(self):
        return self.trigger_read_challenge_scripts_list.to_scripts_tree()

    def trigger_challenge_index(self, index: int) -> int:
        return index

    def trigger_wrong_hash_challenge_index(self, choice: int) -> int:
        return len(
            self.trigger_challenge_scripts
        ) + self.wrong_hash_challenge_script_list.list_index_from_choice(choice=choice)

    def trigger_read_wrong_hash_challenge_index(self, choice: int):
        return self.wrong_hash_challenge_script_list.list_index_from_choice(choice=choice)

    def trigger_read_search_challenge_index(self) -> int:
        return len(self.trigger_challenge_scripts) + len(self.wrong_hash_challenge_script_list)

    @staticmethod
    def bitcoin_script_to_str(script: BitcoinScript) -> str:
        return json.dumps(script.script)

    @field_serializer("hash_result_script", when_used="always")
    def serialize_hash_result_script(hash_result_script: BitcoinScript) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=hash_result_script)

    @field_serializer("trigger_protocol_script", when_used="always")
    def serialize_trigger_protocol_script(trigger_protocol_script: BitcoinScript) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=trigger_protocol_script)

    @field_serializer("trace_script", when_used="always")
    def serialize_trace_script(trace_script: BitcoinScript) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=trace_script)

    @field_serializer("hash_search_scripts", when_used="always")
    def serialize_hash_search_scripts(hash_search_scripts: List[BitcoinScript]) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    hash_search_scripts,
                )
            )
        )

    @field_serializer("choice_search_scripts", when_used="always")
    def serialize_choice_search_scripts(choice_search_scripts: List[BitcoinScript]) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    choice_search_scripts,
                )
            )
        )

    @field_serializer("trigger_challenge_scripts", when_used="always")
    def serialize_trigger_challenge_scripts(trigger_challenge_scripts: BitcoinScriptList) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    trigger_challenge_scripts.script_list,
                )
            )
        )

    @field_serializer("input_equivocation_challenge_scripts", when_used="always")
    def serialize_input_equivocation_challenge_scripts(
        input_equivocation_challenge_scripts: BitcoinScriptList,
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    input_equivocation_challenge_scripts.script_list,
                )
            )
        )

    @field_serializer("constants_equivocation_challenge_scripts", when_used="always")
    def serialize_constants_equivocation_challenge_scripts(
        constants_equivocation_challenge_scripts: BitcoinScriptList,
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    constants_equivocation_challenge_scripts.script_list,
                )
            )
        )

    @field_serializer("hash_read_search_scripts", when_used="always")
    def serialize_hash_read_search_scripts(hash_read_search_scripts: List[BitcoinScript]) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    hash_read_search_scripts,
                )
            )
        )

    @field_serializer("choice_read_search_scripts", when_used="always")
    def serialize_choice_read_search_scripts(
        choice_read_search_scripts: List[BitcoinScript],
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    choice_read_search_scripts,
                )
            )
        )

    @field_serializer("read_trace_script", when_used="always")
    def serialize_read_trace_script(read_trace_script: BitcoinScript) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=read_trace_script)

    @field_serializer("trigger_read_challenge_scripts", when_used="always")
    def serialize_trigger_read_challenge_scripts(
        trigger_read_challenge_scripts: BitcoinScriptList,
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    trigger_read_challenge_scripts.script_list,
                )
            )
        )
