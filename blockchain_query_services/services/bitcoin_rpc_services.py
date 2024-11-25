import json
from typing import Tuple

import requests
from bitcoinutils.constants import SATOSHIS_PER_BITCOIN
from bitcoinutils.transactions import Transaction
from dependency_injector import containers, providers

from blockchain_query_services.entities.transaction_info_service.transaction_info_bo import (
    TransactionInfoBO,
)
from blockchain_query_services.entities.transaction_info_service.transaction_input_bo import (
    TransactionInputBO,
)
from blockchain_query_services.entities.transaction_info_service.transaction_output_bo import (
    TransactionOutputBO,
)


class BitcoinRPCClient:
    def __init__(self, rpc_user, rpc_password, rpc_host="host.docker.internal", rpc_port=8443):
        """
        Initialize Bitcoin RPC client for regtest

        :param rpc_user: RPC username
        :param rpc_password: RPC password
        :param rpc_host: RPC host (default localhost)
        :param rpc_port: RPC port for regtest (default 18443)
        """
        self.rpc_url = f"http://{rpc_host}:{rpc_port}/"
        self.auth = (rpc_user, rpc_password)
        self.address = None
        try:
            self._call_rpc("getwalletinfo", [])
        except Exception as e1:
            if "No wallet is loaded" in e1.args[0]:
                try:
                    self._call_rpc("createwallet", ["testwallet"])
                except Exception as e2:
                    if "Database already exists" in e2.args[0]:
                        self._call_rpc("loadwallet", ["testwallet"])
                    else:
                        raise e2
            else:
                raise e1

    def _call_rpc(self, method, params=None):
        """
        Make an RPC call to the Bitcoin node

        :param method: RPC method name
        :param params: List of parameters
        :return: RPC response
        """
        payload = {"jsonrpc": "1.0", "id": "curltest", "method": method, "params": params or []}

        response = requests.post(
            self.rpc_url,
            auth=self.auth,
            data=json.dumps(payload),
            headers={"Content-Type": "text/plain"},
        )

        if response.status_code != 200:
            raise Exception(f"RPC Error: {response.text}")

        return response.json()["result"]

    def get_new_address(self):
        """
        Generate a new Bitcoin address

        :return: New Bitcoin address
        """
        if self.address is None:
            new_address = self._call_rpc("getnewaddress")
            self.address = new_address
            return new_address
        else:
            return self.address

    def generate_blocks(self, num_blocks):
        """
        Mine specified number of blocks to generate funds

        :param num_blocks: Number of blocks to mine
        :return: List of block hashes
        """
        return self._call_rpc("generatetoaddress", [num_blocks, self.get_new_address()])

    def check_transaction_confirmed(self, tx_id: str):
        try:
            self._call_rpc("gettxoutproof", [[tx_id]])
            return True
        except Exception as e:
            if "Transaction not yet in block" in e.args[0]:
                return False
            raise e

    def get_tx_info(self, tx_id: str) -> TransactionInfoBO:
        tx_info_hex = self._call_rpc("getrawtransaction", [tx_id])
        decoded_transaction = self._call_rpc("decoderawtransaction", [tx_info_hex])
        inputs = list(
            map(
                lambda x: TransactionInputBO(
                    tx_id=x["txid"],
                    index=x["vout"],
                    witness=x["txinwitness"],
                ),
                decoded_transaction["vin"],
            )
        )
        outputs = list(
            map(
                lambda x: TransactionOutputBO(
                    index=x["n"],
                    value=int(x["value"] * SATOSHIS_PER_BITCOIN),
                    address=x["scriptPubKey"]["address"],
                ),
                decoded_transaction["vout"],
            )
        )
        return TransactionInfoBO(
            confirmed=self.check_transaction_confirmed(tx_id=tx_id),
            tx_id=tx_id,
            inputs=inputs,
            outputs=outputs,
        )

    def send_raw_transaction(self, raw_tx: str):
        self._call_rpc("sendrawtransaction", [raw_tx])

    def get_utxo_index(self, amount: float, tx_id: str) -> int:
        raw_transaction = self._call_rpc("getrawtransaction", [tx_id])
        tx = Transaction.from_raw(rawtxhex=raw_transaction)
        amount_of_satoshis = amount * SATOSHIS_PER_BITCOIN
        for i in range(len(tx.outputs)):
            if tx.outputs[i].amount == amount_of_satoshis:
                return i
        raise Exception("Amount not found")

    def send_to_address(self, address: str, amount: float) -> Tuple[str, int]:
        """
        Send funds to a specific address

        :param address: Destination Bitcoin address
        :param amount: Amount in BTC to send
        :return: Transaction ID, index of tx sending the funds
        """
        tx_id = None
        while tx_id is None:
            try:
                tx_id = self._call_rpc("sendtoaddress", [address, amount])
            except Exception as e:
                if "Insufficient funds" not in e.args[0]:
                    raise e
                else:
                    self.generate_blocks(num_blocks=1)
        index = self.get_utxo_index(amount=amount, tx_id=tx_id)
        return tx_id, index


class BitcoinRPCClients(containers.DeclarativeContainer):

    regtest = providers.Factory(
        BitcoinRPCClient,
        rpc_user="myuser",
        rpc_password="SomeDecentp4ssw0rd",
        rpc_host="host.docker.internal",
        rpc_port=8443,
    )
