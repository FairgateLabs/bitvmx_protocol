from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_wrong_halt_step_challenge_transaction_service import (
    TriggerWrongHaltStepChallengeTransactionService,
)


class VerifierWrongHaltStepChallengeDetectionService:
    def __init__(self):
        self.base_path = "verifier_files/"

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        published_execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace
        published_step = int(
            "".join(
                map(
                    lambda x: bin(x)[2:].zfill(
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    ),
                    bitvmx_protocol_verifier_dto.search_choices,
                )
            ),
            2,
        )
        published_halt_step = int(bitvmx_protocol_verifier_dto.published_halt_step, 16)
        if published_step != published_halt_step and published_execution_trace.is_halt():
            return (
                TriggerWrongHaltStepChallengeTransactionService,
                TransactionVerifierStepType.TRIGGER_WRONG_HALT_STEP_CHALLENGE,
            )
        return None, None
