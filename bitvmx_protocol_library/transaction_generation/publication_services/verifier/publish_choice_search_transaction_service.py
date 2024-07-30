from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
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
        self.commit_search_choice_script_generator_service = (
            CommitSearchChoiceScriptGeneratorService()
        )
        self.generate_verifier_witness_from_input_single_word_service = (
            GenerateWitnessFromInputSingleWordService(verifier_private_key)
        )
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(self, protocol_dict, i):
        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
        amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]
        search_choice_tx_list = protocol_dict["search_choice_tx_list"]

        choice_search_verifier_public_keys_list = protocol_dict[
            "choice_search_verifier_public_keys_list"
        ]
        signature_public_keys = protocol_dict["public_keys"]
        search_choice_signatures = protocol_dict["search_choice_signatures"]

        current_choice_public_keys = choice_search_verifier_public_keys_list[i]
        current_choice_search_script = self.commit_search_choice_script_generator_service(
            signature_public_keys,
            current_choice_public_keys[0],
            amount_of_bits_wrong_step_search,
        )

        choice_search_witness = []
        current_choice = self._get_choice(i, protocol_dict)
        protocol_dict["search_choices"].append(current_choice)
        choice_search_witness += self.generate_verifier_witness_from_input_single_word_service(
            step=(3 + i * 2 + 1),
            case=0,
            input_number=current_choice,
            amount_of_bits=amount_of_bits_wrong_step_search,
        )
        current_choice_search_scripts_address = destroyed_public_key.get_taproot_address(
            [[current_choice_search_script]]
        )
        current_choice_search_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[current_choice_search_script]],
            index=0,
            is_odd=current_choice_search_scripts_address.is_odd(),
        )

        search_choice_tx_list[i].witnesses.append(
            TxWitnessInput(
                search_choice_signatures[i]
                + choice_search_witness
                + [
                    current_choice_search_script.to_hex(),
                    current_choice_search_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(transaction=search_choice_tx_list[i].serialize())
        print(
            "Search choice iteration transaction "
            + str(i)
            + ": "
            + search_choice_tx_list[i].get_txid()
        )
        return search_choice_tx_list[i]

    def _get_choice(self, i, protocol_dict):
        bitvmx_protocol_properties_dto = protocol_dict["bitvmx_protocol_properties_dto"]

        previous_hash_search_txid = protocol_dict["search_hash_tx_list"][i].get_txid()
        previous_hash_search_tx = transaction_info_service(previous_hash_search_txid)
        previous_hash_search_witness = previous_hash_search_tx.inputs[0].witness
        public_keys = protocol_dict["public_keys"]
        amount_of_nibbles_hash = protocol_dict["amount_of_nibbles_hash"]

        published_hashes = []
        if i == 0:
            choice_offset = 0
        else:
            choice_offset = 8
        for j in range(2**bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search - 1):
            hash_witness_portion = previous_hash_search_witness[
                len(public_keys)
                + (bitvmx_protocol_properties_dto.amount_of_nibbles_hash_with_checksum * j * 2)
                + choice_offset : len(public_keys)
                + 2 * amount_of_nibbles_hash
                + bitvmx_protocol_properties_dto.amount_of_nibbles_hash_with_checksum * j * 2
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
        for search_choice in protocol_dict["search_choices"]:
            prefix += bin(search_choice)[2:].zfill(
                bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            )
        suffix = (
            "1"
            * bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            * (bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations - i - 1)
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

        for j in range(len(index_list)):
            protocol_dict["search_hashes"][index_list[j]] = published_hashes[j]

        index_list.append(
            int(
                prefix
                + bin(2**bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search - 1)[
                    2:
                ].zfill(bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search)
                + suffix,
                2,
            )
        )
        for j in range(len(index_list)):
            index = index_list[j]
            current_hash = self.execution_trace_query_service(protocol_dict["setup_uuid"], index)[
                "step_hash"
            ]
            if not current_hash == protocol_dict["search_hashes"][index]:
                return j
        raise Exception("There was some error when choosing the wrong step")
