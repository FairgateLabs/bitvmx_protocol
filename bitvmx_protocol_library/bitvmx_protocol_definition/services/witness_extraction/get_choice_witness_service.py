from typing import List

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class GetChoiceWitnessService:

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ) -> List[str]:
        choice_witness = []
        amount_of_bits_wrong_step_search = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
        )
        bin_wrong_choice = bin(bitvmx_protocol_verifier_dto.first_wrong_step)[2:].zfill(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
            * bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
        )
        wrong_hash_choice_array = [
            bin_wrong_choice[i : i + amount_of_bits_wrong_step_search].zfill(
                amount_of_bits_wrong_step_search
            )
            for i in range(0, len(bin_wrong_choice), amount_of_bits_wrong_step_search)
        ]
        counter = -1
        if wrong_hash_choice_array[-1] == "0" * amount_of_bits_wrong_step_search:
            suffix_character = "0"
        else:
            suffix_character = "1"
        while -counter <= len(wrong_hash_choice_array):
            if counter == -1:
                # Trace case
                trace_tx = transaction_info_service(
                    tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.get_txid()
                )
                previous_witness = trace_tx.inputs[0].witness
                while len(previous_witness[0]) == 128:
                    previous_witness = previous_witness[1:]
                choice_witness = (
                    previous_witness[
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                        * 2 : bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                        * 4
                    ]
                    + choice_witness
                )
            else:
                # Hash case
                hash_tx = transaction_info_service(
                    tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list[
                        counter + 1
                    ].get_txid()
                )
                previous_witness = hash_tx.inputs[0].witness
                while len(previous_witness[0]) == 128:
                    previous_witness = previous_witness[1:]
                choice_witness = (
                    previous_witness[
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                        * 2 : bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                        * 4
                    ]
                    + choice_witness
                )
                # choice_witness.extend(previous_witness[4:8])
            if (
                wrong_hash_choice_array[counter]
                != (suffix_character * amount_of_bits_wrong_step_search)
            ) and (bitvmx_protocol_verifier_dto.first_wrong_step != 0):
                break
            counter -= 1
        return choice_witness
