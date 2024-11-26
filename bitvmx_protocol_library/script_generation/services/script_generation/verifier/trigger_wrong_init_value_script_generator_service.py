from abc import abstractmethod
from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_execution.entities.memory_region_dto import MemoryRegionDTO
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


class GenericTriggerWrongInitValueScriptGeneratorService:
    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()

    def __call__(
        self,
        signature_public_keys: List[str],
        trace_words_lengths: List[int],
        read_only_memory_regions: List[MemoryRegionDTO],
        trace_prover_public_keys: List[List[str]],
        amount_of_bits_per_digit_checksum: int,
    ):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )

        # Last step is FF..FF -> not written
        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=trace_prover_public_keys[-self._trace_last_step_index - 1],
            n0=trace_words_lengths[-self._trace_last_step_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=False,
        )
        script.append(0)
        for i in range(trace_words_lengths[-self._trace_last_step_index - 1]):
            script.append(1)
            script.append("OP_ROLL")
            script.append(int("f", 16))
            script.append("OP_EQUAL")
            script.append("OP_ADD")
        script.append(trace_words_lengths[-self._trace_last_step_index - 1])
        script.append("OP_EQUALVERIFY")

        # Trace value is different from zero
        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=trace_prover_public_keys[-self._trace_value_index - 1],
            n0=trace_words_lengths[-self._trace_value_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=False,
        )
        script.append(0)
        for i in range(trace_words_lengths[-self._trace_value_index - 1]):
            script.append("OP_ADD")
        script.append(0)
        script.append("OP_GREATERTHAN")
        script.append("OP_VERIFY")

        # The address is out of the readonly space
        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=trace_prover_public_keys[-self._trace_address_index - 1],
            n0=trace_words_lengths[-self._trace_address_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )

        words_lengths = [2, 3, 3]
        for word_length in words_lengths:
            for i in range(word_length - 1, -1, -1):
                script.append("OP_FROMALTSTACK")
                for _ in range(i * 4):
                    script.extend(["OP_DUP", "OP_ADD"])
                if i < word_length - 1:
                    script.append("OP_ADD")

        script.append(0)
        script.append("OP_TOALTSTACK")
        for memory_region in read_only_memory_regions:
            script.extend([2, "OP_PICK"])
            script.extend([2, "OP_PICK"])
            script.extend([2, "OP_PICK"])
            self._check_interval(script=script, init=memory_region.init, end=memory_region.end)
            script.append("OP_FROMALTSTACK")
            script.append("OP_ADD")
            script.append("OP_TOALTSTACK")

        script.extend(["OP_2DROP", "OP_DROP"])

        script.append("OP_FROMALTSTACK")
        script.append(0)
        script.append("OP_EQUAL")

        return script

    def _check_greater_or_equal(self, script: BitcoinScript, init: str):
        script.extend([2, "OP_PICK", int(init[0:2], 16), "OP_GREATERTHAN"])

        script.append("OP_IF")

        script.extend(["OP_2DROP", "OP_DROP", 1])

        script.append("OP_ELSE")

        script.extend([2, "OP_ROLL", int(init[0:2], 16), "OP_EQUAL"])

        script.append("OP_IF")

        script.extend([1, "OP_PICK", int(init[2:5], 16), "OP_GREATERTHAN"])

        script.append("OP_IF")

        script.extend(["OP_2DROP", 1])

        script.append("OP_ELSE")

        script.extend([1, "OP_ROLL", int(init[2:5], 16), "OP_EQUAL"])

        script.append("OP_IF")

        script.extend([int(init[5:8], 16), "OP_GREATERTHANOREQUAL"])

        script.append("OP_ELSE")

        script.extend(["OP_DROP", 0])

        script.append("OP_ENDIF")

        script.append("OP_ENDIF")

        script.append("OP_ELSE")

        script.extend(["OP_2DROP", 0])

        script.append("OP_ENDIF")

        script.append("OP_ENDIF")

    def _check_lower_or_equal(self, script: BitcoinScript, end: str):
        script.extend([2, "OP_PICK", int(end[0:2], 16), "OP_LESSTHAN"])

        script.append("OP_IF")

        script.extend(["OP_2DROP", "OP_DROP", 1])

        script.append("OP_ELSE")

        script.extend([2, "OP_ROLL", int(end[0:2], 16), "OP_EQUAL"])

        script.append("OP_IF")

        script.extend([1, "OP_PICK", int(end[2:5], 16), "OP_LESSTHAN"])

        script.append("OP_IF")

        script.extend(["OP_2DROP", 1])

        script.append("OP_ELSE")

        script.extend([1, "OP_ROLL", int(end[2:5], 16), "OP_EQUAL"])

        script.append("OP_IF")

        script.extend([int(end[5:8], 16), "OP_LESSTHANOREQUAL"])

        script.append("OP_ELSE")

        script.extend(["OP_DROP", 0])

        script.append("OP_ENDIF")

        script.append("OP_ENDIF")

        script.append("OP_ELSE")

        script.extend(["OP_2DROP", 0])

        script.append("OP_ENDIF")

        script.append("OP_ENDIF")

    def _check_interval(self, script: BitcoinScript, init: str, end: str):
        self._check_greater_or_equal(script=script, init=init)
        script.append("OP_TOALTSTACK")
        script.extend([2, "OP_PICK"])
        script.extend([2, "OP_PICK"])
        script.extend([2, "OP_PICK"])
        self._check_lower_or_equal(script=script, end=end)
        script.append("OP_FROMALTSTACK")
        script.append("OP_ADD")
        script.append(2)
        script.append("OP_EQUAL")
        script.append("OP_IF")
        script.append(1)
        script.append("OP_ELSE")
        script.append(0)
        script.append("OP_ENDIF")

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
