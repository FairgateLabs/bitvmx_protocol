from dependency_injector import containers, providers

from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.publish_choice_search_transaction_service import \
    PublishChoiceSearchTransactionService
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_protocol_transaction_service import \
    TriggerProtocolTransactionService
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection_service import (
    VerifierChallengeDetectionService,
)
from verifier_app.config import protocol_properties
from verifier_app.domain.v1.next_step.controllers.publish_next_step_controller import (
    PublishNextStepController,
)


class PublishNextStepControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        PublishNextStepController,
        trigger_protocol_transaction_service=TriggerProtocolTransactionService(),
        verifier_challenge_detection_service=VerifierChallengeDetectionService(),
        publish_choice_search_transaction_service_class=PublishChoiceSearchTransactionService,
        protocol_properties=protocol_properties,
    )
