from http import HTTPStatus

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import NETWORK
from fastapi import HTTPException

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.transaction_generation.services.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from verifier_app.domain.persistence.interfaces.bitvmx_protocol_setup_properties_dto_persistence_interface import (
    BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
)
from verifier_app.domain.persistence.interfaces.bitvmx_protocol_verifier_private_dto_persistence_interface import (
    BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
)


class GeneratePublicKeysController:

    def __init__(
        self,
        generate_verifier_public_keys_service_class,
        common_protocol_properties,
        transaction_generator_from_public_keys_service: TransactionGeneratorFromPublicKeysService,
        bitvmx_protocol_verifier_private_dto_persistence: BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
        bitvmx_protocol_setup_properties_dto_persistence: BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
    ):
        self.generate_verifier_public_keys_service_class = (
            generate_verifier_public_keys_service_class
        )
        self.common_protocol_properties = common_protocol_properties
        self.transaction_generator_from_public_keys_service = (
            transaction_generator_from_public_keys_service
        )
        self.bitvmx_protocol_verifier_private_dto_persistence = (
            bitvmx_protocol_verifier_private_dto_persistence
        )
        self.bitvmx_protocol_setup_properties_dto_persistence = (
            bitvmx_protocol_setup_properties_dto_persistence
        )

    async def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):

        if self.common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == self.common_protocol_properties.network.value
        setup_uuid = bitvmx_protocol_setup_properties_dto.setup_uuid
        bitvmx_protocol_verifier_private_dto = (
            self.bitvmx_protocol_verifier_private_dto_persistence.get(setup_uuid=setup_uuid)
        )

        destroyed_verifier_private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.destroyed_private_key)
        )
        winternitz_private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.winternitz_private_key)
        )

        if (
            destroyed_verifier_private_key.get_public_key().to_x_only_hex()
            not in bitvmx_protocol_setup_properties_dto.seed_unspendable_public_key
        ):
            raise HTTPException(
                status_code=HTTPStatus.EXPECTATION_FAILED, detail="Seed does not contain public key"
            )

        generate_verifier_public_keys_service = self.generate_verifier_public_keys_service_class(
            private_key=winternitz_private_key
        )
        bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto = generate_verifier_public_keys_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto = (
            self.transaction_generator_from_public_keys_service(
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            )
        )

        self.bitvmx_protocol_setup_properties_dto_persistence.create(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )

        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto,
            winternitz_private_key.get_public_key().to_hex(),
        )
