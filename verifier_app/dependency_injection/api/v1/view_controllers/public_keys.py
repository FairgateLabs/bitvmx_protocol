from dependency_injector import containers, providers

from verifier_app.api.v1.public_keys.crud.v1.view_controllers.post import (
    PublicKeysPostViewControllerV1,
)
from verifier_app.dependency_injection.domain.v1.controllers.generate_public_keys import (
    GeneratePublicKeysControllers,
)


class PublicKeysPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        PublicKeysPostViewControllerV1,
        generate_public_keys_controller=GeneratePublicKeysControllers.bitvmx_protocol,
    )
