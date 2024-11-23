from abc import abstractmethod
from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class GenericTriggerWrongInitValueScriptGeneratorService:
    def __init__(self):
        pass

    def __call__(self, signature_public_keys: List[str]):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )
        return script

    @property
    @abstractmethod
    def _trace_last_step_index(self):
        pass

    @property
    @abstractmethod
    def _trace_address_index(self):
        pass

    @property
    @abstractmethod
    def _trace_value_index(self):
        pass


class TriggerWrongInitValue1ScriptGeneratorService(
    GenericTriggerWrongInitValueScriptGeneratorService
):
    @property
    def _trace_last_step_index(self):
        return BitVMXProtocolPropertiesDTO.read_1_last_step_position

    @property
    @abstractmethod
    def _trace_address_index(self):
        return BitVMXProtocolPropertiesDTO.read_1_address_position

    @property
    @abstractmethod
    def _trace_value_index(self):
        return BitVMXProtocolPropertiesDTO.read_1_value_position


class TriggerWrongInitValue2ScriptGeneratorService(
    GenericTriggerWrongInitValueScriptGeneratorService
):
    @property
    def _trace_last_step_index(self):
        return BitVMXProtocolPropertiesDTO.read_2_last_step_position

    @property
    @abstractmethod
    def _trace_address_index(self):
        return BitVMXProtocolPropertiesDTO.read_2_address_position

    @property
    @abstractmethod
    def _trace_value_index(self):
        return BitVMXProtocolPropertiesDTO.read_2_value_position
