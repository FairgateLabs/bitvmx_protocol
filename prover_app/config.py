from typing import List, Optional

from pydantic_settings import BaseSettings


class ProtocolProperties(BaseSettings):
    verifier_list: List[str]
    prover_host: str
    prover_address: Optional[str] = None
    prover_private_key: Optional[str] = None
    funding_tx_id: Optional[str] = None
    funding_index: Optional[int] = None

    class Config:
        env_file = ".env_prover"


protocol_properties = ProtocolProperties()
