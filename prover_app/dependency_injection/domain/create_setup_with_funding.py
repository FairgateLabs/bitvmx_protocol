from dependency_injector import containers, providers

from bitvmx_protocol_library.config import common_protocol_properties
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    faucet_service,
)
from prover_app.config import protocol_properties
from prover_app.domain.controllers.v1.setup.create_setup_with_funding_controller import (
    CreateSetupWithFundingController,
)


class CreateSetupWithFundingControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        CreateSetupWithFundingController,
        faucet_service=faucet_service,
        common_protocol_properties=common_protocol_properties,
        protocol_properties=protocol_properties,
    )
