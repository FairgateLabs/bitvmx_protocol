from dependency_injector import containers, providers

from bitvmx_protocol_library.bitvmx_protocol_definition.services.generate_verifier_public_keys_service import (
    GenerateVerifierPublicKeysService,
)
from verifier_app.domain.v1.public_keys.controllers.generate_public_keys_controller import (
    GeneratePublicKeysController,
)


class GeneratePublicKeysControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        GeneratePublicKeysController,
        generate_verifier_public_keys_service_class=GenerateVerifierPublicKeysService,
    )
