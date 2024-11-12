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

        words_lengths = [2, 3, 3]
        for word_length in words_lengths:
            for i in range(word_length - 1, -1, -1):
                script.append("OP_FROMALTSTACK")
                for _ in range(i * 4):
                    script.extend(["OP_DUP", "OP_ADD"])
                if i < word_length - 1:
                    script.append("OP_ADD")

        amount_of_published_bits = amount_of_bits_wrong_step_search * len(
            choice_read_search_prover_public_keys_list
        )

        amount_of_remaining_bits = amount_of_published_bits

        script.append(0)
        while amount_of_remaining_bits > 24:
            script.append("OP_FROMALTSTACK")
            amount_of_remaining_bits -= amount_of_bits_wrong_step_search
            for _ in range(amount_of_remaining_bits - 24):
                script.extend(["OP_DUP", "OP_ADD"])
            script.append("OP_ADD")

        script.append(0)
        while amount_of_remaining_bits > 12:
            script.append("OP_FROMALTSTACK")
            amount_of_remaining_bits -= amount_of_bits_wrong_step_search
            for _ in range(amount_of_remaining_bits - 12):
                script.extend(["OP_DUP", "OP_ADD"])
            script.append("OP_ADD")

        script.append(0)
        while amount_of_remaining_bits > 0:
            script.append("OP_FROMALTSTACK")
            amount_of_remaining_bits -= amount_of_bits_wrong_step_search
            for _ in range(amount_of_remaining_bits):
                script.extend(["OP_DUP", "OP_ADD"])
            script.append("OP_ADD")

        for i in range(3, 1, -1):
            script.append(i)
            script.append("OP_ROLL")
            script.append("OP_EQUALVERIFY")
        script.append("OP_EQUALVERIFY")

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
            to_alt_stack=False,
        )

        script.append(0)
        amount_of_value_nibbles = read_trace_words_lengths[-read_trace_value_index - 1]
        for i in range(amount_of_value_nibbles):
            script.append(amount_of_value_nibbles - i)
            script.append("OP_ROLL")
            script.append("OP_FROMALTSTACK")
            script.append("OP_EQUAL")
            script.append("OP_ADD")

        script.append("OP_TOALTSTACK")

        read_trace_address_index = BitVMXProtocolPropertiesDTO.read_write_address_position

        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=read_trace_prover_public_keys[-read_trace_address_index - 1],
            n0=read_trace_words_lengths[-read_trace_address_index - 1],
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            to_alt_stack=False,
        )

        script.append("OP_FROMALTSTACK")

        amount_of_address_nibbles = read_trace_words_lengths[-read_trace_address_index - 1]
        for i in range(amount_of_address_nibbles):
            script.append(amount_of_address_nibbles - i)
            script.append("OP_ROLL")
            script.append("OP_FROMALTSTACK")
            script.append("OP_EQUAL")
            script.append("OP_ADD")

        script.append(amount_of_address_nibbles + amount_of_value_nibbles)
        script.append("OP_LESSTHAN")
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
