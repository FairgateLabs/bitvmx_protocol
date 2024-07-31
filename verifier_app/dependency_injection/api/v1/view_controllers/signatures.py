from dependency_injector import containers, providers

from verifier_app.api.v1.signatures.crud.v1.view_controllers.post import (
    SignaturesPostViewControllerV1,
)
from verifier_app.dependency_injection.domain.v1.controllers.generate_signatures import (
    GenerateSignaturesControllers,
)


class SignaturesPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        SignaturesPostViewControllerV1,
        generate_signatures_controller=GenerateSignaturesControllers.bitvmx_protocol(),
    )
