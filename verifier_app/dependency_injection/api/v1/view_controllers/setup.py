from dependency_injector import containers, providers

from verifier_app.api.v1.setup.crud.v1.view_controllers.post import SetupPostViewControllerV1
from verifier_app.dependency_injection.domain.v1.controllers.create_setup import (
    CreateSetupControllers,
)


class SetupPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        SetupPostViewControllerV1, create_setup_controller=CreateSetupControllers.bitvmx_protocol
    )
