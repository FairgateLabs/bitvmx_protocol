from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_wrong_hash_read_challenge_transaction_service import (
    TriggerWrongHashReadChallengeTransactionService,
)
from bitvmx_protocol_library.winternitz_keys_handling.functions.signature_functions import (
    byte_sha256,
)


class VerifierWrongHashReadChallengeDetectionService:
    def __init__(self):
        self.base_path = "verifier_files/"

    def __call__(self, setup_uuid: str, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO):
        read_execution_trace = bitvmx_protocol_verifier_dto.published_read_execution_trace
        if bitvmx_protocol_verifier_dto.read_revealed_step > 0:
            previous_step_hash = bitvmx_protocol_verifier_dto.published_read_hashes_dict[
                bitvmx_protocol_verifier_dto.read_revealed_step - 1
            ]
        else:
            previous_step_hash = byte_sha256(bytes.fromhex("ff")).hex().zfill(64)
        write_trace = (
            read_execution_trace.write_address
            + read_execution_trace.write_value
            + read_execution_trace.write_PC_address
            + read_execution_trace.write_micro
        )
        next_step_hash = (
            byte_sha256(bytes.fromhex(previous_step_hash + write_trace)).hex().zfill(64)
        )
        if (
            next_step_hash
            != bitvmx_protocol_verifier_dto.published_read_hashes_dict[
                bitvmx_protocol_verifier_dto.read_revealed_step
            ]
        ):
            return (
                TriggerWrongHashReadChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_WRONG_HASH_READ_SEARCH_CHALLENGE,
            )
        return None, None
