from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
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
        setup_uuid: str,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace
        first_wrong_step_trace = self.execution_trace_query_service(
            setup_uuid=setup_uuid, index=bitvmx_protocol_verifier_dto.first_wrong_step
        )
        if (
            hex(int(first_wrong_step_trace["write_pc"]))[2:].zfill(8)
            != execution_trace.write_PC_address
            or hex(int(first_wrong_step_trace["write_micro"]))[2:].zfill(2)
            != execution_trace.write_micro
            or hex(int(first_wrong_step_trace["write_value"]))[2:].zfill(8)
            != execution_trace.write_value
            or hex(int(first_wrong_step_trace["write_address"]))[2:].zfill(8)
            != execution_trace.write_address
        ):
            # No need to check the opcode, the instruction is mapped to the address
            return (
                TriggerExecutionChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_EXECUTION_CHALLENGE,
            )

        return None, None
