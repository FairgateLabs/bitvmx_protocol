from typing import List

from bitcoinutils.transactions import Transaction, TxWitnessInput
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
from bitvmx_protocol_library.script_generation.services.script_generation.hash_result_script_generator_service import (
    HashResultScriptGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_transactions_dto import (
    BitVMXTransactionsDTO,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


def _get_result_hash_value(last_step_trace) -> List[int]:
    hash_value = last_step_trace["step_hash"]
    print(hash_value)
    hash_result_split_number = []
    for letter in hash_value:
        hash_result_split_number.append(int(letter, 16))
    return hash_result_split_number


class PublishHashTransactionService:

    def __init__(self, prover_private_key):
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            prover_private_key
        )
        self.hash_result_script_generator = HashResultScriptGeneratorService()
        self.execution_trace_generation_service = ExecutionTraceGenerationService("prover_files/")
        self.execution_trace_query_service = ExecutionTraceQueryService("prover_files/")

    def __call__(
        self,
        protocol_dict,
        setup_uuid: str,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_transactions_dto: BitVMXTransactionsDTO,
    ) -> Transaction:

        hash_result_signatures = protocol_dict["hash_result_signatures"]

        self.execution_trace_generation_service(setup_uuid=setup_uuid)
        last_step_trace = self.execution_trace_query_service(
            setup_uuid, bitvmx_protocol_properties_dto.amount_of_trace_steps - 1
        )
        hash_result_split_number = _get_result_hash_value(last_step_trace)

        hash_result_witness = []
        hash_result_witness += self.generate_witness_from_input_nibbles_service(
            step=1,
            case=0,
            input_numbers=hash_result_split_number,
            bits_per_digit_checksum=bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        bitvmx_prover_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_prover_winternitz_public_keys_dto"
        ]

        hash_result_script = self.hash_result_script_generator(
            protocol_dict["public_keys"],
            bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys,
            bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        hash_result_script_address = (
            bitvmx_protocol_setup_properties_dto.unspendable_public_key.get_taproot_address(
                [[hash_result_script]]
            )
        )

        hash_result_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=[[hash_result_script]],
            index=0,
            is_odd=hash_result_script_address.is_odd(),
        )

        bitvmx_transactions_dto.hash_result_tx.witnesses.append(
            TxWitnessInput(
                hash_result_signatures
                + hash_result_witness
                + [
                    hash_result_script.to_hex(),
                    hash_result_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_transactions_dto.hash_result_tx.serialize()
        )
        print(
            "Hash result revelation transaction: "
            + bitvmx_transactions_dto.hash_result_tx.get_txid()
        )
        return bitvmx_transactions_dto.hash_result_tx
