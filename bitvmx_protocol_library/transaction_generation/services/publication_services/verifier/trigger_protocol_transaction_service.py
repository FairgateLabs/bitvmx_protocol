from typing import Optional

from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock
from pydantic import BaseModel

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_protocol_script_generator_service import (
    TriggerProtocolScriptGeneratorService,
)
from bitvmx_protocol_library.winternitz_keys_handling.functions.witness_functions import (
    decrypt_first_item,
)
from blockchain_query_services.entities.transaction_info_service.transaction_info_bo import (
    TransactionInfoBO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class HashResultWitness(BaseModel):
    hash_result: str
    input_hex: Optional[str] = None
    halt_step: str


def _decompose_witness(
    hash_result_transaction: TransactionInfoBO,
    bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
) -> HashResultWitness:
    current_witness = hash_result_transaction.inputs[0].witness.copy()
    current_witness = current_witness[:-2]
    while len(current_witness[0]) == 128:
        current_witness = current_witness[1:]

    bits_per_digit_checksum = (
        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum
    )

    hash_result, remaining_witness = decrypt_first_item(
        witness=current_witness,
        amount_of_nibbles=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
        amount_of_bits_per_digit=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit,
        bits_per_digit_checksum=bits_per_digit_checksum,
    )
    halt_step, remaining_witness = decrypt_first_item(
        witness=remaining_witness,
        amount_of_nibbles=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
        amount_of_bits_per_digit=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit,
        bits_per_digit_checksum=bits_per_digit_checksum,
    )
    if (
        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        > 0
    ):
        input_hex = ""
        for i in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        ):
            next_input_hex, remaining_witness = decrypt_first_item(
                witness=remaining_witness,
                amount_of_nibbles=8,
                amount_of_bits_per_digit=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit,
                bits_per_digit_checksum=bits_per_digit_checksum,
            )
            input_hex += next_input_hex
    else:
        input_hex = None

    return HashResultWitness(hash_result=hash_result, halt_step=halt_step, input_hex=input_hex)


class TriggerProtocolTransactionService:

    def __init__(self):
        self.execution_trace_generation_service = ExecutionTraceGenerationService("verifier_files/")
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        hash_result_transaction,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        decomposed_witness = _decompose_witness(
            hash_result_transaction=hash_result_transaction,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        self.execution_trace_generation_service(
            setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid,
            input_hex=decomposed_witness.input_hex,
        )
        last_step_index = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_trace_steps
            - 1
        )

        last_step_trace = self.execution_trace_query_service(
            setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid,
            index=last_step_index,
            input_hex=decomposed_witness.input_hex,
        )

        bitvmx_protocol_verifier_dto.published_halt_step = decomposed_witness.halt_step[::-1]
        bitvmx_protocol_verifier_dto.input_hex = decomposed_witness.input_hex

        if not last_step_trace["step_hash"] == decomposed_witness.hash_result:
            bitvmx_protocol_verifier_dto.published_halt_hash = decomposed_witness.hash_result
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
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx.witnesses.append(
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
                transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx.serialize()
            )
            print(
                "Trigger protocol transaction: "
                + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx.get_txid()
            )
            return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx

        raise Exception("Protocol aborted at trigger step because both hashes are equal")
