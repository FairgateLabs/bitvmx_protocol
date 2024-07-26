from typing import Optional

from pydantic_settings import BaseSettings

from bitvmx_protocol_library.enums import BitcoinNetwork


class CommonProtocolProperties(BaseSettings):
    network: Optional[BitcoinNetwork] = BitcoinNetwork.MUTINYNET
    initial_amount_satoshis: int
    step_fees_satoshis: int
    choice_fees_satoshis: int
    hash_fees_satoshis: int
    trigger_fees_satoshis: int

    class Config:
        env_file = ".env_common"


common_protocol_properties = CommonProtocolProperties()
