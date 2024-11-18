from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_last_hash_equivocation_challenge_transaction_service import (
    TriggerLastHashEquivocationChallengeTransactionService,
)


class VerifierLastHashEquivocationChallengeDetectionService:

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        first_wrong_step = bitvmx_protocol_verifier_dto.first_wrong_step
        published_halt_step = int(bitvmx_protocol_verifier_dto.published_halt_step, 16)
        published_halt_hash = bitvmx_protocol_verifier_dto.published_halt_hash
        first_wrong_hash = bitvmx_protocol_verifier_dto.published_hashes_dict[first_wrong_step]
        if published_halt_step == first_wrong_step and published_halt_hash != first_wrong_hash:
            return (
                TriggerLastHashEquivocationChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_LAST_HASH_EQUIVOCATION_CHALLENGE,
            )
        return None, None
