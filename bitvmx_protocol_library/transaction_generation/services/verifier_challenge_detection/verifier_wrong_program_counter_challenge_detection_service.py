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
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_wrong_program_counter_challenge_transaction_service import (
    TriggerWrongProgramCounterChallengeTransactionService,
)


class VerifierWrongProgramCounterChallengeDetectionService:

    def __init__(self):
        self.base_path = "verifier_files/"
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        published_execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace
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
        first_wrong_trace = ExecutionTraceDTO.from_pandas_series(
            execution_trace=first_wrong_step_trace_series, trace_words_lengths=trace_words_lengths
        )
        # last_correct_step_trace_series = self.execution_trace_query_service(
        #     setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid,
        #     index=bitvmx_protocol_verifier_dto.first_wrong_step - 1,
        #     input_hex=bitvmx_protocol_verifier_dto.input_hex,
        # )
        # last_correct_trace = ExecutionTraceDTO.from_pandas_series(
        #     execution_trace=last_correct_step_trace_series, trace_words_lengths=trace_words_lengths
        # )

        if (
            published_execution_trace.read_PC_address != first_wrong_trace.read_PC_address
            or published_execution_trace.read_micro != first_wrong_trace.read_micro
        ):
            # assert first_wrong_trace.read_PC_address == last_correct_trace.write_PC_address
            # assert first_wrong_trace.read_micro == last_correct_trace.write_micro
            return (
                TriggerWrongProgramCounterChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_WRONG_PROGRAM_COUNTER,
            )
        return None, None
