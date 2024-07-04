from enum import Enum


class TransactionStepType(Enum):
    HASH_RESULT = "hash_result"
    TRIGGER_PROTOCOL = "trigger_protocol"
    SEARCH_STEP_HASH = "search_step_hash"
    SEARCH_STEP_CHOICE = "search_step_choice"
    TRACE = "trace"
    TRIGGER_CHALLENGE = "trigger_challenge"
