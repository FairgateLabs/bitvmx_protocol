from typing import Dict

from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_prover_dto import (
    BitVMXProtocolProverDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
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


class PublishHashReadSearchTransactionService:

    def __init__(self, prover_private_key):
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

        read_search_hash_signatures = bitvmx_protocol_prover_dto.read_search_hash_signatures
        iteration = len(bitvmx_protocol_prover_dto.read_search_choices)
        hash_read_search_witness = []

        previous_choice_tx = (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_choice_tx_list[
                iteration
            ].get_txid()
        )
        previous_choice_transaction_info = transaction_info_service(previous_choice_tx)
        previous_witness = previous_choice_transaction_info.inputs[0].witness
        current_hash_search_index = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_script_index()
        )
        current_hash_search_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_list(
            iteration=iteration
        )[
            current_hash_search_index
        ]
        current_hash_search_taptree = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_list(
            iteration=iteration
        ).to_scripts_tree()
        current_hash_search_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_list(
            iteration=iteration
        ).get_taproot_address(
            public_key=bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )

        hash_read_search_witness += previous_witness[
            len(bitvmx_protocol_setup_properties_dto.signature_public_keys)
            + 0 : len(bitvmx_protocol_setup_properties_dto.signature_public_keys)
            + 4
        ]
        current_choice = (
            int(
                previous_witness[
                    len(bitvmx_protocol_setup_properties_dto.signature_public_keys) + 1
                ]
            )
            if len(
                previous_witness[
                    len(bitvmx_protocol_setup_properties_dto.signature_public_keys) + 1
                ]
            )
            > 0
            else 0
        )
        bitvmx_protocol_prover_dto.read_search_choices.append(current_choice)
        hash_read_search_witness += self.generate_prover_witness_from_input_single_word_service(
            step=(
                3
                + bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                * 2
                + 2
                + 2 * iteration
                + 1
            ),
            case=0,
            input_number=current_choice,
            amount_of_bits=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
        )

        iteration_hashes_dict = self._get_hashes(
            setup_uuid=setup_uuid,
            iteration=iteration,
            bitvmx_protocol_properties_dto=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto,
            bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto,
        )
        iteration_hashes_keys = sorted(list(iteration_hashes_dict.keys()))
        iteration_hashes = []
        for key in iteration_hashes_keys:
            iteration_hashes.append(iteration_hashes_dict[key])

        for word_count in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_hashes_per_iteration
        ):

            input_number = []
            for letter in iteration_hashes[len(iteration_hashes) - word_count - 1]:
                input_number.append(int(letter, 16))

            hash_read_search_witness += self.generate_witness_from_input_nibbles_service(
                step=(
                    3
                    + bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                    * 2
                    + 2
                    + 2 * iteration
                ),
                case=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_hashes_per_iteration
                - word_count
                - 1,
                input_numbers=input_number,
                bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

        current_hash_search_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=current_hash_search_taptree,
            index=current_hash_search_index,
            is_odd=current_hash_search_address.is_odd(),
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
            iteration
        ].witnesses.append(
            TxWitnessInput(
                read_search_hash_signatures[iteration]
                + hash_read_search_witness
                + [
                    current_hash_search_script.to_hex(),
                    current_hash_search_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
                iteration
            ].serialize()
        )
        bitvmx_protocol_prover_dto.published_hashes_dict.update(iteration_hashes_dict)
        print(
            "Read search hash iteration transaction "
            + str(iteration)
            + ": "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
                iteration
            ].get_txid()
        )
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
                iteration
            ]
        )

    def _get_hashes(
        self,
        setup_uuid: str,
        iteration: int,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_prover_dto: BitVMXProtocolProverDTO,
    ) -> Dict[int, str]:
        prefix = ""
        for search_choice in bitvmx_protocol_prover_dto.read_search_choices:
            prefix += bin(search_choice)[2:].zfill(
                bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            )
        suffix = (
            "1"
            * bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            * (
                bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                - iteration
                - 2
            )
        )
        index_list = []
        for j in range(2**bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search - 1):
            index_list.append(
                int(
                    prefix
                    + bin(j)[2:].zfill(
                        bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    )
                    + suffix,
                    2,
                )
            )
        hash_list = []
        hash_dict = {}
        for index in index_list:
            hash_list.append(
                self.execution_trace_query_service(
                    setup_uuid=setup_uuid,
                    index=index,
                    input_hex=bitvmx_protocol_prover_dto.input_hex,
                )["step_hash"]
            )
            hash_dict[index] = hash_list[-1]
        return hash_dict
