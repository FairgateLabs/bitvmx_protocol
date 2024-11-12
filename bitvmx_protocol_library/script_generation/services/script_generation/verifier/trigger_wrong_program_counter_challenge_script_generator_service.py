from typing import List

import pybitvmbinding
from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.initial_program_counter_generation_service import (
    InitialProgramCounterGenerationService,
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


class TriggerWrongProgramCounterChallengeScriptGeneratorService:
    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()
        self.initial_program_counter_generation_service = InitialProgramCounterGenerationService(
            instruction_commitment=ExecutionTraceGenerationService.commitment_file()
        )
        self.cached_sha_scripts = {}

    def __call__(
        self,
        signature_public_keys: List[str],
        trace_words_lengths: List[int],
        amount_of_bits_wrong_step_search: int,
        hash_search_public_keys_list: List[List[List[str]]],
        choice_search_prover_public_keys_list: List[List[List[str]]],
        trace_prover_public_keys: List[List[str]],
        hash_result_public_keys: List[str],
        amount_of_nibbles_hash: int,
        amount_of_bits_per_digit_checksum: int,
        bin_wrong_choice: str,
    ):
        choice = int(bin_wrong_choice, 2)
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )

        wrong_hash_choice_array = [
            bin_wrong_choice[i : i + amount_of_bits_wrong_step_search].zfill(
                amount_of_bits_wrong_step_search
            )
            for i in range(0, len(bin_wrong_choice), amount_of_bits_wrong_step_search)
        ]
        counter = -1
        # Character we need to discard at the end of the array
        if wrong_hash_choice_array[counter] == ("0" * amount_of_bits_wrong_step_search):
            suffix_character = "0"
        else:
            suffix_character = "1"

        if choice == 0:
            for choice_list in reversed(choice_search_prover_public_keys_list):
                self.verify_input_single_word_from_public_keys(
                    script=script,
                    public_keys=choice_list[0],
                    amount_of_bits=amount_of_bits_wrong_step_search,
                    to_alt_stack=False,
                )
                script.append(0)
                script.append("OP_EQUALVERIFY")
        else:
            while -counter <= len(wrong_hash_choice_array):
                self.verify_input_single_word_from_public_keys(
                    script=script,
                    public_keys=choice_search_prover_public_keys_list[counter][0],
                    amount_of_bits=amount_of_bits_wrong_step_search,
                    to_alt_stack=False,
                )
                script.append(int(wrong_hash_choice_array[counter], 2))
                script.append("OP_EQUALVERIFY")
                if wrong_hash_choice_array[counter] != (
                    suffix_character * amount_of_bits_wrong_step_search
                ):
                    break
                counter -= 1

        if choice == 0:
            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=trace_prover_public_keys[0],
                n0=trace_words_lengths[0],
                bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
                to_alt_stack=False,
            )
            script.extend([0, "OP_EQUALVERIFY", 0, "OP_EQUALVERIFY"])

            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=trace_prover_public_keys[1],
                n0=trace_words_lengths[1],
                bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
                to_alt_stack=False,
            )

            initial_program_counter = self.initial_program_counter_generation_service()
            script.append(0)
            for letter in reversed(initial_program_counter):
                script.append(1)
                script.append("OP_ROLL")
                script.append(int(letter, 16))
                script.append("OP_EQUAL")
                script.append("OP_ADD")
            script.append(len(initial_program_counter))
            script.append("OP_LESSTHAN")
        else:
            bin_correct_choice = bin(choice - 1)[2:]
            while len(bin_correct_choice) % amount_of_bits_wrong_step_search != 0:
                bin_correct_choice = "0" + bin_correct_choice
            bin_correct_choice = "0" * amount_of_bits_wrong_step_search + bin_correct_choice
            correct_hash_choice_array = [
                bin_correct_choice[i : i + amount_of_bits_wrong_step_search].zfill(
                    amount_of_bits_wrong_step_search
                )
                for i in range(0, len(bin_correct_choice), amount_of_bits_wrong_step_search)
            ]
            # Correct hash (previous step)
            self._add_hash_to_stack(
                script=script,
                binary_choice_array=correct_hash_choice_array,
                hash_search_public_keys_list=hash_search_public_keys_list,
                hash_result_public_keys=hash_result_public_keys,
                amount_of_nibbles_hash=amount_of_nibbles_hash,
                amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            )

            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=trace_prover_public_keys[0],
                n0=trace_words_lengths[0],
                bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
                to_alt_stack=True,
            )

            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=trace_prover_public_keys[1],
                n0=trace_words_lengths[1],
                bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
                to_alt_stack=True,
            )

            length_to_check = trace_words_lengths[0] + trace_words_lengths[1]
            script.append(0)

            for i in range(length_to_check, 0, -1):
                script.append(i)
                script.append("OP_PICK")
                script.append("OP_FROMALTSTACK")
                script.append("OP_EQUAL")
                script.append("OP_ADD")

            script.append(length_to_check)
            script.append("OP_LESSTHAN")
            script.append("OP_VERIFY")

            amount_of_input_hash_nibbles_trace = 8 + 8 + 8 + 2
            amount_of_input_hash_nibbles = (
                amount_of_nibbles_hash + amount_of_input_hash_nibbles_trace
            )
            current_length = int(amount_of_input_hash_nibbles / 2)
            if current_length in self.cached_sha_scripts:
                sha_256_script = self.cached_sha_scripts[current_length]
            else:
                sha_256_script_int_opcodes = pybitvmbinding.sha_256_script(current_length)
                sha_256_script = BitcoinScript.from_int_list(sha_256_script_int_opcodes)
                self.cached_sha_scripts[current_length] = sha_256_script

            script += sha_256_script

            for i in range(amount_of_nibbles_hash):
                script.append("OP_FROMALTSTACK")
                script.append("OP_EQUALVERIFY")

            script.append(1)

        return script

    def _add_hash_to_stack(
        self,
        script: BitcoinScript,
        binary_choice_array: List[str],
        hash_search_public_keys_list: List[List[List[str]]],
        hash_result_public_keys: List[str],
        amount_of_nibbles_hash: int,
        amount_of_bits_per_digit_checksum: int,
    ):
        wrong_hash_step_iteration = -1
        while -wrong_hash_step_iteration < len(binary_choice_array) and binary_choice_array[
            wrong_hash_step_iteration
        ] == "1" * len(binary_choice_array[0]):
            wrong_hash_step_iteration -= 1
        wrong_hash_index = int(binary_choice_array[wrong_hash_step_iteration], 2)
        if "".join(binary_choice_array) == "1" * len(hash_search_public_keys_list) * len(
            binary_choice_array[0]
        ):
            winternitz_keys = hash_result_public_keys
        else:
            winternitz_keys = hash_search_public_keys_list[wrong_hash_step_iteration][
                wrong_hash_index
            ]
        self.verify_input_nibble_message_from_public_keys(
            script,
            winternitz_keys,
            amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )
