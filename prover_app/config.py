from enum import Enum
from typing import List, Optional

from pydantic_settings import BaseSettings


class Networks(Enum):
    MUTINYNET = "mutinynet"
    TESTNET = "testnet"


class ProtocolProperties(BaseSettings):
    amount_bits_choice: int
    amount_of_bits_per_digit_checksum: int
    verifier_list: List[str]
    prover_host: str
    initial_amount_satoshis: int
    step_fees_satoshis: int
    prover_address: str
    network: Optional[Networks] = Networks.MUTINYNET
    prover_private_key: Optional[str] = None
    funding_tx_id: Optional[str] = None
    funding_index: Optional[int] = None

    class Config:
        env_file = ".env_prover"


protocol_properties = ProtocolProperties()
