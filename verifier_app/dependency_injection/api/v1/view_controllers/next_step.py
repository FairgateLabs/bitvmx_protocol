from dependency_injector import containers, providers

from bitvmx_protocol_library.transaction_generation.publication_services.verifier.publish_choice_search_transaction_service import (
    PublishChoiceSearchTransactionService,
)
from bitvmx_protocol_library.transaction_generation.publication_services.verifier.trigger_protocol_transaction_service import (
    TriggerProtocolTransactionService,
)
from bitvmx_protocol_library.transaction_generation.verifier_challenge_detection_service import (
    VerifierChallengeDetectionService,
)
from verifier_app.api.v1.next_step.crud.v1.view_controllers.post import NextStepPostViewControllerV1


class NextStepPostViewControllers(containers.DeclarativeContainer):
    v1 = providers.Singleton(
        NextStepPostViewControllerV1,
        trigger_protocol_transaction_service=TriggerProtocolTransactionService(),
        verifier_challenge_detection_service=VerifierChallengeDetectionService(),
        publish_choice_search_transaction_service_class=PublishChoiceSearchTransactionService,
    )
