from enum import Enum


class TransactionProverStepType(Enum):
    HASH_RESULT = "hash_result"
    SEARCH_STEP_HASH = "search_step_hash"
    SEARCH_READ_STEP_HASH = "search_read_step_hash"
    TRACE = "trace"
    EXECUTION_CHALLENGE = "execution_challenge"


class TransactionVerifierStepType(Enum):
    TRIGGER_PROTOCOL = "trigger_protocol"
    SEARCH_STEP_CHOICE = "search_step_choice"
    READ_SEARCH_STEP_CHOICE = "read_search_step_choice"
    TRIGGER_EXECUTION_CHALLENGE = "trigger_challenge"
    TRIGGER_WRONG_HASH_CHALLENGE = "trigger_wrong_hash"
