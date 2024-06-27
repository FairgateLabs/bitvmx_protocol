from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_execution.execution_trace_generation_service import ExecutionTraceGenerationService
from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from scripts.services.trigger_protocol_script_generator_service import (
    TriggerProtocolScriptGeneratorService,
)


class TriggerProtocolTransactionService:

    def __init__(self):
        self.broadcast_transaction_service = BroadcastTransactionService()
        self.execution_trace_generation_service = ExecutionTraceGenerationService("verifier_files/")

    def __call__(self, protocol_dict):
        self.execution_trace_generation_service(protocol_dict)

        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
        trigger_protocol_tx = protocol_dict["trigger_protocol_tx"]
        trigger_protocol_signatures = protocol_dict["trigger_protocol_signatures"]

        trigger_protocol_script_generator = TriggerProtocolScriptGeneratorService()
        trigger_protocol_script = trigger_protocol_script_generator(protocol_dict["public_keys"])
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
