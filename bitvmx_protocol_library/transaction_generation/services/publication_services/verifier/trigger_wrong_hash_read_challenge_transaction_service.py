from typing import List

from bitcoinutils.constants import TAPROOT_SIGHASH_ALL
from bitcoinutils.keys import PrivateKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_private_dto import (
    BitVMXProtocolVerifierPrivateDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
    transaction_info_service,
)


class TriggerWrongHashReadChallengeTransactionService:
    def __init__(self, verifier_private_key):
        pass

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        trigger_read_challenge_taptree = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_challenge_taptree()
        )
        trigger_read_challenge_scripts_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_challenge_address(
            destroyed_public_key=bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        current_choice = int(
            "".join(
                map(
                    lambda x: bin(x)[2:].zfill(
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    ),
                    bitvmx_protocol_verifier_dto.read_search_choices,
                )
            ),
            2,
        )
        wrong_hash_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_read_challenge_taptree,
            index=bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_wrong_hash_challenge_index(
                choice=current_choice
            ),
            is_odd=trigger_read_challenge_scripts_address.is_odd(),
        )
        trace_witness = self._get_trace_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        write_trace_witness = []
        # We only take the write part of the trace -> In this case we already had only the write part
        for i in range(len(trace_witness) - 4, len(trace_witness)):
            write_trace_witness.extend(trace_witness[i])
        wrong_hash_witness = self._get_wrong_hash_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
        )
        if bitvmx_protocol_verifier_dto.first_wrong_step > 0:
            correct_hash_witness = self._get_correct_hash_witness(
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
            )
        else:
            correct_hash_witness = []

        choices_witness = self._get_choice_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
        )
        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )

        current_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_challenge_scripts_list[
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_wrong_hash_challenge_index(
                choice=current_choice
            )
        ]
        wrong_hash_read_challenge_signature = private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx,
            0,
            [trigger_read_challenge_scripts_address.to_script_pub_key()],
            [
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.outputs[
                    0
                ].amount
                + bitvmx_protocol_setup_properties_dto.step_fees_satoshis * 4
            ],
            script_path=True,
            tapleaf_script=current_script,
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )
        trigger_read_challenge_signature = [wrong_hash_read_challenge_signature]
        trigger_read_challenge_witness = (
            correct_hash_witness + write_trace_witness + wrong_hash_witness + choices_witness
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_read_challenge_witness
                + trigger_read_challenge_signature
                + [
                    current_script.to_hex(),
                    wrong_hash_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.serialize()
        )

        print(
            "Trigger wrong read hash challenge transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.get_txid()
        )
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx
        )

    def _get_choice_witness(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ) -> List[str]:
        choice_witness = []
        amount_of_bits_wrong_step_search = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
        )
        bin_wrong_choice = "".join(
            list(
                map(
                    lambda x: bin(x)[2:].zfill(
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    ),
                    bitvmx_protocol_verifier_dto.read_search_choices,
                )
            )
        )
        wrong_hash_choice_array = [
            bin_wrong_choice[i : i + amount_of_bits_wrong_step_search].zfill(
                amount_of_bits_wrong_step_search
            )
            for i in range(0, len(bin_wrong_choice), amount_of_bits_wrong_step_search)
        ]
        counter = -1
        if wrong_hash_choice_array[-1] == "0" * amount_of_bits_wrong_step_search:
            suffix_character = "0"
        else:
            suffix_character = "1"
        while -counter <= len(wrong_hash_choice_array):
            if counter == -1:
                # Trace case
                trace_tx = transaction_info_service(
                    tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_trace_tx.get_txid()
                )
                previous_witness = trace_tx.inputs[0].witness
                while len(previous_witness[0]) == 128:
                    previous_witness = previous_witness[1:]
                choice_witness = previous_witness[4:8] + choice_witness
            else:
                # Hash case
                hash_tx = transaction_info_service(
                    tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
                        counter + 1
                    ].get_txid()
                )
                previous_witness = hash_tx.inputs[0].witness
                while len(previous_witness[0]) == 128:
                    previous_witness = previous_witness[1:]
                choice_witness = previous_witness[4:8] + choice_witness
                # choice_witness.extend(previous_witness[4:8])
            if wrong_hash_choice_array[counter] != (
                suffix_character * amount_of_bits_wrong_step_search
            ):
                break
            counter -= 1
        return choice_witness

    def _get_trace_witness(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> List[str]:
        publish_read_trace_tx = transaction_info_service(
            tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_trace_tx.get_txid()
        )

        verifier_keys_witness_values = []
        processed_values = 0
        real_values = []
        publish_trace_tx_witness = publish_read_trace_tx.inputs[0].witness
        while len(publish_trace_tx_witness[0]) == 128:
            publish_trace_tx_witness = publish_trace_tx_witness[1:]
        # At this point, we have erased the signatures
        # In the publication trace, there is the confirmation for the last choice, we also need to erase that
        # The amount of hashes to discard is 4 because we sign a single word. Then we have the hash and the value.
        # Hence, 8 elements. We'll never use more than a nibble to encode the choices.
        publish_trace_tx_witness = publish_trace_tx_witness[8:]

        write_trace_words_lengths = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.write_trace_words_lengths[
            ::-1
        ]

        for i in reversed(range(len(write_trace_words_lengths))):
            current_keys_length = len(
                bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
                    i
                ]
            )
            current_trace_witness = publish_trace_tx_witness[
                processed_values : processed_values + 2 * current_keys_length
            ]
            verifier_keys_witness_values.append(current_trace_witness)
            processed_values += 2 * current_keys_length
            real_values.append(
                "".join(
                    map(
                        lambda elem: "0" if len(elem) == 0 else elem[1],
                        current_trace_witness[1 : 2 * write_trace_words_lengths[i] : 2],
                    )
                )
            )

        return verifier_keys_witness_values

    def _get_hash_witness(
        self,
        binary_choice_array: List[str],
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> List[str]:
        amount_of_bits_wrong_step_search = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
        )
        hash_step_iteration = len(binary_choice_array) - 1
        while (hash_step_iteration >= 0) and (
            binary_choice_array[hash_step_iteration] == "1" * amount_of_bits_wrong_step_search
        ):
            hash_step_iteration -= 1
        if hash_step_iteration < 0:
            raise Exception("This should never be possible in a read search")
            # witness_hash_tx_definition = (
            #     bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx
            # )
            # witness_hash_tx = transaction_info_service(tx_id=witness_hash_tx_definition.get_txid())
            # hash_witness = witness_hash_tx.inputs[0].witness
            # while len(hash_witness[0]) == 128:
            #     hash_witness = hash_witness[1:]
            # # Erase script and control block
            # current_hash_witness = hash_witness[:-2]
        else:
            if hash_step_iteration == 0:
                witness_hash_tx_definition = bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list[
                    0
                ]
            else:
                witness_hash_tx_definition = bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
                    hash_step_iteration - 1
                ]
            witness_hash_tx = transaction_info_service(tx_id=witness_hash_tx_definition.get_txid())
            hash_index = int(binary_choice_array[hash_step_iteration], 2)
            hash_witness = witness_hash_tx.inputs[0].witness
            while len(hash_witness[0]) == 128:
                hash_witness = hash_witness[1:]
            # At this point, we have erased the signatures
            # In the publication trace, there is the confirmation for the last choice, we also need to erase that
            # The amount of hashes to discard is 4 because we sign a single word. Then we have the hash and the value.
            # Hence, 8 elements. We'll never use more than a nibble to encode the choices.
            if hash_step_iteration > 0:
                hash_witness = hash_witness[8:]
            hash_length = (
                len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[
                        hash_step_iteration
                    ][
                        0
                    ]
                )
                * 2
            )
            hash_index_in_witness = (
                len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[
                        hash_step_iteration
                    ]
                )
                - hash_index
                - 1
            )
            current_hash_witness = hash_witness[
                hash_length * hash_index_in_witness : hash_length * (hash_index_in_witness + 1)
            ]
            assert len(current_hash_witness) == hash_length
        return current_hash_witness

    def _get_wrong_hash_witness(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ) -> List[str]:
        binary_choice_array = list(
            map(
                lambda x: bin(x)[2:].zfill(
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                ),
                bitvmx_protocol_verifier_dto.read_search_choices,
            )
        )
        return self._get_hash_witness(
            binary_choice_array=binary_choice_array,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

    def _get_correct_hash_witness(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ) -> List[str]:
        binary_choice_array = list(
            map(
                lambda x: bin(x)[2:].zfill(
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                ),
                bitvmx_protocol_verifier_dto.read_search_choices,
            )
        )
        correct_step_hash = int("".join(binary_choice_array), 2) - 1
        binary_correct_step_hash = bin(correct_step_hash)[2:].zfill(
            len("".join(binary_choice_array))
        )
        search_digit_length = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
        )
        return self._get_hash_witness(
            binary_choice_array=[
                binary_correct_step_hash[i : i + search_digit_length]
                for i in range(0, len(binary_correct_step_hash), search_digit_length)
            ],
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )
