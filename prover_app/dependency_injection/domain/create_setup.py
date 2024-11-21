from dependency_injector import containers, providers

from bitvmx_protocol_library.bitvmx_protocol_definition.services.public_keys_generation.generate_prover_public_keys_service import (
    GenerateProverPublicKeysService,
)
from bitvmx_protocol_library.script_generation.services.bitvmx_bitcoin_scripts_generator_service import (
    BitVMXBitcoinScriptsGeneratorService,
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
    faucet_service,
    transaction_info_service,
)
from prover_app.dependency_injection.persistences.bitvmx_protocol_prover_dto_persistences import (
    BitVMXProtocolProverDTOPersistences,
)
from prover_app.dependency_injection.persistences.bitvmx_protocol_prover_private_dto_persistences import (
    BitVMXProtocolProverPrivateDTOPersistences,
)
from prover_app.dependency_injection.persistences.bitvmx_protocol_setup_properties_dto_persistences import (
    BitVMXProtocolSetupPropertiesDTOPersistences,
)
from prover_app.domain.controllers.v1.setup.create_setup_controller import CreateSetupController


class CreateSetupControllers(containers.DeclarativeContainer):
    bitvmx_protocol = providers.Singleton(
        CreateSetupController,
        broadcast_transaction_service=broadcast_transaction_service,
        transaction_info_service=transaction_info_service,
        transaction_generator_from_public_keys_service=TransactionGeneratorFromPublicKeysService(),
        faucet_service=faucet_service,
        bitvmx_bitcoin_scripts_generator_service=BitVMXBitcoinScriptsGeneratorService(),
        generate_prover_public_keys_service_class=GenerateProverPublicKeysService,
        verify_verifier_signatures_service_class=VerifyVerifierSignaturesService,
        generate_signatures_service_class=GenerateSignaturesService,
        bitvmx_protocol_setup_properties_dto_persistence=BitVMXProtocolSetupPropertiesDTOPersistences.bitvmx,
        bitvmx_protocol_prover_private_dto_persistence=BitVMXProtocolProverPrivateDTOPersistences.bitvmx,
        bitvmx_protocol_prover_dto_persistence=BitVMXProtocolProverDTOPersistences.bitvmx,
    )
