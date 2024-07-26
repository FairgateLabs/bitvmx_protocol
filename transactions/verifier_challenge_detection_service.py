from bitvmx_execution.bo.execution_trace_bo import ExecutionTraceBO
from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork

if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
    from blockchain_query_services.mutinyet_api.services.transaction_info_service import (
        TransactionInfoService,
    )
elif common_protocol_properties.network == BitcoinNetwork.TESTNET:
    from blockchain_query_services.testnet_api.services import TransactionInfoService
elif common_protocol_properties.network == BitcoinNetwork.MAINNET:
    from blockchain_query_services.mainnet_api.services.transaction_info_service import (
        TransactionInfoService,
    )
from transactions.verifier_challenge_detection.verifier_execution_challenge_detection_service import (
    VerifierExecutionChallengeDetectionService,
)
from transactions.verifier_challenge_detection.verifier_wrong_hash_challenge_detection_service import (
    VerifierWrongHashChallengeDetectionService,
)


class VerifierChallengeDetectionService:
    def __init__(self):
        self.transaction_info_service = TransactionInfoService()
        self.verifier_challenge_detection_services = [
            VerifierWrongHashChallengeDetectionService(),
            VerifierExecutionChallengeDetectionService(),
        ]

    def __call__(self, protocol_dict):
        trace_tx_id = protocol_dict["trace_tx"].get_txid()
        trace_transaction_info = self.transaction_info_service(trace_tx_id)
        previous_trace_witness = trace_transaction_info.inputs[0].witness

        # Ugly hardcoding here that should be computed somehow but it depends a lot on the structure of the
        # previous script
        # -> Make static call that gets checked when the script gets generated
        prover_trace_witness = previous_trace_witness[10:246]
        protocol_dict["prover_trace_witness"] = prover_trace_witness

        trace_verifier_public_keys = protocol_dict["trace_verifier_public_keys"]
        trace_words_lengths = protocol_dict["trace_words_lengths"]

        consumed_items = 0
        trace_values = []
        for i in range(len(trace_verifier_public_keys)):
            current_public_keys = trace_verifier_public_keys[i]
            current_length = trace_words_lengths[i]
            current_witness = prover_trace_witness[
                len(prover_trace_witness)
                - (len(current_public_keys) * 2 + consumed_items) : len(prover_trace_witness)
                - consumed_items
            ]
            consumed_items += len(current_public_keys) * 2
            current_witness_values = current_witness[1 : 2 * current_length : 2]
            current_digits = list(
                map(lambda elem: elem[1] if len(elem) > 0 else "0", current_witness_values)
            )
            current_value = "".join(reversed(current_digits))
            trace_values.append(current_value)

        execution_trace = ExecutionTraceBO.from_trace_values_list(trace_values)
        protocol_dict["published_execution_trace"] = execution_trace

        amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]
        first_wrong_step = int(
            "".join(
                map(
                    lambda digit: bin(digit)[2:].zfill(amount_of_bits_wrong_step_search),
                    protocol_dict["search_choices"],
                )
            ),
            2,
        )
        protocol_dict["first_wrong_step"] = first_wrong_step

        for verifier_challenge_detection_service in self.verifier_challenge_detection_services:
            trigger_challenge_transaction_service, transaction_step_type = (
                verifier_challenge_detection_service(protocol_dict)
            )
            if (
                trigger_challenge_transaction_service is not None
                and transaction_step_type is not None
            ):
                return trigger_challenge_transaction_service, transaction_step_type

        raise Exception("No challenge detected")
