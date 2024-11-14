from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_prover_dto import (
    BitVMXProtocolProverDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.execution_trace_script_generator_service import (
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
        setup_uuid: str,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_prover_dto: BitVMXProtocolProverDTO,
    ):

        trace_signatures = bitvmx_protocol_prover_dto.trace_signatures
        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )

        trace_witness = []

        previous_choice_tx = (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                -1
            ].get_txid()
        )
        previous_choice_transaction_info = transaction_info_service(tx_id=previous_choice_tx)
        previous_witness = previous_choice_transaction_info.inputs[0].witness
        trace_witness += previous_witness[len(trace_signatures) + 0 : len(trace_signatures) + 4]
        current_choice = (
            int(previous_witness[len(trace_signatures) + 1])
            if len(previous_witness[len(trace_signatures) + 1]) > 0
            else 0
        )

        bitvmx_protocol_prover_dto.search_choices.append(current_choice)
        first_wrong_step = int(
            "".join(
                map(
                    lambda digit: bin(digit)[2:].zfill(
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    ),
                    bitvmx_protocol_prover_dto.search_choices,
                )
            ),
            2,
        )
        print("First wrong step: " + str(first_wrong_step))

        current_trace = self.execution_trace_query_service(
            setup_uuid=setup_uuid,
            index=first_wrong_step,
            input_hex=bitvmx_protocol_prover_dto.input_hex,
        )
        # CHECK CONSTANT EQUIVOCATION COMBINED WITH FAIL HASH
        # current_trace["read2_address"] = str(int("90000000", 16))
        # current_trace["read2_value"] = str(int("deaddead", 16))
        current_trace_values = current_trace[:13].to_list()
        current_trace_values.reverse()
        trace_array = []
        for j in range(len(trace_words_lengths)):
            word_length = trace_words_lengths[j]
            trace_array.append(hex(int(current_trace_values[j]))[2:].zfill(word_length))

        trace_witness += self.generate_prover_witness_from_input_single_word_service(
            step=(
                3
                + (
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                    - 1
                )
                * 2
                + 1
            ),
            case=0,
            input_number=current_choice,
            amount_of_bits=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
        )

        for word_count in range(len(trace_words_lengths)):

            input_number = []
            for letter in reversed(trace_array[len(trace_array) - word_count - 1]):
                input_number.append(int(letter, 16))

            trace_witness += self.generate_witness_from_input_nibbles_service(
                step=3
                + bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                * 2,
                case=len(trace_words_lengths) - word_count - 1,
                input_numbers=input_number,
                bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

        trace_script = self.execution_trace_script_generator_service(
            bitvmx_protocol_setup_properties_dto.signature_public_keys,
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            trace_words_lengths,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list[
                -1
            ][
                0
            ],
            bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list[
                -1
            ][
                0
            ],
        )
        trace_script_address = (
            bitvmx_protocol_setup_properties_dto.unspendable_public_key.get_taproot_address(
                [[trace_script]]
            )
        )

        trace_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=[[trace_script]],
            index=0,
            is_odd=trace_script_address.is_odd(),
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.witnesses.append(
            TxWitnessInput(
                trace_signatures
                + trace_witness
                + [
                    trace_script.to_hex(),
                    trace_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.serialize()
        )
        print(
            "Trace transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.get_txid()
        )
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx
