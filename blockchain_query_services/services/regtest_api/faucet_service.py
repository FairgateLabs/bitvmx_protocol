from typing import Optional

from bitcoinutils.constants import SATOSHIS_PER_BITCOIN

from blockchain_query_services.services.bitcoin_rpc_services import BitcoinRPCClients
from blockchain_query_services.services.interfaces.faucet_service import FaucetServiceInterface


class FaucetService(FaucetServiceInterface):
    def __init__(self):
        self.bitcoin_rpc_client = BitcoinRPCClients.regtest()

    def __call__(
        self,
        amount: Optional[int] = 1000000,
        destination_address: Optional[str] = None,
    ):
        if destination_address is None:
            raise Exception("For regtest the faucet's destination address is mandatory")

        # Destination address (replace with actual address)
        destination_address = destination_address

        # Amount to send
        send_amount = amount / float(SATOSHIS_PER_BITCOIN)

        try:
            # Send funds
            return self.bitcoin_rpc_client.send_to_address(destination_address, send_amount)
        except Exception as e:
            print(f"Error sending funds: {e}")
            raise e
