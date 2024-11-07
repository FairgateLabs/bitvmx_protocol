from abc import abstractmethod

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
)


class GenericTriggerWrongValueAddressReadChallengeTransactionService:
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
        current_index = self._get_index(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        current_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_challenge_scripts_list[
            current_index
        ]
        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )
        wrong_value_address_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_read_challenge_taptree,
            index=current_index,
            is_odd=trigger_read_challenge_scripts_address.is_odd(),
        )
        wrong_value_address_challenge_signature = private_key.sign_taproot_input(
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
        trigger_read_challenge_signature = [wrong_value_address_challenge_signature]

        trigger_read_challenge_witness = []

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_read_challenge_witness
                + trigger_read_challenge_signature
                + [
                    current_script.to_hex(),
                    wrong_value_address_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.serialize()
        )
        print(
            "Trigger wrong read value address challenge transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.get_txid()
        )
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx
        )

    @abstractmethod
    def _get_index(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> int:
        pass


class TriggerWrongValueAddressRead1ChallengeTransactionService(
    GenericTriggerWrongValueAddressReadChallengeTransactionService
):
    def _get_index(self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_wrong_value_address_read_1_index()
        )


class TriggerWrongValueAddressRead2ChallengeTransactionService(
    GenericTriggerWrongValueAddressReadChallengeTransactionService
):
    def _get_index(self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_wrong_value_address_read_2_index()
        )
