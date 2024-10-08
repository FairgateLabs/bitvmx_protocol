from dependency_injector import containers, providers

from prover_app.dependency_injection.persistences.bitvmx_protocol_prover_dto_persistences import (
    BitVMXProtocolProverDTOPersistences,
)
from prover_app.dependency_injection.persistences.bitvmx_protocol_setup_properties_dto_persistences import (
    BitVMXProtocolSetupPropertiesDTOPersistences,
)
from prover_app.domain.controllers.v1.input.input_controller import InputController


class InputControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        InputController,
        bitvmx_protocol_setup_properties_dto_persistence=BitVMXProtocolSetupPropertiesDTOPersistences.bitvmx,
        bitvmx_protocol_prover_dto_persistence=BitVMXProtocolProverDTOPersistences.bitvmx,
    )
