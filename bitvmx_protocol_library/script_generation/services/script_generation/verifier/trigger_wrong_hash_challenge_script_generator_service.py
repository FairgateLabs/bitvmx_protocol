from typing import List

import pybitvmbinding
from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


class TriggerWrongHashChallengeScriptGeneratorService:
    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()

    def __call__(
        self,
        signature_public_keys: List[str],
        trace_words_lengths: List[int],
        amount_of_bits_wrong_step_search: int,
        hash_search_public_keys_list: List[List[List[str]]],
        trace_prover_public_keys: List[List[str]],
        amount_of_nibbles_hash: int,
        amount_of_bits_per_digit_checksum: int,
        choice: int,
    ):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )

        bin_wrong_choice = bin(choice)[2:]
        wrong_hash_choice_array = [
            bin_wrong_choice[i : i + amount_of_bits_wrong_step_search].zfill(
                amount_of_bits_wrong_step_search
            )
            for i in range(0, len(bin_wrong_choice), amount_of_bits_wrong_step_search)
        ]

        # Wrong hash (chosen step)
        self._add_hash_to_stack(
            script=script,
            binary_choice_array=wrong_hash_choice_array,
            hash_search_public_keys_list=hash_search_public_keys_list,
            amount_of_nibbles_hash=amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

        for i in range(4):
            self.verify_input_nibble_message_from_public_keys(
                script,
                trace_prover_public_keys[i],
                trace_words_lengths[i],
                amount_of_bits_per_digit_checksum,
                to_alt_stack=True,
            )

        bin_correct_choice = bin(choice - 1)[2:]
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
            amount_of_nibbles_hash=amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

        amount_of_input_hash_nibbles_hash = 64
        for _ in range(amount_of_input_hash_nibbles_hash):
            script.append("OP_FROMALTSTACK")
        for i in range(1, amount_of_input_hash_nibbles_hash):
            script.extend([i, "OP_ROLL"])
        amount_of_input_hash_nibbles_trace = 8 + 8 + 8 + 2
        for _ in range(amount_of_input_hash_nibbles_trace):
            script.append("OP_FROMALTSTACK")
        amount_of_input_hash_nibbles = (
            amount_of_input_hash_nibbles_hash + amount_of_input_hash_nibbles_trace
        )
        sha_256_script_int_opcodes = pybitvmbinding.sha_256_script(
            int(amount_of_input_hash_nibbles / 2)
        )
        sha_256_script = BitcoinScript.from_int_list(sha_256_script_int_opcodes)
        script += sha_256_script
        for i in range(64):
            script.append(i)
            script.append("OP_ROLL")
            script.append("OP_FROMALTSTACK")
            script.append("OP_EQUAL")
        for i in range(64 - 1):
            script.append("OP_ADD")
        script.append(64)
        script.append("OP_EQUAL")
        return script

    def _add_hash_to_stack(
        self,
        script: BitcoinScript,
        binary_choice_array: List[str],
        hash_search_public_keys_list: List[List[List[str]]],
        amount_of_nibbles_hash: int,
        amount_of_bits_per_digit_checksum: int,
    ):
        wrong_hash_step_iteration = -1
        while binary_choice_array[wrong_hash_step_iteration] == "1" * len(binary_choice_array[0]):
            wrong_hash_step_iteration -= 1
        # TODO
        # We should add the verification for every choice until different from "11"
        wrong_hash_index = int(binary_choice_array[wrong_hash_step_iteration], 2)
        self.verify_input_nibble_message_from_public_keys(
            script,
            hash_search_public_keys_list[wrong_hash_step_iteration][wrong_hash_index],
            amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )
