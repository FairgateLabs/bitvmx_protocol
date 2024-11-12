from dependency_injector import containers, providers

from bitvmx_protocol_library.bitvmx_protocol_definition.services.public_keys_generation.generate_verifier_public_keys_service import (
    GenerateVerifierPublicKeysService,
)
from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.transaction_generation.services.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from verifier_app.dependency_injection.persistences.bitvmx_protocol_setup_properties_dto_persistences import (
    BitVMXProtocolSetupPropertiesDTOPersistences,
)
from verifier_app.dependency_injection.persistences.bitvmx_protocol_verifier_private_dto_persistences import (
    BitVMXProtocolVerifierPrivateDTOPersistences,
)
from verifier_app.domain.controllers.v1.public_keys.generate_public_keys_controller import (
    GeneratePublicKeysController,
)


class GeneratePublicKeysControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        GeneratePublicKeysController,
        generate_verifier_public_keys_service_class=GenerateVerifierPublicKeysService,
        common_protocol_properties=common_protocol_properties,
        transaction_generator_from_public_keys_service=TransactionGeneratorFromPublicKeysService(),
        bitvmx_protocol_verifier_private_dto_persistence=BitVMXProtocolVerifierPrivateDTOPersistences.bitvmx,
        bitvmx_protocol_setup_properties_dto_persistence=BitVMXProtocolSetupPropertiesDTOPersistences.bitvmx,
    )
