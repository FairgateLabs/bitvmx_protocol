from enum import Enum
from typing import List, Optional

from pydantic_settings import BaseSettings


class BitcoinNetwork(Enum):
    MUTINYNET = "mutinynet"
    TESTNET = "testnet"
    MAINNET = "mainnet"


class ProtocolProperties(BaseSettings):
    amount_bits_choice: int
    amount_of_bits_per_digit_checksum: int
    verifier_list: List[str]
    prover_host: str
    prover_address: Optional[str] = None
    prover_private_key: Optional[str] = None
    funding_tx_id: Optional[str] = None
    funding_index: Optional[int] = None

    class Config:
        env_file = ".env_prover"


class CommonProtocolProperties(BaseSettings):
    network: Optional[BitcoinNetwork] = BitcoinNetwork.MUTINYNET
    initial_amount_satoshis: int
    step_fees_satoshis: int
    choice_fees_satoshis: int
    hash_fees_satoshis: int
    trigger_fees_satoshis: int

    class Config:
        env_file = ".env_common"


protocol_properties = ProtocolProperties()
common_protocol_properties = CommonProtocolProperties()
