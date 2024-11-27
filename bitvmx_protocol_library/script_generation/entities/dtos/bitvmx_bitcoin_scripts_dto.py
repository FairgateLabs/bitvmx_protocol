import json
from typing import Dict, List

from bitcoinutils.keys import P2trAddress, PublicKey
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.input_and_constant_addresses_generation_service import (
    InputAndConstantAddressesGenerationService,
)
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
    BitVMXLastHashEquivocationScriptList,
    BitVMXWrongHashScriptList,
    BitVMXWrongProgramCounterScriptList,
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
    last_hash_equivocation_script_list: BitVMXLastHashEquivocationScriptList
    wrong_program_counter_challenge_scripts_list: BitVMXWrongProgramCounterScriptList
    input_1_equivocation_challenge_scripts: BitcoinScriptList
    input_2_equivocation_challenge_scripts: BitcoinScriptList
    constants_1_equivocation_challenge_scripts: BitcoinScriptList
    constants_2_equivocation_challenge_scripts: BitcoinScriptList
    wrong_init_value_1_challenge_script: BitcoinScript
    wrong_init_value_2_challenge_script: BitcoinScript
    cached_trigger_trace_challenge_address: Dict[str, str] = Field(default_factory=dict)
    hash_read_search_scripts: List[BitcoinScript]
    choice_read_search_scripts: List[BitcoinScript]
    trigger_read_search_equivocation_scripts: List[BitcoinScript]
    read_trace_script: BitcoinScript
    trigger_wrong_trace_step_script: BitcoinScript
    trigger_wrong_read_trace_step_script: BitcoinScript
    trigger_read_wrong_hash_challenge_scripts: BitVMXWrongHashScriptList
    trigger_wrong_value_address_read_1_challenge_script: BitcoinScript
    trigger_wrong_value_address_read_2_challenge_script: BitcoinScript
    trigger_wrong_latter_step_1_challenge_script: BitcoinScript
    trigger_wrong_latter_step_2_challenge_script: BitcoinScript
    trigger_wrong_halt_step_challenge_script: BitcoinScript
    trigger_no_halt_in_halt_step_challenge_script: BitcoinScript
    prover_timeout_script: BitcoinScript
    verifier_timeout_script: BitcoinScript
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
            elif field_type == BitVMXWrongProgramCounterScriptList:
                if not isinstance(data[field_name], BitVMXWrongProgramCounterScriptList):
                    data[field_name] = BitVMXWrongProgramCounterScriptList(**data[field_name])
            elif field_type == BitVMXLastHashEquivocationScriptList:
                if not isinstance(data[field_name], BitVMXLastHashEquivocationScriptList):
                    data[field_name] = BitVMXLastHashEquivocationScriptList(**data[field_name])
            elif field_type == Dict[str, str]:
                pass
            else:
                raise TypeError(f"Unexpected type {field_type} for field {field_name}")
        super().__init__(**data)

    def hash_search_scripts_list(self, iteration: int) -> BitcoinScriptList:
        return BitcoinScriptList([self.hash_search_scripts[iteration], self.prover_timeout_script])

    @staticmethod
    def hash_search_script_index():
        return 0

    def choice_search_scripts_list(self, iteration: int) -> BitcoinScriptList:
        return BitcoinScriptList(
            [self.choice_search_scripts[iteration], self.verifier_timeout_script]
        )

    @staticmethod
    def choice_search_script_index():
        return 0

    def hash_read_search_scripts_list(self, iteration: int) -> BitcoinScriptList:
        return BitcoinScriptList(
            [self.hash_read_search_scripts[iteration], self.prover_timeout_script]
        )

    @staticmethod
    def hash_read_search_script_index():
        return 0

    @property
    def trigger_trace_challenge_scripts_list(self) -> BitcoinScriptList:
        return (
            self.trigger_challenge_scripts
            + self.wrong_hash_challenge_script_list.script_list()
            + self.wrong_program_counter_challenge_scripts_list.script_list()
            + BitcoinScriptList(self.choice_read_search_scripts[0])
            + self.input_1_equivocation_challenge_scripts
            + self.input_2_equivocation_challenge_scripts
            + self.constants_1_equivocation_challenge_scripts
            + self.constants_2_equivocation_challenge_scripts
            + BitcoinScriptList(self.trigger_wrong_halt_step_challenge_script)
            + BitcoinScriptList(self.trigger_no_halt_in_halt_step_challenge_script)
            + self.last_hash_equivocation_script_list.script_list()
            + self.wrong_init_value_1_challenge_script
            + self.wrong_init_value_2_challenge_script
            + self.verifier_timeout_script
        )

    @property
    def trigger_protocol_scripts_list(self) -> BitcoinScriptList:
        return BitcoinScriptList([self.trigger_protocol_script, self.verifier_timeout_script])

    @staticmethod
    def trigger_protocol_index() -> int:
        return 0

    @property
    def trace_script_list(self) -> BitcoinScriptList:
        return BitcoinScriptList(
            [self.trace_script, self.trigger_wrong_trace_step_script, self.prover_timeout_script]
        )

    @staticmethod
    def trace_script_index() -> int:
        return 0

    @staticmethod
    def trigger_wrong_trace_step_index() -> int:
        return 1

    @property
    def read_trace_script_list(self) -> BitcoinScriptList:
        return BitcoinScriptList(
            [
                self.read_trace_script,
                self.trigger_wrong_read_trace_step_script,
                self.prover_timeout_script,
            ]
        )

    @staticmethod
    def read_trace_script_index() -> int:
        return 0

    @staticmethod
    def trigger_wrong_read_trace_step_index() -> int:
        return 1

    def trigger_trace_challenge_address(self, destroyed_public_key: PublicKey) -> P2trAddress:
        if destroyed_public_key.to_hex() in self.cached_trigger_trace_challenge_address:
            return P2trAddress(
                self.cached_trigger_trace_challenge_address[destroyed_public_key.to_hex()]
            )
        trigger_trace_challenge_address = (
            self.trigger_trace_challenge_scripts_list.get_taproot_address(
                public_key=destroyed_public_key
            )
        )
        self.cached_trigger_trace_challenge_address[destroyed_public_key.to_hex()] = (
            trigger_trace_challenge_address.to_string()
        )
        return trigger_trace_challenge_address

    @property
    def trigger_read_challenge_scripts_list(self) -> BitcoinScriptList:
        return (
            self.trigger_read_wrong_hash_challenge_scripts.script_list()
            + self.trigger_wrong_value_address_read_1_challenge_script
            + self.trigger_wrong_value_address_read_2_challenge_script
            + self.trigger_wrong_latter_step_1_challenge_script
            + self.trigger_wrong_latter_step_2_challenge_script
            + self.verifier_timeout_script
        )

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

    def hash_read_search_scripts_address(
        self, destroyed_public_key: PublicKey, iteration: int
    ) -> P2trAddress:
        assert iteration > 0
        return self.hash_read_search_script_list(iteration=iteration).get_taproot_address(
            destroyed_public_key
        )

    @staticmethod
    def choice_read_search_script_index(iteration: int) -> int:
        assert iteration > 0
        return 0

    @staticmethod
    def trigger_read_search_equivocation_index(iteration: int) -> int:
        assert iteration > 0
        return 1

    def choice_read_search_script_list(self, iteration: int) -> BitcoinScriptList:
        assert iteration > 0
        return BitcoinScriptList(
            [
                self.choice_read_search_scripts[iteration],
                self.trigger_read_search_equivocation_scripts[iteration - 1],
                self.verifier_timeout_script,
            ]
        )

    def hash_read_search_script_list(self, iteration: int) -> BitcoinScriptList:
        assert iteration > 0
        return BitcoinScriptList(
            [
                self.hash_read_search_scripts[iteration - 1],
                self.prover_timeout_script,
            ]
        )

    def trigger_challenge_taptree(self):
        return self.trigger_trace_challenge_scripts_list.to_scripts_tree()

    def trigger_read_challenge_taptree(self):
        return self.trigger_read_challenge_scripts_list.to_scripts_tree()

    @staticmethod
    def trigger_challenge_index(index: int) -> int:
        return index

    def trigger_wrong_hash_challenge_index(self, choice: int) -> int:
        return len(
            self.trigger_challenge_scripts
        ) + self.wrong_hash_challenge_script_list.list_index_from_choice(choice=choice)

    def trigger_wrong_program_counter_challenge_index(self, choice: int) -> int:
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + self.wrong_program_counter_challenge_scripts_list.list_index_from_choice(
                choice=choice
            )
        )

    def trigger_read_search_challenge_index(self) -> int:
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
        )

    @staticmethod
    def _check_input_range(address: str, base_input_address: str, amount_of_input_words: int):
        int_address = int(address, 16)
        int_base_input_address = int(base_input_address, 16)
        if not ((int_address - int_base_input_address) % 4) == 0:
            raise Exception("Input address not aligned with base input address")
        if int_address < int_base_input_address or (
            int_address >= (int_base_input_address + amount_of_input_words * 4)
        ):
            raise Exception("Input address out of input region")

    @staticmethod
    def _get_index_from_address_constant(address: str, amount_of_input_words: int):
        input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        static_addresses = input_and_constant_addresses_generation_service(
            input_length=amount_of_input_words
        )
        addresses = list(sorted(static_addresses.constants.keys()))
        return addresses.index(address)

    @staticmethod
    def get_index_from_address(address: str, base_input_address: str):
        int_address = int(address, 16)
        int_base_input_address = int(base_input_address, 16)
        return int((int_address - int_base_input_address) / 4)

    def trigger_input_1_equivocation_challenge_index(
        self, address: str, base_input_address: str, amount_of_input_words: int
    ) -> int:
        self._check_input_range(
            address=address,
            base_input_address=base_input_address,
            amount_of_input_words=amount_of_input_words,
        )
        index_from_address = self.get_index_from_address(
            address=address, base_input_address=base_input_address
        )
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + index_from_address
        )

    def trigger_input_2_equivocation_challenge_index(
        self, address: str, base_input_address: str, amount_of_input_words: int
    ) -> int:
        self._check_input_range(
            address=address,
            base_input_address=base_input_address,
            amount_of_input_words=amount_of_input_words,
        )
        index_from_address = self.get_index_from_address(
            address=address, base_input_address=base_input_address
        )
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + index_from_address
        )

    def trigger_constant_1_equivocation_challenge_index(
        self, address: str, amount_of_input_words: int
    ) -> int:
        index_from_address = self._get_index_from_address_constant(
            address=address, amount_of_input_words=amount_of_input_words
        )
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + len(self.input_2_equivocation_challenge_scripts)
            + index_from_address
        )

    def trigger_constant_2_equivocation_challenge_index(
        self, address: str, amount_of_input_words: int
    ) -> int:
        index_from_address = self._get_index_from_address_constant(
            address=address, amount_of_input_words=amount_of_input_words
        )
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + len(self.input_2_equivocation_challenge_scripts)
            + len(self.constants_1_equivocation_challenge_scripts)
            + index_from_address
        )

    def trigger_wrong_halt_step_challenge_index(self):
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + len(self.input_2_equivocation_challenge_scripts)
            + len(self.constants_1_equivocation_challenge_scripts)
            + len(self.constants_2_equivocation_challenge_scripts)
        )

    def trigger_no_halt_in_halt_step_challenge_index(self):
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + len(self.input_2_equivocation_challenge_scripts)
            + len(self.constants_1_equivocation_challenge_scripts)
            + len(self.constants_2_equivocation_challenge_scripts)
            + 1
        )

    def trigger_last_hash_equivocation_challenge_index(self, choice: int) -> int:
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + len(self.input_2_equivocation_challenge_scripts)
            + len(self.constants_1_equivocation_challenge_scripts)
            + len(self.constants_2_equivocation_challenge_scripts)
            + 2
        ) + self.last_hash_equivocation_script_list.list_index_from_choice(choice=choice)

    def trigger_wrong_init_value_1_challenge_index(self):
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + len(self.input_2_equivocation_challenge_scripts)
            + len(self.constants_1_equivocation_challenge_scripts)
            + len(self.constants_2_equivocation_challenge_scripts)
            + 2
            + len(self.last_hash_equivocation_script_list)
        )

    def trigger_wrong_init_value_2_challenge_index(self):
        return (
            len(self.trigger_challenge_scripts)
            + len(self.wrong_hash_challenge_script_list)
            + len(self.wrong_program_counter_challenge_scripts_list)
            + 1
            + len(self.input_1_equivocation_challenge_scripts)
            + len(self.input_2_equivocation_challenge_scripts)
            + len(self.constants_1_equivocation_challenge_scripts)
            + len(self.constants_2_equivocation_challenge_scripts)
            + 2
            + len(self.last_hash_equivocation_script_list)
            + 1
        )

    def trigger_read_wrong_hash_challenge_index(self, choice: int):
        return self.trigger_read_wrong_hash_challenge_scripts.list_index_from_choice(choice=choice)

    def trigger_wrong_value_address_read_1_index(self):
        return len(self.trigger_read_wrong_hash_challenge_scripts)

    def trigger_wrong_value_address_read_2_index(self):
        return len(self.trigger_read_wrong_hash_challenge_scripts) + 1

    def trigger_wrong_latter_step_1_index(self):
        return len(self.trigger_read_wrong_hash_challenge_scripts) + 2

    def trigger_wrong_latter_step_2_index(self):
        return len(self.trigger_read_wrong_hash_challenge_scripts) + 3

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

    @field_serializer("input_1_equivocation_challenge_scripts", when_used="always")
    def serialize_input_1_equivocation_challenge_scripts(
        input_1_equivocation_challenge_scripts: BitcoinScriptList,
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    input_1_equivocation_challenge_scripts.script_list,
                )
            )
        )

    @field_serializer("input_2_equivocation_challenge_scripts", when_used="always")
    def serialize_input_2_equivocation_challenge_scripts(
        input_2_equivocation_challenge_scripts: BitcoinScriptList,
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    input_2_equivocation_challenge_scripts.script_list,
                )
            )
        )

    @field_serializer("constants_1_equivocation_challenge_scripts", when_used="always")
    def serialize_constants_1_equivocation_challenge_scripts(
        constants_1_equivocation_challenge_scripts: BitcoinScriptList,
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    constants_1_equivocation_challenge_scripts.script_list,
                )
            )
        )

    @field_serializer("constants_2_equivocation_challenge_scripts", when_used="always")
    def serialize_constants_2_equivocation_challenge_scripts(
        constants_2_equivocation_challenge_scripts: BitcoinScriptList,
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    constants_2_equivocation_challenge_scripts.script_list,
                )
            )
        )

    @field_serializer("wrong_init_value_1_challenge_script", when_used="always")
    def serialize_wrong_init_value_1_challenge_script(
        wrong_init_value_1_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=wrong_init_value_1_challenge_script
        )

    @field_serializer("wrong_init_value_2_challenge_script", when_used="always")
    def serialize_wrong_init_value_2_challenge_script(
        wrong_init_value_2_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=wrong_init_value_2_challenge_script
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

    @field_serializer("trigger_read_search_equivocation_scripts", when_used="always")
    def serialize_trigger_read_search_equivocation_scripts(
        trigger_read_search_equivocation_scripts: List[BitcoinScript],
    ) -> str:
        return json.dumps(
            list(
                map(
                    lambda btc_scr: BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=btc_scr),
                    trigger_read_search_equivocation_scripts,
                )
            )
        )

    @field_serializer("read_trace_script", when_used="always")
    def serialize_read_trace_script(read_trace_script: BitcoinScript) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=read_trace_script)

    @field_serializer("trigger_wrong_value_address_read_1_challenge_script", when_used="always")
    def serialize_trigger_wrong_value_address_read_1_challenge_script(
        trigger_wrong_value_address_read_1_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=trigger_wrong_value_address_read_1_challenge_script
        )

    @field_serializer("trigger_wrong_value_address_read_2_challenge_script", when_used="always")
    def serialize_trigger_wrong_value_address_read_2_challenge_script(
        trigger_wrong_value_address_read_2_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=trigger_wrong_value_address_read_2_challenge_script
        )

    @field_serializer("trigger_wrong_latter_step_1_challenge_script", when_used="always")
    def serialize_trigger_wrong_latter_step_1_challenge_script(
        trigger_wrong_latter_step_1_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=trigger_wrong_latter_step_1_challenge_script
        )

    @field_serializer("trigger_wrong_latter_step_2_challenge_script", when_used="always")
    def serialize_trigger_wrong_latter_step_2_challenge_script(
        trigger_wrong_latter_step_2_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=trigger_wrong_latter_step_2_challenge_script
        )

    @field_serializer("trigger_wrong_halt_step_challenge_script", when_used="always")
    def serialize_trigger_wrong_halt_step_challenge_script(
        trigger_wrong_halt_step_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=trigger_wrong_halt_step_challenge_script
        )

    @field_serializer("trigger_no_halt_in_halt_step_challenge_script", when_used="always")
    def serialize_trigger_no_halt_in_halt_step_challenge_script(
        trigger_no_halt_in_halt_step_challenge_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=trigger_no_halt_in_halt_step_challenge_script
        )

    @field_serializer("trigger_wrong_trace_step_script", when_used="always")
    def serialize_trigger_wrong_trace_step_script(
        trigger_wrong_trace_step_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=trigger_wrong_trace_step_script)

    @field_serializer("trigger_wrong_read_trace_step_script", when_used="always")
    def serialize_trigger_wrong_read_trace_step_script(
        trigger_wrong_read_trace_step_script: BitcoinScript,
    ) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(
            script=trigger_wrong_read_trace_step_script
        )

    @field_serializer("prover_timeout_script", when_used="always")
    def serialize_prover_timeout_script(prover_timeout_script: BitcoinScript) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=prover_timeout_script)

    @field_serializer("verifier_timeout_script", when_used="always")
    def serialize_verifier_timeout_script(verifier_timeout_script: BitcoinScript) -> str:
        return BitVMXBitcoinScriptsDTO.bitcoin_script_to_str(script=verifier_timeout_script)
