from dependency_injector import containers, providers

from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    faucet_service,
)
from prover_app.api.v1.fund.crud.v1.view_controllers.post import FundPostViewControllerV1


class FundPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        FundPostViewControllerV1,
        faucet_service=faucet_service,
    )
