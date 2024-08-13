from typing import Optional

from pydantic import BaseModel


class BitVMXProtocolVerifierPrivateDTO(BaseModel):
    winternitz_private_key: str
    verifier_signature_private_key: str
    destroyed_private_key: Optional[str] = None
