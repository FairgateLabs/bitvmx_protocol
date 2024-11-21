from blockchain_query_services.entities.transaction_info_service.transaction_info_bo import (
    TransactionInfoBO,
)
from blockchain_query_services.services.bitcoin_rpc_services import BitcoinRPCClients


class TransactionInfoService:

    def __init__(self):
        self.bitcoin_rpc_client = BitcoinRPCClients.regtest()

    def __call__(self, tx_id: str) -> TransactionInfoBO:
        return self.bitcoin_rpc_client.get_tx_info(tx_id=tx_id)
