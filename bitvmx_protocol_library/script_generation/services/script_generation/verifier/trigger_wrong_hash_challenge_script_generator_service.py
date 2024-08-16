from typing import List

import pybitvmbinding
from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
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

    def __call__(self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO):
        script = BitcoinScript()
        script.extend(
            [
                PublicKey(
                    hex_str=bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
                ).to_x_only_hex(),
                "OP_CHECKSIGVERIFY",
            ]
        )

        # Wrong hash (chosen step)
        self._add_hash_to_stack(
            script=script,
            choice_array=[0, 3, 3, 2, 2],
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )
        for i in range(4):
            self.verify_input_nibble_message_from_public_keys(
                script,
                bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
                    i
                ],
                trace_words_lengths[i],
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
                to_alt_stack=True,
            )

        # Correct hash (previous step)
        self._add_hash_to_stack(
            script=script,
            choice_array=[0, 3, 3, 2, 1],
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        amount_of_input_hash_nibbles_hash = 64
        for _ in range(amount_of_input_hash_nibbles_hash):
            script.append("OP_FROMALTSTACK")
        for i in range(1, amount_of_input_hash_nibbles_hash):
            script.extend([i, "OP_ROLL"])
        # script.extend([0, "OP_PICK", int("8", 16), "OP_EQUALVERIFY"])
        # script.extend([1, "OP_PICK", int("d", 16), "OP_EQUALVERIFY"])
        # script.extend([2, "OP_PICK", int("2", 16), "OP_EQUALVERIFY"])
        # script.extend([3, "OP_PICK", int("8", 16), "OP_EQUALVERIFY"])
        # script.extend([4, "OP_PICK", int("d", 16), "OP_EQUALVERIFY"])
        amount_of_input_hash_nibbles_trace = 8 + 8 + 8 + 2
        for _ in range(amount_of_input_hash_nibbles_trace):
            script.append("OP_FROMALTSTACK")
        amount_of_input_hash_nibbles = (
            amount_of_input_hash_nibbles_hash + amount_of_input_hash_nibbles_trace
        )
        # script.extend([0, "OP_PICK", 0, "OP_EQUALVERIFY"])
        # script.extend([1, "OP_PICK", 0, "OP_EQUALVERIFY"])
        # script.extend([2, "OP_PICK", 4, "OP_EQUALVERIFY"])
        # script.extend([3, "OP_PICK", 8, "OP_EQUALVERIFY"])
        # script.extend([4, "OP_PICK", 3, "OP_EQUALVERIFY"])
        sha_256_script_int_opcodes = pybitvmbinding.sha_256_script(
            int(amount_of_input_hash_nibbles / 2)
        )
        sha_256_script = BitcoinScript.from_int_list(sha_256_script_int_opcodes)
        script += sha_256_script
        # nibbles_to_verify = [int("0f", 16), int("0a", 16), int("02", 16), int("01", 16)]
        # for i in range(len(nibbles_to_verify)):
        #     script.append(nibbles_to_verify[i])
        #     script.append("OP_EQUALVERIFY")
        for _ in range(64):
            script.append("OP_FROMALTSTACK")
            script.append("OP_EQUALVERIFY")
        script.append(1)
        return script

    def _add_hash_to_stack(
        self,
        script: BitcoinScript,
        choice_array: List[int],
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):
        binary_choice_array = list(
            map(
                lambda x: bin(x)[2:].zfill(
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                ),
                choice_array,
            )
        )
        wrong_hash_step_iteration = len(choice_array) - 1
        while binary_choice_array[wrong_hash_step_iteration] == "11":
            wrong_hash_step_iteration -= 1
        wrong_hash_index = int(binary_choice_array[wrong_hash_step_iteration], 2)
        current_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[
            wrong_hash_step_iteration
        ][
            wrong_hash_index
        ]
        self.verify_input_nibble_message_from_public_keys(
            script,
            current_public_keys,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            to_alt_stack=True,
        )
