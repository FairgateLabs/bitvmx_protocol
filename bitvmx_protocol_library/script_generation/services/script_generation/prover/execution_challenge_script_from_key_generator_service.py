from typing import Dict, List

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


class ExecutionChallengeScriptFromKeyGeneratorService:

    def __call__(
        self,
        key: str,
        signature_public_keys: List[str],
        public_keys: List[List[str]],
        trace_words_lengths: List[int],
        bits_per_digit_checksum: int,
        instruction_dict: Dict[str, str],
        opcode_dict: Dict[str, str],
        trace_to_script_mapping: List[int],
    ):
        script = BitcoinScript()
        trace_to_script_mapping = reversed(trace_to_script_mapping)
        max_value = 12
        complementary_trace_to_script_mapping = list(
            map(lambda index: max_value - index, trace_to_script_mapping)
        )

        verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()

        for i in complementary_trace_to_script_mapping:
            if (
                len(trace_words_lengths) - i - 1
                == BitVMXProtocolPropertiesDTO.read_pc_opcode_position
            ):
                verify_input_nibble_message_from_public_keys(
                    script,
                    public_keys[i],
                    trace_words_lengths[i],
                    bits_per_digit_checksum,
                    to_alt_stack=False,
                )
                current_opcode = opcode_dict[key]
                for letter in reversed(current_opcode):
                    script.extend(["OP_DUP", int(letter, 16), "OP_EQUALVERIFY", "OP_TOALTSTACK"])
            else:
                verify_input_nibble_message_from_public_keys(
                    script,
                    public_keys[i],
                    trace_words_lengths[i],
                    bits_per_digit_checksum,
                    to_alt_stack=True,
                )

        total_length = 0
        current_micro = key[-2:]
        current_pc_address = key[:-2]
        for i in reversed(complementary_trace_to_script_mapping):
            current_length = trace_words_lengths[i]
            for j in range(current_length):
                script.append("OP_FROMALTSTACK")

                # MICRO CHECK
                if i == 5:
                    script.extend(["OP_DUP", int(current_micro, 16), "OP_NUMEQUALVERIFY"])

                # PC ADDRESS CHECK
                if i == 6:
                    script.extend(["OP_DUP", int(current_pc_address[j], 16), "OP_NUMEQUALVERIFY"])

            if current_length == 2:
                script.extend([1, "OP_ROLL", "OP_DROP"])
                total_length += 1
            else:
                total_length += current_length

        execution_script = BitcoinScript.from_raw(
            scriptrawhex=instruction_dict[key], has_segwit=True
        )

        script = script + execution_script

        script.extend(
            [PublicKey(hex_str=signature_public_keys[-1]).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        )

        script.append(1)
        return script
