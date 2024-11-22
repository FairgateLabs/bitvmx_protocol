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
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_full_prover_choice_witness_service import (
    GetFullProverChoiceWitnessService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_full_prover_read_choice_witness_service import (
    GetFullProverReadChoiceWitnessService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_hashes_witness_service import (
    GetHashesWitnessService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_read_hashes_witness_service import (
    GetReadHashesWitnessService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class TriggerReadSearchEquivocationTransactionService:
    def __init__(self):
        self.get_full_read_choice_witness_service = GetFullProverReadChoiceWitnessService()
        self.get_full_choice_witness_service = GetFullProverChoiceWitnessService()
        self.get_hashes_witness_service = GetHashesWitnessService()
        self.get_read_hahes_witness_service = GetReadHashesWitnessService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        iteration = len(bitvmx_protocol_verifier_dto.read_search_choices)
        trigger_challenge_taptree = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_script_list(
            iteration=iteration
        ).to_scripts_tree()
        trigger_challenge_scripts_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_script_list(
            iteration=iteration
        ).get_taproot_address(
            public_key=bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        trigger_challenge_index = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_search_equivocation_index(
            iteration=iteration
        )
        trigger_challenge_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_script_list(
            iteration=iteration
        )[
            trigger_challenge_index
        ]

        trigger_challenge_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_challenge_taptree,
            index=trigger_challenge_index,
            is_odd=trigger_challenge_scripts_address.is_odd(),
        )
        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )
        trigger_challenge_tx = bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_equivocation_tx_list[
            iteration - 1
        ]

        trigger_challenge_signature = private_key.sign_taproot_input(
            trigger_challenge_tx,
            0,
            [trigger_challenge_scripts_address.to_script_pub_key()],
            [
                trigger_challenge_tx.outputs[0].amount
                + bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=trigger_challenge_script,
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        trigger_challenge_signatures = [trigger_challenge_signature]

        choices_witness = self.get_choices(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )
        read_choices_witness = self.get_read_choices(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )
        hashes_witness = self.get_hashes(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )
        read_hash_witness = self.get_read_hashes(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )

        trigger_challenge_witness = (
            read_choices_witness + choices_witness + read_hash_witness + hashes_witness
        )

        trigger_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_challenge_witness
                + trigger_challenge_signatures
                + [
                    trigger_challenge_script.to_hex(),
                    trigger_challenge_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(transaction=trigger_challenge_tx.serialize())

        print(
            "Trigger read search equivocation challenge transaction: "
            + trigger_challenge_tx.get_txid()
        )
        return trigger_challenge_tx

    def get_choices(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO, iteration: int
    ):
        choices = self.get_full_choice_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )
        return choices

    def get_read_choices(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO, iteration: int
    ):
        choices = self.get_full_read_choice_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )
        witness_length = 2 * len(
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list[
                0
            ][
                0
            ]
        )
        choices_witness = []
        assert iteration * witness_length == len(choices)
        for i in range(iteration):
            choices_witness = (
                choices[i * witness_length : (i + 1) * witness_length] + choices_witness
            )
        return choices_witness

    def get_hashes(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO, iteration: int
    ):
        return self.get_hashes_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )

    def get_read_hashes(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO, iteration: int
    ):
        read_hashes = self.get_read_hahes_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            iteration=iteration,
        )
        amount_of_hashes = len(
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_read_search_public_keys_list[
                0
            ]
        )
        assert int(amount_of_hashes * (len(read_hashes) / amount_of_hashes)) == len(read_hashes)
        hash_length = int(len(read_hashes) / amount_of_hashes)
        read_hashes_witness = []
        for i in range(amount_of_hashes):
            read_hashes_witness = (
                read_hashes[i * hash_length : (i + 1) * hash_length] + read_hashes_witness
            )
        return read_hashes_witness
