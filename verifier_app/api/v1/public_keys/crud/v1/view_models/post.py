from pydantic import BaseModel

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)


class PublicKeysPostV1Input(BaseModel):
    bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO


class PublicKeysPostV1Output(BaseModel):
    verifier_public_key: str
    bitvmx_verifier_winternitz_public_keys_dto: BitVMXVerifierWinternitzPublicKeysDTO
