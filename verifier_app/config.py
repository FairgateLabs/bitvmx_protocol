from typing import Optional

from pydantic_settings import BaseSettings

from prover_app.config import BitcoinNetwork


class ProtocolProperties(BaseSettings):
    prover_host: str

    class Config:
        env_file = ".env_verifier"


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
