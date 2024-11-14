from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
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
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_read_constant_equivocation_challenge_transaction_service import (
    TriggerRead1ConstantEquivocationChallengeTransactionService,
    TriggerRead2ConstantEquivocationChallengeTransactionService,
)


class VerifierReadConstantEquivocationChallengeDetectionService:
    def __init__(self):
        self.base_path = "verifier_files/"
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        published_execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace
        # This goes here and not in the init because the plan is to agree it on the setup phase
        input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        static_addresses = input_and_constant_addresses_generation_service(
            input_length=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        )
        # If addresses are different, go through the execution path
        if (published_execution_trace.read_1_address in static_addresses.constants.keys()) and (
            published_execution_trace.read_1_value
            != static_addresses.constants[published_execution_trace.read_1_address]
        ):
            return (
                TriggerRead1ConstantEquivocationChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_CONSTANT_EQUIVOCATION_CHALLENGE_1,
            )
        if (published_execution_trace.read_2_address in static_addresses.constants.keys()) and (
            published_execution_trace.read_2_value
            != static_addresses.constants[published_execution_trace.read_2_address]
        ):
            return (
                TriggerRead2ConstantEquivocationChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_CONSTANT_EQUIVOCATION_CHALLENGE_2,
            )
        return None, None
