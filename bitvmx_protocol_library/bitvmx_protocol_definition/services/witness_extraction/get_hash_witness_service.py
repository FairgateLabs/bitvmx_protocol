from typing import List

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class GetHashWitnessService:

    def __call__(
        self,
        binary_choice_array: List[str],
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> List[str]:
        amount_of_bits_wrong_step_search = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
        )
        hash_step_iteration = len(binary_choice_array) - 1
        while (hash_step_iteration >= 0) and (
            binary_choice_array[hash_step_iteration] == "1" * amount_of_bits_wrong_step_search
        ):
            hash_step_iteration -= 1
        if hash_step_iteration < 0:
            witness_hash_tx_definition = (
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx
            )
            witness_hash_tx = transaction_info_service(tx_id=witness_hash_tx_definition.get_txid())
            hash_witness = witness_hash_tx.inputs[0].witness
            while len(hash_witness[0]) == 128:
                hash_witness = hash_witness[1:]
            # Erase script and control block
            current_hash_witness = hash_witness[:-2]
        else:
            witness_hash_tx_definition = (
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list[
                    hash_step_iteration
                ]
            )
            witness_hash_tx = transaction_info_service(tx_id=witness_hash_tx_definition.get_txid())
            hash_index = int(binary_choice_array[hash_step_iteration], 2)
            hash_witness = witness_hash_tx.inputs[0].witness
            while len(hash_witness[0]) == 128:
                hash_witness = hash_witness[1:]
            # At this point, we have erased the signatures
            # In the publication trace, there is the confirmation for the last choice, we also need to erase that
            # The amount of hashes to discard is 4 because we sign a single word. Then we have the hash and the value.
            # Hence, 8 elements. We'll never use more than a nibble to encode the choices.
            if hash_step_iteration > 0:
                hash_witness = hash_witness[8:]
            hash_length = (
                len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[
                        hash_step_iteration
                    ][
                        0
                    ]
                )
                * 2
            )
            hash_index_in_witness = (
                len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[
                        hash_step_iteration
                    ]
                )
                - hash_index
                - 1
            )
            current_hash_witness = hash_witness[
                hash_length * hash_index_in_witness : hash_length * (hash_index_in_witness + 1)
            ]
            assert len(current_hash_witness) == hash_length
        return current_hash_witness
