from typing import List, Optional

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class GetFullProverChoiceWitnessService:

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        iteration: Optional[int] = None,
    ) -> List[str]:
        choice_witness = []
        counter = 0
        total_amount_of_choices = len(
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list
        )
        if iteration is not None:
            counter += total_amount_of_choices - iteration
        while counter < total_amount_of_choices:
            if counter == 0:
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
                        total_amount_of_choices - counter
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
            counter += 1
        return choice_witness
