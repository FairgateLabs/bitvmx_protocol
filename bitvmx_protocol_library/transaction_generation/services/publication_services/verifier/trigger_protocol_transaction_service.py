from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.trigger_protocol_script_generator_service import (
    TriggerProtocolScriptGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_transactions_dto import (
    BitVMXTransactionsDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class TriggerProtocolTransactionService:

    def __init__(self):
        self.execution_trace_generation_service = ExecutionTraceGenerationService("verifier_files/")
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        hash_result_transaction,
        bitvmx_transactions_dto: BitVMXTransactionsDTO,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        hash_result_witness = hash_result_transaction.inputs[0].witness

        hash_witness_portion = hash_result_witness[
            len(bitvmx_protocol_setup_properties_dto.signature_public_keys) : len(
                bitvmx_protocol_setup_properties_dto.signature_public_keys
            )
            + 2 * bitvmx_protocol_properties_dto.amount_of_nibbles_hash
        ]
        published_result_hash = "".join(
            [
                (hex_repr[1] if len(hex_repr) == 2 else "0")
                for hex_repr in reversed(hash_witness_portion[1::2])
            ]
        )

        self.execution_trace_generation_service(bitvmx_protocol_setup_properties_dto.setup_uuid)
        last_step_index = bitvmx_protocol_properties_dto.amount_of_trace_steps - 1
        last_step_trace = self.execution_trace_query_service(
            setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid, index=last_step_index
        )

        if not last_step_trace["step_hash"] == published_result_hash:
            bitvmx_protocol_verifier_dto.published_hashes_dict[last_step_index] = (
                published_result_hash
            )
            trigger_protocol_signatures = bitvmx_protocol_verifier_dto.trigger_protocol_signatures

            trigger_protocol_script_generator = TriggerProtocolScriptGeneratorService()
            trigger_protocol_script = trigger_protocol_script_generator(
                signature_public_keys=bitvmx_protocol_setup_properties_dto.signature_public_keys
            )
            trigger_protocol_script_address = (
                bitvmx_protocol_setup_properties_dto.unspendable_public_key.get_taproot_address(
                    [[trigger_protocol_script]]
                )
            )

            trigger_protocol_control_block = ControlBlock(
                bitvmx_protocol_setup_properties_dto.unspendable_public_key,
                scripts=[[trigger_protocol_script]],
                index=0,
                is_odd=trigger_protocol_script_address.is_odd(),
            )

            trigger_protocol_witness = []
            bitvmx_transactions_dto.trigger_protocol_tx.witnesses.append(
                TxWitnessInput(
                    trigger_protocol_witness
                    + trigger_protocol_signatures
                    + [
                        trigger_protocol_script.to_hex(),
                        trigger_protocol_control_block.to_hex(),
                    ]
                )
            )

            broadcast_transaction_service(
                transaction=bitvmx_transactions_dto.trigger_protocol_tx.serialize()
            )
            print(
                "Trigger protocol transaction: "
                + bitvmx_transactions_dto.trigger_protocol_tx.get_txid()
            )
            return bitvmx_transactions_dto.trigger_protocol_tx

        raise Exception("Protocol aborted at trigger step because both hashes are equal")
