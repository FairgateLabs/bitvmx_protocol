from enum import Enum


class TransactionProverStepType(Enum):
    HASH_RESULT = "hash_result"
    SEARCH_STEP_HASH = "search_step_hash"
    SEARCH_READ_STEP_HASH = "search_read_step_hash"
    TRACE = "trace"
    EXECUTION_CHALLENGE = "execution_challenge"
    READ_TRACE = "read_trace"


class TransactionVerifierStepType(Enum):
    TRIGGER_PROTOCOL = "trigger_protocol"
    SEARCH_STEP_CHOICE = "search_step_choice"
    READ_SEARCH_STEP_CHOICE = "read_search_step_choice"
    TRIGGER_EXECUTION_CHALLENGE = "trigger_challenge"
    TRIGGER_WRONG_HASH_CHALLENGE = "trigger_wrong_hash"
    TRIGGER_INPUT_EQUIVOCATION_CHALLENGE_1 = "trigger_input_equivocation_1"
    TRIGGER_INPUT_EQUIVOCATION_CHALLENGE_2 = "trigger_input_equivocation_2"
    TRIGGER_READ_SEARCH_CHALLENGE = "trigger_read_search_challenge"
