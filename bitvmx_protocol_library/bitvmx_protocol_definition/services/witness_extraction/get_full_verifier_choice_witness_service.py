from typing import List

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class GetFullVerifierChoiceWitnessService:

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> List[str]:
        choice_witness = []

        total_amount_of_choices = len(
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list
        )
        for i in range(total_amount_of_choices - 1, -1, -1):
            # Hash case
            search_choice_tx = transaction_info_service(
                tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                    i
                ].get_txid()
            )
            previous_witness = search_choice_tx.inputs[0].witness
            while len(previous_witness[0]) == 128:
                previous_witness = previous_witness[1:]
            choice_witness = (
                previous_witness[
                    : bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    * 2
                ]
                + choice_witness
            )
        return choice_witness
