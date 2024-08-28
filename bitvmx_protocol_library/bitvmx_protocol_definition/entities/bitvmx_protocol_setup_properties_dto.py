import hashlib
from typing import Dict, Optional, Union

from bitcoinutils.keys import PublicKey
from pydantic import BaseModel, field_serializer

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import (
    BitVMXProverWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.script_generation.entities.dtos.bitvmx_bitcoin_scripts_dto import (
    BitVMXBitcoinScriptsDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_transactions_dto import (
    BitVMXTransactionsDTO,
)


class BitVMXProtocolSetupPropertiesDTO(BaseModel):
    setup_uuid: str
    uuid: Optional[str]
    funding_amount_of_satoshis: int
    step_fees_satoshis: int
    funding_tx_id: str
    funding_index: int
    verifier_address_dict: Dict[str, str]
    prover_destination_address: str
    prover_signature_public_key: str
    verifier_destination_address: str
    verifier_signature_public_key: str
    seed_unspendable_public_key: str
    prover_destroyed_public_key: str
    verifier_destroyed_public_key: str
    bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO
    bitvmx_bitcoin_scripts_dto: Optional[BitVMXBitcoinScriptsDTO] = None
    bitvmx_transactions_dto: Optional[BitVMXTransactionsDTO] = None
    bitvmx_prover_winternitz_public_keys_dto: Optional[BitVMXProverWinternitzPublicKeysDTO] = None
    bitvmx_verifier_winternitz_public_keys_dto: Optional[BitVMXVerifierWinternitzPublicKeysDTO] = (
        None
    )

    def __init__(self, **data):
        if "bitvmx_transactions_dto" in data and data["bitvmx_transactions_dto"] is not None:
            data["bitvmx_transactions_dto"] = BitVMXTransactionsDTO(
                **data["bitvmx_transactions_dto"]
            )
        if "bitvmx_bitcoin_scripts_dto" in data and data["bitvmx_bitcoin_scripts_dto"] is not None:
            data["bitvmx_bitcoin_scripts_dto"] = BitVMXBitcoinScriptsDTO(
                **data["bitvmx_bitcoin_scripts_dto"]
            )
        super().__init__(**data)

    @field_serializer("bitvmx_transactions_dto", when_used="always")
    def serialize_transactions_dto(
        bitvmx_transactions_dto: Union[BitVMXTransactionsDTO, None]
    ) -> Union[None, dict]:
        if bitvmx_transactions_dto is None:
            return None
        return bitvmx_transactions_dto.model_dump()

    @staticmethod
    def unspendable_public_key_from_seed(seed_unspendable_public_key: str):
        destroyed_public_key_hex = hashlib.sha256(
            bytes.fromhex(seed_unspendable_public_key)
        ).hexdigest()
        # This is done so everyone can verify that they participated on the seed construction
        # but at the same time the public key is unspendable
        return PublicKey(hex_str="02" + destroyed_public_key_hex)

    @property
    def unspendable_public_key(self):
        return self.unspendable_public_key_from_seed(self.seed_unspendable_public_key)

    @property
    def signature_public_keys(self):
        return [self.verifier_destroyed_public_key, self.prover_destroyed_public_key]
