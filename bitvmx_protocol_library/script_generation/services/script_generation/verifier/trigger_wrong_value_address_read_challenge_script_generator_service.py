from abc import abstractmethod
from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_single_word_service import (
    VerifyDigitSignatureSingleWordService,
)


class GenericTriggerWrongValueAddressReadChallengeScriptGeneratorService:

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()

    def __call__(
        self,
        signature_public_keys: List[str],
        trace_words_lengths: List[int],
        read_trace_words_lengths: List[int],
        amount_of_bits_wrong_step_search: int,
        choice_read_search_prover_public_keys_list: List[List[List[str]]],
        trace_prover_public_keys: List[List[str]],
        read_trace_prover_public_keys: List[List[str]],
        amount_of_bits_per_digit_checksum: int,
    ) -> BitcoinScript:
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )
        for choice_list in reversed(choice_read_search_prover_public_keys_list):
            self.verify_input_single_word_from_public_keys(
                script=script,
                public_keys=choice_list[0],
                amount_of_bits=amount_of_bits_wrong_step_search,
                to_alt_stack=True,
            )

        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=trace_prover_public_keys[-self._trace_last_step_index - 1],
            n0=trace_words_lengths[-self._trace_last_step_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )

        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=trace_prover_public_keys[-self._trace_address_index - 1],
            n0=trace_words_lengths[-self._trace_address_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )

        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=trace_prover_public_keys[-self._trace_value_index - 1],
            n0=trace_words_lengths[-self._trace_value_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )

        read_trace_value_index = BitVMXProtocolPropertiesDTO.read_write_value_position

        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=read_trace_prover_public_keys[-read_trace_value_index - 1],
            n0=read_trace_words_lengths[-read_trace_value_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )

        read_trace_address_index = BitVMXProtocolPropertiesDTO.read_write_address_position

        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=read_trace_prover_public_keys[-read_trace_address_index - 1],
            n0=read_trace_words_lengths[-read_trace_address_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )

        script.append(1)
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


class TriggerWrongValueAddressRead1ChallengeScriptGeneratorService(
    GenericTriggerWrongValueAddressReadChallengeScriptGeneratorService
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


class TriggerWrongValueAddressRead2ChallengeScriptGeneratorService(
    GenericTriggerWrongValueAddressReadChallengeScriptGeneratorService
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
