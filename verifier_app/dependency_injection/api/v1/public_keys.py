from dependency_injector import containers, providers

from verifier_app.api.v1.public_keys.crud.v1.view_controllers.post import (
    PublicKeysPostViewControllerV1,
)
from winternitz_keys_handling.services.generate_verifier_public_keys_service import (
    GenerateVerifierPublicKeysService,
)


class PublicKeysPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        PublicKeysPostViewControllerV1,
        generate_verifier_public_keys_service_class=GenerateVerifierPublicKeysService,
    )
