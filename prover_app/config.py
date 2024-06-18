from typing import List

from pydantic_settings import BaseSettings


class ProtocolProperties(BaseSettings):
    amount_bits_choice: int
    amount_of_bits_per_digit_checksum: int
    verifier_list: List[str]

    class Config:
        env_file = ".env_prover"


protocol_properties = ProtocolProperties()
