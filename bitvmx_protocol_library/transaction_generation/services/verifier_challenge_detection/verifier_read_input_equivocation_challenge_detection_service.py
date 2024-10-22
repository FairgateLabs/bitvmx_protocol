from bitvmx_protocol_library.bitvmx_execution.entities.execution_trace_dto import ExecutionTraceDTO
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
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_read_input_equivocation_challenge_transaction_service import (
    TriggerReadInput1EquivocationChallengeTransactionService,
    TriggerReadInput2EquivocationChallengeTransactionService,
)


class VerifierReadInputEquivocationChallengeDetectionService:
    def __init__(self):
        self.base_path = "verifier_files/"
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace
        first_wrong_step_trace_series = self.execution_trace_query_service(
            setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid,
            index=bitvmx_protocol_verifier_dto.first_wrong_step,
            input_hex=bitvmx_protocol_verifier_dto.input_hex,
        )
        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )
        first_wrong_step_trace = ExecutionTraceDTO.from_pandas_series(
            execution_trace=first_wrong_step_trace_series, trace_words_lengths=trace_words_lengths
        )
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
        if (
            (first_wrong_step_trace.read_1_value != execution_trace.read_1_value)
            and (first_wrong_step_trace.read_1_address == execution_trace.read_1_address)
            or (first_wrong_step_trace.read_2_value != execution_trace.read_2_value)
            and (first_wrong_step_trace.read_2_address == execution_trace.read_2_address)
        ):
            if int(static_addresses.input.address, 16) <= int(
                first_wrong_step_trace.read_1_address, 16
            ) and int(
                static_addresses.input.address, 16
            ) + bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words * 4 > int(
                first_wrong_step_trace.read_1_address, 16
            ):
                return (
                    TriggerReadInput1EquivocationChallengeTransactionService,
                    TransactionVerifierStepType.TRIGGER_INPUT_EQUIVOCATION_CHALLENGE_1,
                )
            if int(static_addresses.input.address, 16) <= int(
                first_wrong_step_trace.read_2_address, 16
            ) and int(
                static_addresses.input.address, 16
            ) + bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words * 4 > int(
                first_wrong_step_trace.read_2_address, 16
            ):
                return (
                    TriggerReadInput2EquivocationChallengeTransactionService,
                    TransactionVerifierStepType.TRIGGER_INPUT_EQUIVOCATION_CHALLENGE_2,
                )
        return None, None
