from typing import List

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_hash_witness_service import (
    GetHashWitnessService,
)


class GetCorrectHashWitnessService:

    def __init__(self):
        self.get_hash_witness_service = GetHashWitnessService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ) -> List[str]:
        binary_choice_array = list(
            map(
                lambda x: bin(x)[2:].zfill(
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                ),
                bitvmx_protocol_verifier_dto.search_choices,
            )
        )
        correct_step_hash = int("".join(binary_choice_array), 2) - 1
        binary_correct_step_hash = bin(correct_step_hash)[2:].zfill(
            len("".join(binary_choice_array))
        )
        search_digit_length = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
        )
        return self.get_hash_witness_service(
            binary_choice_array=[
                binary_correct_step_hash[i : i + search_digit_length]
                for i in range(0, len(binary_correct_step_hash), search_digit_length)
            ],
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )
