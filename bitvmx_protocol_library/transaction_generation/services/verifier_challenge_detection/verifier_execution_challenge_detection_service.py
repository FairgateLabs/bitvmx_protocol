from bitvmx_protocol_library.bitvmx_execution.entities.execution_trace_dto import ExecutionTraceDTO
from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_execution_challenge_transaction_service import (
    TriggerExecutionChallengeTransactionService,
)


class VerifierExecutionChallengeDetectionService:

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
        if (
            first_wrong_step_trace.write_PC_address != execution_trace.write_PC_address
            or first_wrong_step_trace.write_micro != execution_trace.write_micro
            or first_wrong_step_trace.write_value != execution_trace.write_value
            or first_wrong_step_trace.write_address != execution_trace.write_address
            or first_wrong_step_trace.read_1_address != execution_trace.read_1_address
            or first_wrong_step_trace.read_2_address != execution_trace.read_2_address
        ):
            # No need to check the opcode, the instruction is mapped to the address
            return (
                TriggerExecutionChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_EXECUTION_CHALLENGE,
            )

        return None, None
