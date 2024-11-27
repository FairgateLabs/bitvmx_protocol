from typing import Dict, Tuple

from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_single_word_service import (
    GenerateWitnessFromInputSingleWordService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
    transaction_info_service,
)


class PublishChoiceSearchTransactionService:

    def __init__(self, verifier_private_key):
        self.generate_verifier_witness_from_input_single_word_service = (
            GenerateWitnessFromInputSingleWordService(verifier_private_key)
        )
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        iteration: int,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        search_choice_signatures = bitvmx_protocol_verifier_dto.search_choice_signatures

        current_choice_search_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
            iteration=iteration
        )[
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_script_index()
        ]

        choice_search_witness = []
        current_choice, new_published_hashes_dict = self._get_choice(
            iteration=iteration,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
        )

        choice_search_witness += self.generate_verifier_witness_from_input_single_word_service(
            step=(3 + iteration * 2 + 1),
            case=0,
            input_number=current_choice,
            amount_of_bits=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
        )
        current_choice_search_scripts_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
            iteration=iteration
        ).get_taproot_address(
            public_key=bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        current_choice_search_scripts_taptree = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
            iteration=iteration
        ).to_scripts_tree()
        current_choice_search_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=current_choice_search_scripts_taptree,
            index=0,
            is_odd=current_choice_search_scripts_address.is_odd(),
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
            iteration
        ].witnesses.append(
            TxWitnessInput(
                search_choice_signatures[iteration]
                + choice_search_witness
                + [
                    current_choice_search_script.to_hex(),
                    current_choice_search_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                iteration
            ].serialize()
        )
        bitvmx_protocol_verifier_dto.search_choices.append(current_choice)
        bitvmx_protocol_verifier_dto.published_hashes_dict = new_published_hashes_dict
        print(
            "Search choice iteration transaction "
            + str(iteration)
            + ": "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                iteration
            ].get_txid()
        )
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
            iteration
        ]

    def _get_choice(
        self,
        iteration,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ) -> Tuple[int, Dict[int, str]]:

        previous_hash_search_txid = (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list[
                iteration
            ].get_txid()
        )
        previous_hash_search_tx = transaction_info_service(previous_hash_search_txid)
        previous_hash_search_witness = previous_hash_search_tx.inputs[0].witness

        published_hashes = []
        if iteration == 0:
            choice_offset = 0
        else:
            choice_offset = 8
        for j in range(
            2
            ** bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            - 1
        ):
            hash_witness_portion = previous_hash_search_witness[
                len(bitvmx_protocol_setup_properties_dto.signature_public_keys)
                + (
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash_with_checksum
                    * j
                    * 2
                )
                + choice_offset : len(bitvmx_protocol_setup_properties_dto.signature_public_keys)
                + 2
                * bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash
                + bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash_with_checksum
                * j
                * 2
                + choice_offset
            ]
            published_hashes.append(
                "".join(
                    [
                        (hex_repr[1] if len(hex_repr) == 2 else "0")
                        for hex_repr in reversed(hash_witness_portion[1::2])
                    ]
                )
            )
        published_hashes.reverse()
        prefix = ""
        for search_choice in bitvmx_protocol_verifier_dto.search_choices:
            prefix += bin(search_choice)[2:].zfill(
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            )
        suffix = (
            "1"
            * bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            * (
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                - iteration
                - 1
            )
        )
        index_list = []
        for j in range(
            2
            ** bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            - 1
        ):
            index_list.append(
                int(
                    prefix
                    + bin(j)[2:].zfill(
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    )
                    + suffix,
                    2,
                )
            )

        previous_published_hashes_dict = bitvmx_protocol_verifier_dto.published_hashes_dict.copy()

        for j in range(len(index_list)):
            previous_published_hashes_dict[index_list[j]] = published_hashes[j]

        index_list.append(
            int(
                prefix
                + bin(
                    2
                    ** bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    - 1
                )[2:].zfill(
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                )
                + suffix,
                2,
            )
        )
        for j in range(len(index_list)):
            index = index_list[j]
            current_hash = self.execution_trace_query_service(
                setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid,
                index=index,
                input_hex=bitvmx_protocol_verifier_dto.input_hex,
            )["step_hash"]
            if not current_hash == previous_published_hashes_dict[index] or index >= int(
                bitvmx_protocol_verifier_dto.published_halt_step, 16
            ):
                return j, previous_published_hashes_dict
        raise Exception("There was some error when choosing the wrong step")
