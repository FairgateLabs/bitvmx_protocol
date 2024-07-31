from dependency_injector import containers, providers

from bitvmx_protocol_library.bitvmx_protocol_definition.services.generate_prover_public_keys_service import (
    GenerateProverPublicKeysService,
)
from bitvmx_protocol_library.script_generation.services.scripts_dict_generator_service import (
    ScriptsDictGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.services.generate_signatures_service import (
    GenerateSignaturesService,
)
from bitvmx_protocol_library.transaction_generation.services.signature_verification.verify_verifier_signatures_service import (
    VerifyVerifierSignaturesService,
)
from bitvmx_protocol_library.transaction_generation.services.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
    transaction_info_service,
)
from blockchain_query_services.services.mutinynet_api.faucet_service import FaucetService
from prover_app.domain.v1.setup.controllers.create_setup_controller import CreateSetupController


class CreateSetupControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        CreateSetupController,
        broadcast_transaction_service=broadcast_transaction_service,
        transaction_info_service=transaction_info_service,
        transaction_generator_from_public_keys_service=TransactionGeneratorFromPublicKeysService(),
        faucet_service=FaucetService(),
        scripts_dict_generator_service=ScriptsDictGeneratorService(),
        generate_prover_public_keys_service_class=GenerateProverPublicKeysService,
        verify_verifier_signatures_service_class=VerifyVerifierSignaturesService,
        generate_signatures_service_class=GenerateSignaturesService,
    )
