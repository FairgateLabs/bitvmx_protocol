from typing import Dict, List

from bitcoinutils.transactions import Transaction, TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_prover_dto import (
    BitVMXProtocolProverDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.hash_result_script_generator_service import (
    HashResultScriptGeneratorService,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


def _get_result_hash_value(last_step_trace: Dict) -> List[int]:
    hash_value = last_step_trace["step_hash"]
    print(hash_value)
    hash_result_split_number = []
    for letter in hash_value:
        hash_result_split_number.append(int(letter, 16))
    return hash_result_split_number


def _hex_to_witness(hex_str: str, length: int) -> List[int]:
    int_array = list(map(lambda x: int(x, 16), hex_str))
    while len(int_array) < length:
        int_array.insert(0, 0)
    return int_array


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
        setup_uuid: str,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_prover_dto: BitVMXProtocolProverDTO,
    ) -> Transaction:
        if (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
            > 0
            and bitvmx_protocol_prover_dto.input_hex is None
        ):
            raise Exception("Input should be set before publishing the hash result")

        hash_result_signatures = bitvmx_protocol_prover_dto.hash_result_signatures

        self.execution_trace_generation_service(
            setup_uuid=setup_uuid,
            input_hex=bitvmx_protocol_prover_dto.input_hex,
        )
        last_step_trace = self.execution_trace_query_service(
            setup_uuid=setup_uuid,
            index=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_trace_steps
            - 1,
            input_hex=bitvmx_protocol_prover_dto.input_hex,
        )
        hash_result_split_number = _get_result_hash_value(last_step_trace)

        last_step = self.execution_trace_query_service.get_last_step(setup_uuid=setup_uuid)

        hash_result_witness = self.generate_witness_from_input_nibbles_service(
            step=1,
            case=0,
            input_numbers=hash_result_split_number,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        halt_step_witness = self.generate_witness_from_input_nibbles_service(
            step=1,
            case=1,
            input_numbers=list(
                reversed(
                    _hex_to_witness(
                        hex_str=hex(last_step - 1)[2:],
                        length=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
                    )
                )
            ),
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        if (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
            > 0
        ):
            input_witness = []
            for i in range(
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
            ):
                input_witness += self.generate_witness_from_input_nibbles_service(
                    step=1,
                    case=2 + i,
                    input_numbers=_hex_to_witness(
                        hex_str=bitvmx_protocol_prover_dto.input_hex[i * 8 : (i + 1) * 8],
                        length=8,
                    ),
                    bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
                )
        else:
            input_witness = []

        hash_result_script = self.hash_result_script_generator(
            signature_public_keys=bitvmx_protocol_setup_properties_dto.signature_public_keys,
            hash_result_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys,
            halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys,
            input_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.input_public_keys,
            n0=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            amount_of_nibbles_halt_step=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
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

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx.witnesses.append(
            TxWitnessInput(
                hash_result_signatures
                + hash_result_witness
                + halt_step_witness
                + input_witness
                + [
                    hash_result_script.to_hex(),
                    hash_result_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx.serialize()
        )
        print(
            "Hash result revelation transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx.get_txid()
        )
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx
