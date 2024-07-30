from dependency_injector import containers, providers

from bitvmx_protocol_library.transaction_generation.publication_services.prover.execution_challenge_transaction_service import (
    ExecutionChallengeTransactionService,
)
from bitvmx_protocol_library.transaction_generation.publication_services.prover.publish_hash_search_transaction_service import (
    PublishHashSearchTransactionService,
)
from bitvmx_protocol_library.transaction_generation.publication_services.prover.publish_hash_transaction_service import (
    PublishHashTransactionService,
)
from bitvmx_protocol_library.transaction_generation.publication_services.prover.publish_trace_transaction_service import (
    PublishTraceTransactionService,
)
from blockchain_query_services.common.transaction_published_service import (
    TransactionPublishedService,
)
from prover_app.domain.v1.next_step.controllers.publish_next_step_controller import (
    PublishNextStepController,
)


class PublishNextStepControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        PublishNextStepController,
        transaction_published_service=TransactionPublishedService(),
        publish_hash_transaction_service_class=PublishHashTransactionService,
        publish_hash_search_transaction_service_class=PublishHashSearchTransactionService,
        publish_trace_transaction_service_class=PublishTraceTransactionService,
        execution_challenge_transaction_service_class=ExecutionChallengeTransactionService,
    )
