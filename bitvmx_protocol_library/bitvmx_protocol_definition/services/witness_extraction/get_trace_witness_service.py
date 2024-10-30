from typing import List

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class GetTraceWitnessService:

    def __call__(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> List[str]:
        publish_trace_tx = transaction_info_service(
            tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.get_txid()
        )

        verifier_keys_witness_values = []
        processed_values = 0
        real_values = []
        publish_trace_tx_witness = publish_trace_tx.inputs[0].witness
        while len(publish_trace_tx_witness[0]) == 128:
            publish_trace_tx_witness = publish_trace_tx_witness[1:]
        # At this point, we have erased the signatures
        # In the publication trace, there is the confirmation for the last choice, we also need to erase that
        # The amount of hashes to discard is 4 because we sign a single word. Then we have the hash and the value.
        # Hence, 8 elements. We'll never use more than a nibble to encode the choices.
        publish_trace_tx_witness = publish_trace_tx_witness[8:]

        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )

        for i in reversed(range(len(trace_words_lengths))):
            current_keys_length = len(
                bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
                    i
                ]
            )
            current_trace_witness = publish_trace_tx_witness[
                processed_values : processed_values + 2 * current_keys_length
            ]
            verifier_keys_witness_values.append(current_trace_witness)
            processed_values += 2 * current_keys_length
            real_values.append(
                "".join(
                    map(
                        lambda elem: "0" if len(elem) == 0 else elem[1],
                        current_trace_witness[1 : 2 * trace_words_lengths[i] : 2],
                    )
                )
            )

        return verifier_keys_witness_values
