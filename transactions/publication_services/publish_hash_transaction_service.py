from typing import List

from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import Transaction, TxWitnessInput
from bitcoinutils.utils import ControlBlock

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from scripts.services.hash_result_script_generator_service import HashResultScriptGeneratorService
from winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)


def _get_result_hash_value() -> List[int]:
    hash_value = "1111111111111111111111111111111111111111111111111111111111111112"
    hash_result_split_number = []
    for letter in hash_value:
        hash_result_split_number.append(int(letter, 16))
    return hash_result_split_number


class PublishHashTransactionService:

    def __init__(self, prover_private_key):
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            prover_private_key
        )
        self.hash_result_script_generator = HashResultScriptGeneratorService()
        self.broadcast_transaction_service = BroadcastTransactionService()

    def __call__(self, protocol_dict) -> Transaction:

        hash_result_split_number = _get_result_hash_value()
        amount_of_bits_per_digit_checksum = protocol_dict["amount_of_bits_per_digit_checksum"]
        amount_of_nibbles_hash = protocol_dict["amount_of_nibbles_hash"]
        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])
        hash_result_tx = protocol_dict["hash_result_tx"]
        hash_result_signatures = protocol_dict["hash_result_signatures"]

        hash_result_witness = []
        hash_result_witness += self.generate_witness_from_input_nibbles_service(
            step=1,
            case=0,
            input_numbers=hash_result_split_number,
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

        hash_result_public_keys = protocol_dict["hash_result_public_keys"]

        hash_result_script = self.hash_result_script_generator(
            protocol_dict["public_keys"],
            hash_result_public_keys,
            amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum,
        )
        hash_result_script_address = destroyed_public_key.get_taproot_address(
            [[hash_result_script]]
        )

        hash_result_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[hash_result_script]],
            index=0,
            is_odd=hash_result_script_address.is_odd(),
        )

        hash_result_tx.witnesses.append(
            TxWitnessInput(
                hash_result_witness
                + hash_result_signatures
                + [
                    hash_result_script.to_hex(),
                    hash_result_control_block.to_hex(),
                ]
            )
        )

        self.broadcast_transaction_service(transaction=hash_result_tx.serialize())
        print("Hash result revelation transaction: " + hash_result_tx.get_txid())
        return hash_result_tx
