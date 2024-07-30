from dependency_injector import containers, providers

from prover_app.api.v1.next_step.crud.v1.view_controllers.post import NextStepPostViewControllerV1
from prover_app.dependency_injection.domain.publish_next_step import PublishNextStepControllers


class NextStepPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        NextStepPostViewControllerV1,
        publish_next_step_controller=PublishNextStepControllers.bitvmx_protocol(),
    )
