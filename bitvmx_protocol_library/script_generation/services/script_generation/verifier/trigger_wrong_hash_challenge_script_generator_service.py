from typing import List

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

        # Correct hash (previous step)
        self._add_hash_to_stack(
            script=script,
            choice_array=[0, 3, 3, 2, 1],
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
