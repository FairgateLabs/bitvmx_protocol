from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.publication_services.trigger_wrong_hash_challenge_transaction_service import (
    TriggerWrongHashChallengeTransactionService,
)
from winternitz_keys_handling.functions.signature_functions import byte_sha256


class VerifierWrongHashChallengeDetectionService:

    def __init__(self):
        self.base_path = "verifier_files/"

    def __call__(self, protocol_dict):
        execution_trace = protocol_dict["published_execution_trace"]
        first_wrong_hash = protocol_dict["first_wrong_step"]
        previous_step_hash = protocol_dict["search_hashes"][first_wrong_hash - 1]
        write_trace = (
            execution_trace.write_address
            + execution_trace.write_value
            + execution_trace.write_PC_address
            + execution_trace.write_micro
        )
        next_step_hash = (
            byte_sha256(bytes.fromhex(previous_step_hash + write_trace)).hex().zfill(64)
        )
        if protocol_dict["search_hashes"][first_wrong_hash] != next_step_hash:
            return (
                TriggerWrongHashChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_WRONG_HASH_CHALLENGE,
            )
        return None, None
