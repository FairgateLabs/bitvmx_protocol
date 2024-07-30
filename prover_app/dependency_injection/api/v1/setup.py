from dependency_injector import containers, providers

from bitvmx_protocol_library.config import common_protocol_properties
from prover_app.api.v1.setup.crud.v1.view_controllers.post import SetupPostViewControllerV1
from prover_app.config import protocol_properties
from prover_app.dependency_injection.domain.create_setup import CreateSetupControllers


class SetupPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        SetupPostViewControllerV1,
        create_setup_controller=CreateSetupControllers.bitvmx_protocol,
        protocol_properties=protocol_properties,
        common_protocol_properties=common_protocol_properties,
    )
