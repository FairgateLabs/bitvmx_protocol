from enum import Enum


class TransactionProverStepType(Enum):
    HASH_RESULT = "hash_result"
    SEARCH_STEP_HASH = "search_step_hash"
    SEARCH_READ_STEP_HASH = "search_read_step_hash"
    TRACE = "trace"
    EXECUTION_CHALLENGE = "execution_challenge"
    READ_TRACE = "read_trace"
    TRIGGER_WRONG_TRACE_STEP = "trigger_wrong_trace_step"
    TRIGGER_WRONG_READ_TRACE_STEP = "trigger_wrong_read_trace_step"


class TransactionVerifierStepType(Enum):
    TRIGGER_PROTOCOL = "trigger_protocol"
    SEARCH_STEP_CHOICE = "search_step_choice"
    READ_SEARCH_STEP_CHOICE = "read_search_step_choice"
    TRIGGER_EXECUTION_CHALLENGE = "trigger_challenge"
    TRIGGER_WRONG_HASH_CHALLENGE = "trigger_wrong_hash"
    TRIGGER_INPUT_EQUIVOCATION_CHALLENGE_1 = "trigger_input_equivocation_1"
    TRIGGER_INPUT_EQUIVOCATION_CHALLENGE_2 = "trigger_input_equivocation_2"
    TRIGGER_CONSTANT_EQUIVOCATION_CHALLENGE_1 = "trigger_constant_equivocation_1"
    TRIGGER_CONSTANT_EQUIVOCATION_CHALLENGE_2 = "trigger_constant_equivocation_2"
    TRIGGER_WRONG_PROGRAM_COUNTER = "trigger_wrong_program_counter"
    TRIGGER_WRONG_HASH_READ_SEARCH_CHALLENGE = "trigger_wrong_hash_read_challenge"
    TRIGGER_WRONG_LATTER_STEP_CHALLENGE_1 = "trigger_wrong_latter_step_challenge_1"
    TRIGGER_WRONG_LATTER_STEP_CHALLENGE_2 = "trigger_wrong_latter_step_challenge_2"
    TRIGGER_WRONG_VALUE_ADDRESS_READ_CHALLENGE_1 = "trigger_wrong_value_address_read_challenge_1"
    TRIGGER_WRONG_VALUE_ADDRESS_READ_CHALLENGE_2 = "trigger_wrong_value_address_read_challenge_2"
    TRIGGER_WRONG_HALT_STEP_CHALLENGE = "trigger_wrong_halt_step_challenge"
    TRIGGER_NO_HALT_IN_HALT_STEP_CHALLENGE = "trigger_no_halt_in_halt_step_challenge"
    TRIGGER_LAST_HASH_EQUIVOCATION_CHALLENGE = "trigger_last_hash_equivocation_challenge"
    TRIGGER_READ_SEARCH_EQUIVOCATION_CHALLENGE = "trigger_read_equivocation_challenge"
    TRIGGER_WRONG_INPUT_VALUE_CHALLENGE_1 = "trigger_wrong_input_value_challenge_1"
    TRIGGER_WRONG_INPUT_VALUE_CHALLENGE_2 = "trigger_wrong_input_value_challenge_2"
