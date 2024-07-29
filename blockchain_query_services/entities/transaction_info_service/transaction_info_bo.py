from typing import List, Optional

from pydantic import BaseModel

from blockchain_query_services.entities.transaction_info_service.transaction_input_bo import (
    TransactionInputBO,
)
from blockchain_query_services.entities.transaction_info_service.transaction_output_bo import (
    TransactionOutputBO,
)


class TransactionInfoBO(BaseModel):
    confirmed: Optional[bool] = None
    tx_id: str
    inputs: List[TransactionInputBO]
    outputs: List[TransactionOutputBO]

    @staticmethod
    def from_transaction(tx: dict) -> "TransactionInfoBO":
        return TransactionInfoBO(
            confirmed=tx["status"]["confirmed"],
            tx_id=tx["txid"],
            inputs=[TransactionInputBO.from_vin(vin) for vin in tx["vin"]],
            outputs=[
                TransactionOutputBO.from_vout(vout, index) for index, vout in enumerate(tx["vout"])
            ],
        )

    def get_output(self, address: str) -> TransactionOutputBO:
        for element in self.outputs:
            if element.address == address:
                return element
        raise Exception("Address not found in the outputs")
