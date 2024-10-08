from dependency_injector import containers, providers

from prover_app.api.v1.input.crud.v1.view_controllers.post import InputPostViewControllerV1
from prover_app.dependency_injection.domain.input import InputControllers


class InputPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        InputPostViewControllerV1, input_controller=InputControllers.bitvmx_protocol
    )
