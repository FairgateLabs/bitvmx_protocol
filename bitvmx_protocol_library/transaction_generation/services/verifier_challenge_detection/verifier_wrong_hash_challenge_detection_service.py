from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_wrong_hash_challenge_transaction_service import (
    TriggerWrongHashChallengeTransactionService,
)
from bitvmx_protocol_library.winternitz_keys_handling.functions.signature_functions import (
    byte_sha256,
)


class VerifierWrongHashChallengeDetectionService:

    def __init__(self):
        self.base_path = "verifier_files/"

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace
        if bitvmx_protocol_verifier_dto.first_wrong_step > 0:
            previous_step_hash = bitvmx_protocol_verifier_dto.published_hashes_dict[
                bitvmx_protocol_verifier_dto.first_wrong_step - 1
            ]
        else:
            previous_step_hash = byte_sha256(bytes.fromhex("ff")).hex().zfill(64)
        write_trace = (
            execution_trace.write_address
            + execution_trace.write_value
            + execution_trace.write_PC_address
            + execution_trace.write_micro
        )
        next_step_hash = (
            byte_sha256(bytes.fromhex(previous_step_hash + write_trace))
            .hex()
            .zfill(
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash
            )
        )
        print(
            "Checking correct hash challenge. Previous hash (correct): "
            + previous_step_hash
            + ", write trace: "
            + write_trace
            + ", next hash(incorrect): "
            + next_step_hash
        )
        # This should be erased when the script works
        if (
            bitvmx_protocol_verifier_dto.published_hashes_dict[
                bitvmx_protocol_verifier_dto.first_wrong_step
            ]
            != next_step_hash
        ):
            return (
                TriggerWrongHashChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_WRONG_HASH_CHALLENGE,
            )
        return None, None
