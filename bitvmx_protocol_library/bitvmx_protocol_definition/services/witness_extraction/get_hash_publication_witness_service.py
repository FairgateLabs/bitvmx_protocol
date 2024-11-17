from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.hash_publication_witness_dto import (
    HashPublicationWitnessDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class GetHashPublicationWitnessService:
    def __call__(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> HashPublicationWitnessDTO:
        publish_hash_tx = transaction_info_service(
            tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx.get_txid()
        )
        publish_hash_tx_witness = publish_hash_tx.inputs[0].witness
        while len(publish_hash_tx_witness[0]) == 128:
            publish_hash_tx_witness = publish_hash_tx_witness[1:]

        amount_of_keys_hash = len(
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys
        )
        final_hash = publish_hash_tx_witness[: 2 * amount_of_keys_hash]
        publish_hash_tx_witness = publish_hash_tx_witness[2 * amount_of_keys_hash :]

        amount_of_keys_halt_step = len(
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys
        )
        halt_step = publish_hash_tx_witness[: 2 * amount_of_keys_halt_step]
        publish_hash_tx_witness = publish_hash_tx_witness[2 * amount_of_keys_halt_step :]

        input_list = []
        for (
            input_public_keys_list
        ) in (
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.input_public_keys
        ):
            current_input_length = len(input_public_keys_list)
            input_list.append(publish_hash_tx_witness[: 2 * current_input_length])
            publish_hash_tx_witness = publish_hash_tx_witness[2 * current_input_length :]

        assert len(publish_hash_tx_witness) == 2
        return HashPublicationWitnessDTO(
            final_hash=final_hash,
            halt_step=halt_step,
            input=input_list,
        )
