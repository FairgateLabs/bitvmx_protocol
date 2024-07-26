from pydantic import BaseModel


class TransactionOutputBO(BaseModel):
    address: str
    index: int
    value: int

    @staticmethod
    def from_vout(vout: dict, index: int) -> "TransactionOutputBO":
        return TransactionOutputBO(
            address=vout["scriptpubkey_address"], index=index, value=vout["value"]
        )
