from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork

if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
    from blockchain_query_services.mutinynet_api.services.broadcast_transaction_service import (
        BroadcastTransactionService,
    )
    from blockchain_query_services.mutinynet_api.services.transaction_info_service import (
        TransactionInfoService,
    )
elif common_protocol_properties.network == BitcoinNetwork.TESTNET:
    from blockchain_query_services.testnet_api.services import (
        TransactionInfoService,
    )
elif common_protocol_properties.network == BitcoinNetwork.MAINNET:
    from blockchain_query_services.mainnet_api.services.transaction_info_service import (
        TransactionInfoService,
    )
from scripts.services.trigger_generic_challenge_script_generator_service import (
    TriggerGenericChallengeScriptGeneratorService,
)
from winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)


class TriggerWrongHashChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.transaction_info_service = TransactionInfoService()
        self.broadcast_transaction_service = BroadcastTransactionService()
        self.verifier_challenge_execution_script_generator_service = (
            TriggerGenericChallengeScriptGeneratorService()
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            verifier_private_key
        )

    def __call__(self, protocol_dict):
        raise Exception("Trigger wrong hash challenge not implemented")
