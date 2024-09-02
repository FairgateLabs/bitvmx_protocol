from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.publish_choice_read_search_transaction_service import (
    PublishChoiceReadSearchTransactionService,
)


class VerifierReadSearchChallengeDetectionService:

    def __init__(self):
        self.base_path = "verifier_files/"

    def __call__(
        self,
        setup_uuid: str,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        return (
            PublishChoiceReadSearchTransactionService,
            TransactionVerifierStepType.READ_SEARCH_STEP_CHOICE,
        )
