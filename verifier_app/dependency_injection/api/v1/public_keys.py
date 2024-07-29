from dependency_injector import containers, providers

from bitvmx_protocol_library.bitvmx_protocol_definition.services.generate_verifier_public_keys_service import (
    GenerateVerifierPublicKeysService,
)
from verifier_app.api.v1.public_keys.crud.v1.view_controllers.post import (
    PublicKeysPostViewControllerV1,
)


class PublicKeysPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        PublicKeysPostViewControllerV1,
        generate_verifier_public_keys_service_class=GenerateVerifierPublicKeysService,
    )
