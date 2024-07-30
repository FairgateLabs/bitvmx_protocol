from dependency_injector import containers, providers

from verifier_app.domain.v1.setup.controllers.create_setup_controller import CreateSetupController


class CreateSetupControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        CreateSetupController,
    )
