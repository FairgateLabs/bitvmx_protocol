from dependency_injector import containers, providers

from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.publish_choice_search_transaction_service import (
    PublishChoiceSearchTransactionService,
)
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_protocol_transaction_service import (
    TriggerProtocolTransactionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection_service import (
    VerifierChallengeDetectionService,
)
from verifier_app.config import protocol_properties
from verifier_app.dependency_injection.persistence.bitvmx_protocol_setup_properties_dto_persistences import (
    BitVMXProtocolSetupPropertiesDTOPersistences,
)
from verifier_app.dependency_injection.persistence.bitvmx_protocol_verifier_private_dto_persistences import (
    BitVMXProtocolVerifierPrivateDTOPersistences,
)
from verifier_app.domain.controllers.v1.next_step.publish_next_step_controller import (
    PublishNextStepController,
)


class PublishNextStepControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        PublishNextStepController,
        trigger_protocol_transaction_service=TriggerProtocolTransactionService(),
        verifier_challenge_detection_service=VerifierChallengeDetectionService(),
        publish_choice_search_transaction_service_class=PublishChoiceSearchTransactionService,
        protocol_properties=protocol_properties,
        common_protocol_properties=common_protocol_properties,
        bitvmx_protocol_verifier_private_dto_persistence=BitVMXProtocolVerifierPrivateDTOPersistences.bitvmx,
        bitvmx_protocol_setup_properties_dto_persistence=BitVMXProtocolSetupPropertiesDTOPersistences.bitvmx,
    )
