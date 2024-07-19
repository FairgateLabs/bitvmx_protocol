import pandas as pd

from transactions.enums import TransactionVerifierStepType
from transactions.publication_services.trigger_execution_challenge_transaction_service import (
    TriggerExecutionChallengeTransactionService,
)


class VerifierExecutionChallengeDetectionService:

    def __init__(self):
        self.base_path = "verifier_files/"

    def __call__(self, protocol_dict):
        execution_trace = protocol_dict["published_execution_trace"]
        trace_df = pd.read_csv(
            self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", sep=";"
        )
        first_wrong_step = protocol_dict["first_wrong_step"]
        if (
            hex(int(trace_df.iloc[first_wrong_step]["write_pc"]))[2:].zfill(8)
            != execution_trace.write_PC_address
            or hex(int(trace_df.iloc[first_wrong_step]["write_micro"]))[2:].zfill(2)
            != execution_trace.write_micro
            or hex(int(trace_df.iloc[first_wrong_step]["write_value"]))[2:].zfill(8)
            != execution_trace.write_value
            or hex(int(trace_df.iloc[first_wrong_step]["write_address"]))[2:].zfill(8)
            != execution_trace.write_address
        ):
            # No need to check the opcode, the instruction is mapped to the address
            return (
                TriggerExecutionChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_EXECUTION_CHALLENGE,
            )

        return None, None
