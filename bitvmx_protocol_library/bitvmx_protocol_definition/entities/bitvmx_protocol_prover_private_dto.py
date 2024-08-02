from pydantic import BaseModel


class BitVMXProtocolProverPrivateDTO(BaseModel):
    winternitz_private_key: str
    prover_signature_private_key: str
