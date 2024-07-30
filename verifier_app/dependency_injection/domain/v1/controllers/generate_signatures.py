from dependency_injector import containers, providers

from bitvmx_protocol_library.script_generation.services.scripts_dict_generator_service import (
    ScriptsDictGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.generate_signatures_service import (
    GenerateSignaturesService,
)
from bitvmx_protocol_library.transaction_generation.signatures.verify_prover_signatures_service import (
    VerifyProverSignaturesService,
)
from bitvmx_protocol_library.transaction_generation.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from verifier_app.domain.v1.signatures.controllers.generate_signatures_controller import (
    GenerateSignaturesController,
)


class GenerateSignaturesControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        GenerateSignaturesController,
        scripts_dict_generator_service=ScriptsDictGeneratorService(),
        transaction_generator_from_public_keys_service=TransactionGeneratorFromPublicKeysService(),
        generate_signatures_service_class=GenerateSignaturesService,
        verify_prover_signatures_service_class=VerifyProverSignaturesService,
    )
