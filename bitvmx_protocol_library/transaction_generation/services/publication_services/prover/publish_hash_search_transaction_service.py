from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import (
    BitVMXProverWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.commit_search_hashes_script_generator_service import (
    CommitSearchHashesScriptGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_transactions_dto import (
    BitVMXTransactionsDTO,
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


class PublishHashSearchTransactionService:

    def __init__(self, prover_private_key):
        self.commit_search_hashes_script_generator_service = (
            CommitSearchHashesScriptGeneratorService()
        )
        self.commit_search_choice_script_generator_service = (
            CommitSearchChoiceScriptGeneratorService()
        )
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
        iteration: int,
        setup_uuid: str,
        bitvmx_transactions_dto: BitVMXTransactionsDTO,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_prover_winternitz_public_keys_dto: BitVMXProverWinternitzPublicKeysDTO,
        bitvmx_verifier_winternitz_public_keys_dto: BitVMXVerifierWinternitzPublicKeysDTO,
    ):

        signature_public_keys = protocol_dict["public_keys"]
        search_hash_signatures = protocol_dict["search_hash_signatures"]

        bitvmx_prover_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_prover_winternitz_public_keys_dto"
        ]

        hash_search_witness = []
        current_hash_public_keys = (
            bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[iteration]
        )

        if iteration > 0:
            previous_choice_tx = bitvmx_transactions_dto.search_choice_tx_list[
                iteration - 1
            ].get_txid()
            previous_choice_transaction_info = transaction_info_service(previous_choice_tx)
            previous_witness = previous_choice_transaction_info.inputs[0].witness
            previous_choice_verifier_public_keys = (
                bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list[
                    iteration - 1
                ]
            )
            current_choice_prover_public_keys = (
                bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list[
                    iteration - 1
                ]
            )
            current_hash_search_script = self.commit_search_hashes_script_generator_service(
                signature_public_keys,
                current_hash_public_keys,
                bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
                bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
                bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
                current_choice_prover_public_keys[0],
                previous_choice_verifier_public_keys[0],
            )

            hash_search_witness += previous_witness[
                len(signature_public_keys) + 0 : len(signature_public_keys) + 4
            ]
            current_choice = (
                int(previous_witness[len(signature_public_keys) + 1])
                if len(previous_witness[len(signature_public_keys) + 1]) > 0
                else 0
            )
            protocol_dict["search_choices"].append(current_choice)
            hash_search_witness += self.generate_prover_witness_from_input_single_word_service(
                step=(3 + (iteration - 1) * 2 + 1),
                case=0,
                input_number=current_choice,
                amount_of_bits=bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            )

        else:
            current_hash_search_script = self.commit_search_hashes_script_generator_service(
                signature_public_keys,
                current_hash_public_keys,
                bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
                bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

        iteration_hashes = self._get_hashes(
            setup_uuid=setup_uuid,
            iteration=iteration,
            protocol_dict=protocol_dict,
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
        )

        for word_count in range(
            bitvmx_protocol_properties_dto.amount_of_wrong_step_search_hashes_per_iteration
        ):

            input_number = []
            for letter in iteration_hashes[len(iteration_hashes) - word_count - 1]:
                input_number.append(int(letter, 16))

            hash_search_witness += self.generate_witness_from_input_nibbles_service(
                step=(3 + iteration * 2),
                case=bitvmx_protocol_properties_dto.amount_of_wrong_step_search_hashes_per_iteration
                - word_count
                - 1,
                input_numbers=input_number,
                bits_per_digit_checksum=bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

        current_hash_search_scripts_address = (
            bitvmx_protocol_setup_properties_dto.unspendable_public_key.get_taproot_address(
                [[current_hash_search_script]]
            )
        )
        current_hash_search_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=[[current_hash_search_script]],
            index=0,
            is_odd=current_hash_search_scripts_address.is_odd(),
        )

        bitvmx_transactions_dto.search_hash_tx_list[iteration].witnesses.append(
            TxWitnessInput(
                search_hash_signatures[iteration]
                + hash_search_witness
                + [
                    current_hash_search_script.to_hex(),
                    current_hash_search_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_transactions_dto.search_hash_tx_list[iteration].serialize()
        )
        print(
            "Search hash iteration transaction "
            + str(iteration)
            + ": "
            + bitvmx_transactions_dto.search_hash_tx_list[iteration].get_txid()
        )
        return bitvmx_transactions_dto.search_hash_tx_list[iteration]

    def _get_hashes(
        self,
        setup_uuid: str,
        iteration: int,
        protocol_dict,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
    ):
        prefix = ""
        for search_choice in protocol_dict["search_choices"]:
            prefix += bin(search_choice)[2:].zfill(
                bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            )
        suffix = (
            "1"
            * bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
            * (
                bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                - iteration
                - 1
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
        for index in index_list:
            hash_list.append(
                self.execution_trace_query_service(setup_uuid=setup_uuid, index=index)["step_hash"]
            )
        for j in range(len(index_list)):
            protocol_dict["published_hashes_dict"][index_list[j]] = hash_list[j]
        return hash_list
