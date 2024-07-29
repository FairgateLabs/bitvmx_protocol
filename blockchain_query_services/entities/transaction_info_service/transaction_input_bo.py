from typing import List

from pydantic import BaseModel


class TransactionInputBO(BaseModel):
    tx_id: str
    index: int
    witness: List[str]

    @staticmethod
    def from_vin(vin: dict) -> "TransactionInputBO":
        return TransactionInputBO(tx_id=vin["txid"], index=vin["vout"], witness=vin["witness"])
