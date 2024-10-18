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
from bitvmx_protocol_library.script_generation.services.bitvmx_bitcoin_scripts_generator_service import (
    BitVMXBitcoinScriptsGeneratorService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class GenericTriggerReadInputEquivocationChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.bitvmx_bitcoin_scripts_generator_service = BitVMXBitcoinScriptsGeneratorService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):

        trigger_input_equivocation_witness = []

        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        # TODO: we should load this address from protocol dict as we add more challenges
        trigger_challenge_taptree = bitvmx_bitcoin_scripts_dto.trigger_challenge_taptree()
        trigger_challenge_scripts_address = (
            bitvmx_protocol_setup_properties_dto.unspendable_public_key.get_taproot_address(
                trigger_challenge_taptree
            )
        )

        if self.read_parameter() == 1:
            current_script_index = (
                bitvmx_bitcoin_scripts_dto.trigger_input_1_equivocation_challenge_index(
                    address=bitvmx_protocol_verifier_dto.published_execution_trace.read_1_address
                )
            )
        elif self.read_parameter() == 2:
            current_script_index = (
                bitvmx_bitcoin_scripts_dto.trigger_input_2_equivocation_challenge_index(
                    address=bitvmx_protocol_verifier_dto.published_execution_trace.read_2_address
                )
            )
        else:
            raise Exception("Case not recognized in input equivocation challenge")

        current_script = bitvmx_bitcoin_scripts_dto.trigger_challenge_scripts_list[
            current_script_index
        ]

        trigger_input_equivocation_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_challenge_taptree,
            index=current_script_index,
            is_odd=trigger_challenge_scripts_address.is_odd(),
        )

        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )

        trigger_input_equivocation_signature = private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx,
            0,
            [trigger_challenge_scripts_address.to_script_pub_key()],
            [
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.outputs[
                    0
                ].amount
                + bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=current_script,
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        trigger_input_equivocation_signatures = [trigger_input_equivocation_signature]

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.witnesses.append(
            TxWitnessInput(
                trigger_input_equivocation_witness
                + trigger_input_equivocation_signatures
                + [
                    current_script.to_hex(),
                    trigger_input_equivocation_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.serialize()
        )
        print(
            "Trigger input equivocation transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.get_txid()
        )
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx

    @abstractmethod
    def read_parameter(self):
        pass


class TriggerReadInput1EquivocationChallengeTransactionService(
    GenericTriggerReadInputEquivocationChallengeTransactionService
):
    def read_parameter(self):
        return 1


class TriggerReadInput2EquivocationChallengeTransactionService(
    GenericTriggerReadInputEquivocationChallengeTransactionService
):
    def read_parameter(self):
        return 2
