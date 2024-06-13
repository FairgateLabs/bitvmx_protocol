from pydantic_settings import BaseSettings


class ProtocolProperties(BaseSettings):
    amount_bits_choice: int
    d0: int


protocol_properties = ProtocolProperties()
