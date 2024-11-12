from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_wrong_value_address_read_challenge_transaction_service import (
    TriggerWrongValueAddressRead1ChallengeTransactionService,
    TriggerWrongValueAddressRead2ChallengeTransactionService,
)


class VerifierWrongValueAddressReadChallengeDetectionService:
    def __init__(self):
        self.base_path = "verifier_files/"

    def __call__(self, setup_uuid: str, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO):
        read_execution_trace = bitvmx_protocol_verifier_dto.published_read_execution_trace
        execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace
        if int(execution_trace.read_1_last_step, 16) == int(
            "".join(
                map(lambda x: bin(x)[2:].zfill(2), bitvmx_protocol_verifier_dto.read_search_choices)
            ),
            2,
        ):
            if (
                read_execution_trace.write_address != execution_trace.read_1_address
                or read_execution_trace.write_value != execution_trace.read_1_value
            ):
                return (
                    TriggerWrongValueAddressRead1ChallengeTransactionService,
                    TransactionVerifierStepType.TRIGGER_WRONG_VALUE_ADDRESS_READ_CHALLENGE_1,
                )

        if int(execution_trace.read_2_last_step, 16) == int(
            "".join(
                map(lambda x: bin(x)[2:].zfill(2), bitvmx_protocol_verifier_dto.read_search_choices)
            ),
            2,
        ):
            if (
                read_execution_trace.write_address != execution_trace.read_2_address
                or read_execution_trace.write_value != execution_trace.read_2_value
            ):
                return (
                    TriggerWrongValueAddressRead2ChallengeTransactionService,
                    TransactionVerifierStepType.TRIGGER_WRONG_VALUE_ADDRESS_READ_CHALLENGE_2,
                )

        return None, None
