from dependency_injector import containers, providers

from verifier_app.dependency_injection.persistences.bitvmx_protocol_verifier_private_dto_persistences import (
    BitVMXProtocolVerifierPrivateDTOPersistences,
)
from verifier_app.domain.controllers.v1.setup.create_setup_controller import CreateSetupController


class CreateSetupControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        CreateSetupController,
        bitvmx_protocol_verifier_private_dto_persistence=BitVMXProtocolVerifierPrivateDTOPersistences.bitvmx,
    )
