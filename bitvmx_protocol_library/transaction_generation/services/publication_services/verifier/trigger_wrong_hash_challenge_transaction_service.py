from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.trigger_generic_challenge_script_generator_service import (
    TriggerGenericChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_transactions_dto import (
    BitVMXTransactionsDTO,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)


class TriggerWrongHashChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.verifier_challenge_execution_script_generator_service = (
            TriggerGenericChallengeScriptGeneratorService()
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            verifier_private_key
        )

    def __call__(
        self,
        protocol_dict,
        bitvmx_transactions_dto: BitVMXTransactionsDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):
        raise Exception("Trigger wrong hash challenge not implemented")
