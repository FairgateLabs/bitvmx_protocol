from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from scripts.services.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from winternitz_keys_handling.services.generate_witness_from_input_single_word_service import (
    GenerateWitnessFromInputSingleWordService,
)


class PublishChoiceSearchTransactionService:

    def __init__(self, verifier_private_key):
        self.commit_search_choice_script_generator_service = (
            CommitSearchChoiceScriptGeneratorService()
        )
        self.broadcast_transaction_service = BroadcastTransactionService()
        self.generate_verifier_witness_from_input_single_word_service = (
            GenerateWitnessFromInputSingleWordService(verifier_private_key)
        )

    def __call__(self, protocol_dict, i):
        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
        amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]
        choice_hash_tx_list = protocol_dict["choice_hash_tx_list"]

        choice_search_verifier_public_keys_list = protocol_dict[
            "choice_search_verifier_public_keys_list"
        ]

        current_choice_public_keys = choice_search_verifier_public_keys_list[i]
        current_choice_search_script = self.commit_search_choice_script_generator_service(
            current_choice_public_keys[0],
            amount_of_bits_wrong_step_search,
        )

        choice_search_witness = []
        current_choice = 2
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

        choice_hash_tx_list[i].witnesses.append(
            TxWitnessInput(
                choice_search_witness
                + [
                    # third_signature_bob,
                    # third_signature_alice,
                    current_choice_search_script.to_hex(),
                    current_choice_search_control_block.to_hex(),
                ]
            )
        )

        self.broadcast_transaction_service(transaction=choice_hash_tx_list[i].serialize())
        print(
            "Choice hash iteration transaction " + str(i) + ": " + choice_hash_tx_list[i].get_txid()
        )
        return choice_hash_tx_list[i]
