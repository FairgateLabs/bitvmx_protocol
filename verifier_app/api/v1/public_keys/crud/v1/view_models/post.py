from pydantic import BaseModel

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import (
    BitVMXProverWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)


class PublicKeysPostV1Input(BaseModel):
    setup_uuid: str
    seed_destroyed_public_key_hex: str
    bitvmx_prover_winternitz_public_keys_dto: BitVMXProverWinternitzPublicKeysDTO
    bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO
    prover_public_key: str
    controlled_prover_address: str


class PublicKeysPostV1Output(BaseModel):
    verifier_public_key: str
    bitvmx_verifier_winternitz_public_keys_dto: BitVMXVerifierWinternitzPublicKeysDTO
