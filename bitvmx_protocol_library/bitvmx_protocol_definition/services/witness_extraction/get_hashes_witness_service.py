from typing import List, Optional

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class GetHashesWitnessService:

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        iteration: Optional[int] = None,
    ) -> List[str]:
        hashes_transaction = (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list[
                iteration
            ]
        )
        hashes_tx = transaction_info_service(tx_id=hashes_transaction.get_txid())
        hashes_tx_witness = hashes_tx.inputs[0].witness.copy()
        while len(hashes_tx_witness[0]) == 128:
            hashes_tx_witness = hashes_tx_witness[1:]
        while len(hashes_tx_witness[-1]) == 128:
            hashes_tx_witness = hashes_tx_witness[:-1]
        hashes_tx_witness = hashes_tx_witness[:-2]
        if iteration > 0:
            hashes_tx_witness = hashes_tx_witness[8:]
        return hashes_tx_witness
