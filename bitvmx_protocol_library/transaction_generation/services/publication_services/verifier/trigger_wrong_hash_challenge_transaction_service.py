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
from bitvmx_protocol_library.script_generation.services.bitvmx_bitcoin_scripts_generator_service import (
    BitVMXBitcoinScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_hash_challenge_script_generator_service import (
    TriggerWrongHashChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
    transaction_info_service,
)


class TriggerWrongHashChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.verifier_wrong_hash_script_generator_service = (
            TriggerWrongHashChallengeScriptGeneratorService()
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            verifier_private_key
        )
        self.bitvmx_bitcoin_scripts_generator_service = BitVMXBitcoinScriptsGeneratorService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):

        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            signature_public_keys=bitvmx_protocol_setup_properties_dto.signature_public_keys,
        )

        trigger_challenge_taptree = bitvmx_bitcoin_scripts_dto.trigger_challenge_taptree()
        trigger_challenge_scripts_address = bitvmx_bitcoin_scripts_dto.trigger_challenge_address(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )

        wrong_hash_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_challenge_taptree,
            index=bitvmx_bitcoin_scripts_dto.trigger_wrong_hash_challenge_index(0),
            is_odd=trigger_challenge_scripts_address.is_odd(),
        )

        trace_witness = self._get_trace_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        write_trace_witness = []
        for i in range(len(trace_witness) - 4, len(trace_witness)):
            write_trace_witness.extend(trace_witness[i])

        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )
        wrong_hash_challenge_signature = private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx,
            0,
            [trigger_challenge_scripts_address.to_script_pub_key()],
            [
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.outputs[
                    0
                ].amount
                + bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=bitvmx_bitcoin_scripts_dto.wrong_hash_challenge_scripts[0],
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        trigger_execution_challenge_signature = [wrong_hash_challenge_signature]
        trigger_challenge_witness = write_trace_witness

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_challenge_witness
                + trigger_execution_challenge_signature
                + [
                    bitvmx_bitcoin_scripts_dto.wrong_hash_challenge_scripts[0].to_hex(),
                    wrong_hash_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.serialize()
        )

        print(
            "Trigger wrong hash challenge transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.get_txid()
        )
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx
        )

    def _get_trace_witness(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> List[str]:
        publish_trace_tx = transaction_info_service(
            tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.get_txid()
        )

        verifier_keys_witness_values = []
        processed_values = 0
        real_values = []
        publish_trace_tx_witness = publish_trace_tx.inputs[0].witness
        while len(publish_trace_tx_witness[0]) == 128:
            publish_trace_tx_witness = publish_trace_tx_witness[1:]
        # At this point, we have erased the signatures
        # In the publication trace, there is the confirmation for the last choice, we also need to erase that
        # The amount of hashes to discard is 4 because we sign a single word. Then we have the hash and the value.
        # Hence, 8 elements
        publish_trace_tx_witness = publish_trace_tx_witness[8:]

        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )

        for i in reversed(range(len(trace_words_lengths))):
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
                        current_trace_witness[1 : 2 * trace_words_lengths[i] : 2],
                    )
                )
            )

        return verifier_keys_witness_values

    def _get_wrong_hash_witness(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        pass

    def _get_correct_hash_witness(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        pass
