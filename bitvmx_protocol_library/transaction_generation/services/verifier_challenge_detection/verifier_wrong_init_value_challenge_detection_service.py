from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.input_and_constant_addresses_generation_service import (
    InputAndConstantAddressesGenerationService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)


class VerifierWrongInitValueChallengeDetectionService:
    def __init__(self):
        pass

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        input_and_constant_addresses = input_and_constant_addresses_generation_service(
            input_length=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        )
        memory_regions = input_and_constant_addresses.memory_regions()
        pass
