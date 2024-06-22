from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from scripts.services.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from scripts.services.commit_search_hashes_script_generator_service import (
    CommitSearchHashesScriptGeneratorService,
)
from winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from winternitz_keys_handling.services.generate_witness_from_input_single_word_service import (
    GenerateWitnessFromInputSingleWordService,
)


class PublishHashSearchTransactionService:

    def __init__(self, prover_private_key, verifier_private_key):
        self.commit_search_hashes_script_generator_service = (
            CommitSearchHashesScriptGeneratorService()
        )
        self.commit_search_choice_script_generator_service = (
            CommitSearchChoiceScriptGeneratorService()
        )
        self.broadcast_transaction_service = BroadcastTransactionService()
        ## TO BE ERASED ##
        self.generate_verifier_witness_from_input_single_word_service = (
            GenerateWitnessFromInputSingleWordService(verifier_private_key)
        )
        ## END TO BE ERASED ##
        self.generate_prover_witness_from_input_single_word_service = (
            GenerateWitnessFromInputSingleWordService(prover_private_key)
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            prover_private_key
        )

    def __call__(self, protocol_dict, i):
        search_hash_tx_list = protocol_dict["search_hash_tx_list"]
        amount_of_bits_per_digit_checksum = protocol_dict["amount_of_bits_per_digit_checksum"]
        amount_of_nibbles_hash = protocol_dict["amount_of_nibbles_hash"]
        amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]
        amount_of_wrong_step_search_hashes_per_iteration = protocol_dict[
            "amount_of_wrong_step_search_hashes_per_iteration"
        ]
        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])

        hash_search_public_keys_list = protocol_dict["hash_search_public_keys_list"]
        choice_search_prover_public_keys_list = protocol_dict[
            "choice_search_prover_public_keys_list"
        ]
        choice_search_verifier_public_keys_list = protocol_dict[
            "choice_search_verifier_public_keys_list"
        ]

        iteration_hashes = 3 * ["1111111111111111111111111111111111111111111111111111111111111112"]
        hash_search_witness = []

        current_hash_public_keys = hash_search_public_keys_list[i]

        if i > 0:
            previous_choice_verifier_public_keys = choice_search_verifier_public_keys_list[i - 1]
            current_choice_prover_public_keys = choice_search_prover_public_keys_list[i - 1]
            current_hash_search_script = self.commit_search_hashes_script_generator_service(
                current_hash_public_keys,
                amount_of_nibbles_hash,
                amount_of_bits_per_digit_checksum,
                amount_of_bits_wrong_step_search,
                current_choice_prover_public_keys[0],
                previous_choice_verifier_public_keys[0],
            )

            current_choice = 2
            hash_search_witness += self.generate_verifier_witness_from_input_single_word_service(
                step=(3 + (i - 1) * 2 + 1),
                case=0,
                input_number=current_choice,
                amount_of_bits=amount_of_bits_wrong_step_search,
            )
            hash_search_witness += self.generate_prover_witness_from_input_single_word_service(
                step=(3 + (i - 1) * 2 + 1),
                case=0,
                input_number=current_choice,
                amount_of_bits=amount_of_bits_wrong_step_search,
            )

        else:
            current_hash_search_script = self.commit_search_hashes_script_generator_service(
                current_hash_public_keys,
                amount_of_nibbles_hash,
                amount_of_bits_per_digit_checksum,
            )

        for word_count in range(amount_of_wrong_step_search_hashes_per_iteration):

            input_number = []
            for letter in iteration_hashes[len(iteration_hashes) - word_count - 1]:
                input_number.append(int(letter, 16))

            hash_search_witness += self.generate_witness_from_input_nibbles_service(
                step=(3 + i * 2),
                case=2 - word_count,
                input_numbers=input_number,
                bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            )

        current_hash_search_scripts_address = destroyed_public_key.get_taproot_address(
            [[current_hash_search_script]]
        )
        current_hash_search_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[current_hash_search_script]],
            index=0,
            is_odd=current_hash_search_scripts_address.is_odd(),
        )

        search_hash_tx_list[i].witnesses.append(
            TxWitnessInput(
                hash_search_witness
                + [
                    # third_signature_bob,
                    # third_signature_alice,
                    current_hash_search_script.to_hex(),
                    current_hash_search_control_block.to_hex(),
                ]
            )
        )

        self.broadcast_transaction_service(transaction=search_hash_tx_list[i].serialize())
        print(
            "Search hash iteration transaction " + str(i) + ": " + search_hash_tx_list[i].get_txid()
        )
        return search_hash_tx_list[i]