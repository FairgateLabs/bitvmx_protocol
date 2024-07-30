from pydantic_settings import BaseSettings


class ProtocolProperties(BaseSettings):
    prover_host: str

    class Config:
        env_file = ".env_verifier"


protocol_properties = ProtocolProperties()
