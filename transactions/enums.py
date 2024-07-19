from enum import Enum


class TransactionProverStepType(Enum):
    HASH_RESULT = "hash_result"
    SEARCH_STEP_HASH = "search_step_hash"
    TRACE = "trace"
    EXECUTION_CHALLENGE = "execution_challenge"


class TransactionVerifierStepType(Enum):
    TRIGGER_PROTOCOL = "trigger_protocol"
    SEARCH_STEP_CHOICE = "search_step_choice"
    TRIGGER_EXECUTION_CHALLENGE = "trigger_challenge"
