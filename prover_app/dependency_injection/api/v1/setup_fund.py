from dependency_injector import containers, providers

from bitvmx_protocol_library.config import common_protocol_properties
from prover_app.api.v1.setup.fund.v1.view_controllers.post import SetupFundPostViewControllerV1
from prover_app.config import protocol_properties
from prover_app.dependency_injection.domain.create_setup_with_funding import (
    CreateSetupWithFundingControllers,
)


class SetupFundPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        SetupFundPostViewControllerV1,
        create_setup_with_funding_controller=CreateSetupWithFundingControllers.bitvmx_protocol,
        protocol_properties=protocol_properties,
        common_protocol_properties=common_protocol_properties,
    )
