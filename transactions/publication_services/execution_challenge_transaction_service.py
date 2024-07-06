from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from mutinyet_api.services.transaction_info_service import TransactionInfoService
from scripts.services.execution_challenge_script_generator_service import (
    ExecutionChallengeScriptGeneratorService,
)


class ExecutionChallengeTransactionService:
    def __init__(self):
        self.transaction_info_service = TransactionInfoService()
        self.broadcast_transaction_service = BroadcastTransactionService()
        self.execution_challenge_script_generator_service = (
            ExecutionChallengeScriptGeneratorService()
        )

    def __call__(self, protocol_dict):
        trace_words_lengths = protocol_dict["trace_words_lengths"]
        trace_prover_public_keys = protocol_dict["trace_prover_public_keys"]
        trigger_execution_challenge_transaction = protocol_dict["trigger_execution_challenge_tx"]
        execution_challenge_signatures = protocol_dict["execution_challenge_signatures"]
        execution_challenge_tx = protocol_dict["execution_challenge_tx"]
        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
        signature_public_keys = protocol_dict["public_keys"]

        trigger_execution_challenge_published_transaction = self.transaction_info_service(
            trigger_execution_challenge_transaction.get_txid()
        )
        trigger_execution_challenge_witness = (
            trigger_execution_challenge_published_transaction.inputs[0].witness[2:]
        )
        verifier_keys_witness = []
        processed_values = 0
        for i in reversed(range(len(trace_words_lengths))):
            current_keys_length = len(trace_prover_public_keys[i])
            current_verifier_witness = trigger_execution_challenge_witness[
                processed_values
                + 2 * current_keys_length : processed_values
                + 4 * current_keys_length
            ]
            verifier_keys_witness.append(current_verifier_witness)
            processed_values += 4 * current_keys_length

        execution_challenge_script = self.execution_challenge_script_generator_service(
            signature_public_keys
        )
        execution_challenge_taptree = [[execution_challenge_script]]
        execution_challenge_script_address = destroyed_public_key.get_taproot_address(
            execution_challenge_taptree
        )

        execution_challenge_control_block = ControlBlock(
            destroyed_public_key,
            scripts=execution_challenge_taptree,
            index=0,
            is_odd=execution_challenge_script_address.is_odd(),
        )

        execution_challenge_tx.witnesses.append(
            TxWitnessInput(
                execution_challenge_signatures
                + [
                    execution_challenge_script.to_hex(),
                    execution_challenge_control_block.to_hex(),
                ]
            )
        )

        self.broadcast_transaction_service(transaction=execution_challenge_tx.serialize())
        print("Execution challenge transaction: " + execution_challenge_tx.get_txid())
        return execution_challenge_tx
