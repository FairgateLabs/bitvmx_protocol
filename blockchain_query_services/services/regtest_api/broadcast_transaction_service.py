from blockchain_query_services.services.bitcoin_rpc_services import BitcoinRPCClients


class BroadcastTransactionService:

    def __init__(self):
        self.bitcoin_rpc_client = BitcoinRPCClients.regtest()

    def __call__(self, transaction: str):
        self.bitcoin_rpc_client.send_raw_transaction(raw_tx=transaction)
        self.bitcoin_rpc_client.generate_blocks(num_blocks=1)
