from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from scripts.services.trigger_protocol_script_generator_service import (
    TriggerProtocolScriptGeneratorService,
)


class TriggerProtocolTransactionService:

    def __init__(self):
        self.broadcast_transaction_service = BroadcastTransactionService()
        self.execution_trace_generation_service = ExecutionTraceGenerationService("verifier_files/")

    def __call__(self, protocol_dict, hash_result_transaction):
        hash_result_witness = hash_result_transaction.inputs[0].witness
        public_keys = protocol_dict["public_keys"]
        amount_of_nibbles_hash = protocol_dict["amount_of_nibbles_hash"]
        hash_witness_portion = hash_result_witness[
            len(public_keys) : len(public_keys) + 2 * amount_of_nibbles_hash
        ]
        published_result_hash = "".join(
            [
                (hex_repr[1] if len(hex_repr) == 2 else "0")
                for hex_repr in reversed(hash_witness_portion[1::2])
            ]
        )

        execution_result = self.execution_trace_generation_service(protocol_dict)

        if not execution_result[-1]["step_hash"] == published_result_hash:
            protocol_dict["search_hashes"][len(execution_result) - 1] = published_result_hash
            destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
            trigger_protocol_tx = protocol_dict["trigger_protocol_tx"]
            trigger_protocol_signatures = protocol_dict["trigger_protocol_signatures"]

            trigger_protocol_script_generator = TriggerProtocolScriptGeneratorService()
            trigger_protocol_script = trigger_protocol_script_generator(
                protocol_dict["public_keys"]
            )
            trigger_protocol_script_address = destroyed_public_key.get_taproot_address(
                [[trigger_protocol_script]]
            )

            trigger_protocol_control_block = ControlBlock(
                destroyed_public_key,
                scripts=[[trigger_protocol_script]],
                index=0,
                is_odd=trigger_protocol_script_address.is_odd(),
            )

            trigger_protocol_witness = []
            trigger_protocol_tx.witnesses.append(
                TxWitnessInput(
                    trigger_protocol_witness
                    + trigger_protocol_signatures
                    + [
                        trigger_protocol_script.to_hex(),
                        trigger_protocol_control_block.to_hex(),
                    ]
                )
            )

            self.broadcast_transaction_service(transaction=trigger_protocol_tx.serialize())
            print("Trigger protocol transaction: " + trigger_protocol_tx.get_txid())
            return trigger_protocol_tx

        raise Exception("Protocol aborted at trigger step because both hashes are equal")
