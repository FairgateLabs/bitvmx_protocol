from pydantic import BaseModel

from bitvmx_protocol_library.enums import BitcoinNetwork


class SetupPostV1Input(BaseModel):
    setup_uuid: str
    network: BitcoinNetwork


class SetupPostV1Output(BaseModel):
    public_key: str
    verifier_signature_public_key: str
    verifier_destination_address: str
