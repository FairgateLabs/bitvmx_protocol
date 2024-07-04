from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from mutinyet_api.services.transaction_info_service import TransactionInfoService
from scripts.services.verifier_challenge_execution_script_generator_service import (
    VerifierChallengeExecutionScriptGeneratorService,
)


class TriggerExeecutionChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.transaction_info_service = TransactionInfoService()
        self.broadcast_transaction_service = BroadcastTransactionService()
        self.verifier_challenge_execution_script_generator_service = (
            VerifierChallengeExecutionScriptGeneratorService()
        )

    def __call__(self, protocol_dict):
        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
        trace_tx_id = protocol_dict["trace_tx"].get_txid()
        trace_transaction_info = self.transaction_info_service(trace_tx_id)
        previous_trace_witness = trace_transaction_info.inputs[0].witness

        trigger_challenge_witness = []

        # Ugly hardcoding here that should be computed somehow but it depends a lot on the structure of the
        # previous script
        # -> Make static call that gets checked when the script gets generated
        trigger_challenge_witness += previous_trace_witness[10:246]

        trigger_execution_challenge_tx = protocol_dict["trigger_execution_challenge_tx"]
        trace_prover_public_keys = protocol_dict["trace_prover_public_keys"]
        trace_verifier_public_keys = protocol_dict["trace_verifier_public_keys"]
        signature_public_keys = protocol_dict["public_keys"]
        trace_words_lengths = protocol_dict["trace_words_lengths"]
        amount_of_bits_per_digit_checksum = protocol_dict["amount_of_bits_per_digit_checksum"]

        consumed_items = 0
        for i in range(len(trace_verifier_public_keys)):
            current_public_keys = trace_verifier_public_keys[i]
            current_length = trace_words_lengths[i]
            current_witness = trigger_challenge_witness[
                len(trigger_challenge_witness)
                - (len(current_public_keys) * 2 + consumed_items) : len(trigger_challenge_witness)
                - consumed_items
            ]
            consumed_items += len(current_public_keys) * 2
            current_witness_values = current_witness[1:2*current_length:2]
            current_digits = list(map(lambda elem: elem[1] if len(elem) > 0 else "0", current_witness_values))
            current_value = "".join(reversed(current_digits))

        # ['00', '800000c8', '800002c4', 'e07ffffc', '06112623', '00', '800000c4', '00000001', '800002c4', 'f0000004', '00000002', 'e07fff90', 'f0000008']

        trigger_execution_script = self.verifier_challenge_execution_script_generator_service(
            trace_prover_public_keys,
            trace_verifier_public_keys,
            signature_public_keys,
            trace_words_lengths,
            amount_of_bits_per_digit_checksum,
        )

        # TODO: we should load this address from protocol dict as we add more challenges
        challenge_scripts = [[trigger_execution_script]]
        challenge_scripts_address = destroyed_public_key.get_taproot_address(challenge_scripts)

        challenge_scripts_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[trigger_execution_script]],
            index=0,
            is_odd=challenge_scripts_address.is_odd(),
        )

        trigger_execution_challenge_tx.witnesses.append(
            TxWitnessInput(
                # trace_signatures
                trigger_challenge_witness
                + [
                    trigger_execution_script.to_hex(),
                    challenge_scripts_control_block.to_hex(),
                ]
            )
        )

        self.broadcast_transaction_service(transaction=trigger_execution_challenge_tx.serialize())
        print(
            "Trigger execution challenge transaction: " + trigger_execution_challenge_tx.get_txid()
        )
        return trigger_execution_challenge_tx
