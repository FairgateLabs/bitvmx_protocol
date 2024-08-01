from pydantic import BaseModel


class BitVMXProtocolProverPrivateDTO(BaseModel):
    winternitz_private_key: str
