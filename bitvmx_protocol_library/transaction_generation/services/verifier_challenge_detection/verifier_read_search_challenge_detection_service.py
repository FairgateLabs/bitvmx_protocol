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
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.publish_choice_read_search_transaction_service import (
    PublishChoiceReadSearchTransactionService,
)


class VerifierReadSearchChallengeDetectionService:

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
        )
        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )
        trace = ExecutionTraceDTO.from_pandas_series(
            execution_trace=first_wrong_step_trace_series, trace_words_lengths=trace_words_lengths
        )
        if (
            trace.read_1_address != published_execution_trace.read_1_address
            or trace.read_2_address != published_execution_trace.read_2_address
            or trace.read_1_value != published_execution_trace.read_1_value
            or trace.read_2_value != published_execution_trace.read_2_value
        ):
            return (
                PublishChoiceReadSearchTransactionService,
                TransactionVerifierStepType.READ_SEARCH_STEP_CHOICE,
            )
        return None, None
