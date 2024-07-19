from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from mutinyet_api.services.transaction_info_service import TransactionInfoService
from scripts.services.trigger_challenge_execution_script_generator_service import (
    TriggerChallengeExecutionScriptGeneratorService,
)
from winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)


class TriggerWrongHashChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.transaction_info_service = TransactionInfoService()
        self.broadcast_transaction_service = BroadcastTransactionService()
        self.verifier_challenge_execution_script_generator_service = (
            TriggerChallengeExecutionScriptGeneratorService()
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            verifier_private_key
        )

    def __call__(self, protocol_dict):
        raise Exception("Trigger wrong hash challenge not implemented")
