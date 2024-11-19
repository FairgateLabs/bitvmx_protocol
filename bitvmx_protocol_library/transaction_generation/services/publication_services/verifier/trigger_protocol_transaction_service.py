from typing import List, Optional

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
from bitvmx_protocol_library.winternitz_keys_handling.functions.witness_functions import (
    decrypt_first_item,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from blockchain_query_services.entities.transaction_info_service.transaction_info_bo import (
    TransactionInfoBO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class HashResultWitness(BaseModel):
    hash_result: str
    hash_result_witness: List[str]
    input_hex: Optional[str] = None
    input_hex_witness: Optional[List[str]] = None
    halt_step: str
    halt_step_witness: List[str]


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

    hash_result, hash_result_witness, remaining_witness = decrypt_first_item(
        witness=current_witness,
        amount_of_nibbles=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
        amount_of_bits_per_digit=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit,
        bits_per_digit_checksum=bits_per_digit_checksum,
    )
    halt_step, halt_step_witness, remaining_witness = decrypt_first_item(
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
        input_hex_witness = []
        for i in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        ):
            next_input_hex, next_input_hex_witness, remaining_witness = decrypt_first_item(
                witness=remaining_witness,
                amount_of_nibbles=8,
                amount_of_bits_per_digit=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit,
                bits_per_digit_checksum=bits_per_digit_checksum,
            )
            input_hex += next_input_hex
            input_hex_witness += next_input_hex_witness
    else:
        input_hex = None
        input_hex_witness = None

    return HashResultWitness(
        hash_result=hash_result,
        hash_result_witness=hash_result_witness,
        halt_step=halt_step,
        halt_step_witness=halt_step_witness,
        input_hex=input_hex,
        input_hex_witness=input_hex_witness,
    )


def _hex_to_witness(hex_str: str, length: int) -> List[int]:
    int_array = list(map(lambda x: int(x, 16), hex_str))
    while len(int_array) < length:
        int_array.insert(0, 0)
    return int_array


class TriggerProtocolTransactionService:

    def __init__(self, verifier_private_key):
        self.execution_trace_generation_service = ExecutionTraceGenerationService("verifier_files/")
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            verifier_private_key
        )

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

            trigger_protocol_taptree = (
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list.to_scripts_tree()
            )

            trigger_protocol_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list.get_taproot_address(
                public_key=bitvmx_protocol_setup_properties_dto.unspendable_public_key
            )

            current_index = 0
            current_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list[
                current_index
            ]

            trigger_protocol_control_block = ControlBlock(
                bitvmx_protocol_setup_properties_dto.unspendable_public_key,
                scripts=trigger_protocol_taptree,
                index=current_index,
                is_odd=trigger_protocol_script_address.is_odd(),
            )

            verifier_halt_step_witness = self.generate_witness_from_input_nibbles_service(
                step=2,
                case=0,
                input_numbers=list(
                    reversed(
                        _hex_to_witness(
                            hex_str=bitvmx_protocol_verifier_dto.published_halt_step,
                            length=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
                        )
                    )
                ),
                bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

            prover_halt_step_witness = decomposed_witness.halt_step_witness

            trigger_protocol_witness = prover_halt_step_witness + verifier_halt_step_witness

            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx.witnesses.append(
                TxWitnessInput(
                    trigger_protocol_witness
                    + trigger_protocol_signatures
                    + [
                        current_script.to_hex(),
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
