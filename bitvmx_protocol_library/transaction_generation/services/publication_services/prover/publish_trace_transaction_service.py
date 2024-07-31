from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import \
    BitVMXProtocolPropertiesDTO
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import \
    BitVMXProverWinternitzPublicKeysDTO
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import \
    BitVMXVerifierWinternitzPublicKeysDTO
from bitvmx_protocol_library.script_generation.services.script_generation.execution_trace_script_generator_service import (
    ExecutionTraceScriptGeneratorService,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_single_word_service import (
    GenerateWitnessFromInputSingleWordService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
    transaction_info_service,
)


class PublishTraceTransactionService:

    def __init__(self, prover_private_key):
        self.execution_trace_script_generator_service = ExecutionTraceScriptGeneratorService()
        self.generate_prover_witness_from_input_single_word_service = (
            GenerateWitnessFromInputSingleWordService(prover_private_key)
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            prover_private_key
        )
        self.execution_trace_query_service = ExecutionTraceQueryService("prover_files/")

    def __call__(
            self,
            protocol_dict,
            bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
            bitvmx_prover_winternitz_public_keys_dto: BitVMXProverWinternitzPublicKeysDTO,
            bitvmx_verifier_winternitz_public_keys_dto: BitVMXVerifierWinternitzPublicKeysDTO,
    ):
        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
        trace_signatures = protocol_dict["trace_signatures"]
        trace_words_lengths = bitvmx_protocol_properties_dto.trace_words_lengths[::-1]

        trace_witness = []

        previous_choice_tx = protocol_dict["search_choice_tx_list"][-1].get_txid()
        previous_choice_transaction_info = transaction_info_service(previous_choice_tx)
        previous_witness = previous_choice_transaction_info.inputs[0].witness
        trace_witness += previous_witness[len(trace_signatures) + 0 : len(trace_signatures) + 4]
        current_choice = (
            int(previous_witness[len(trace_signatures) + 1])
            if len(previous_witness[len(trace_signatures) + 1]) > 0
            else 0
        )

        protocol_dict["search_choices"].append(current_choice)
        first_wrong_step = int(
            "".join(
                map(
                    lambda digit: bin(digit)[2:].zfill(
                        bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    ),
                    protocol_dict["search_choices"],
                )
            ),
            2,
        )
        print("First wrong step: " + str(first_wrong_step))

        current_trace = self.execution_trace_query_service(
            protocol_dict["setup_uuid"], first_wrong_step
        )
        current_trace_values = current_trace[:13].to_list()
        current_trace_values.reverse()
        trace_array = []
        for j in range(len(trace_words_lengths)):
            word_length = trace_words_lengths[j]
            trace_array.append(hex(int(current_trace_values[j]))[2:].zfill(word_length))

        trace_witness += self.generate_prover_witness_from_input_single_word_service(
            step=(
                3
                + (bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations - 1) * 2
                + 1
            ),
            case=0,
            input_number=current_choice,
            amount_of_bits=bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
        )

        for word_count in range(len(trace_words_lengths)):

            input_number = []
            for letter in reversed(trace_array[len(trace_array) - word_count - 1]):
                input_number.append(int(letter, 16))

            trace_witness += self.generate_witness_from_input_nibbles_service(
                step=3 + bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations * 2,
                case=len(trace_words_lengths) - word_count - 1,
                input_numbers=input_number,
                bits_per_digit_checksum=bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

        trace_tx = protocol_dict["trace_tx"]

        trace_script = self.execution_trace_script_generator_service(
            protocol_dict["public_keys"],
            bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            trace_words_lengths,
            bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list[-1][0],
            bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list[-1][0],
        )
        trace_script_address = destroyed_public_key.get_taproot_address([[trace_script]])

        trace_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[trace_script]],
            index=0,
            is_odd=trace_script_address.is_odd(),
        )

        trace_tx.witnesses.append(
            TxWitnessInput(
                trace_signatures
                + trace_witness
                + [
                    trace_script.to_hex(),
                    trace_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(transaction=trace_tx.serialize())
        print("Trace transaction: " + trace_tx.get_txid())
        return trace_tx
