from dependency_injector import containers, providers

from verifier_app.api.v1.setup.crud.v1.view_controllers.post import SetupPostViewControllerV1


class SetupPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        SetupPostViewControllerV1,
    )
