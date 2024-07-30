from typing import List

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


class PublicKeysPostV1Input(BaseModel):
    setup_uuid: str
    seed_destroyed_public_key_hex: str
    prover_public_key: str
    trace_words_lengths: List[int]
    amount_of_wrong_step_search_iterations: int
    amount_of_bits_wrong_step_search: int
    amount_of_bits_per_digit_checksum: int
    funding_amount_satoshis: int
    step_fees_satoshis: int
    funds_tx_id: str
    funds_index: int
    amount_of_nibbles_hash: int
    controlled_prover_address: str
    bitvmx_prover_winternitz_public_keys_dto: BitVMXProverWinternitzPublicKeysDTO
    bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO


class PublicKeysPostV1Output(BaseModel):
    choice_search_verifier_public_keys_list: List[List[List[str]]]
    verifier_public_key: str
    trace_verifier_public_keys: List[List[str]]
