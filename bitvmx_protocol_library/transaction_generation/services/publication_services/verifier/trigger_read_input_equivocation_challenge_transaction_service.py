from abc import abstractmethod
from typing import List

from bitcoinutils.constants import TAPROOT_SIGHASH_ALL
from bitcoinutils.keys import PrivateKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.input_and_constant_addresses_generation_service import (
    InputAndConstantAddressesGenerationService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_private_dto import (
    BitVMXProtocolVerifierPrivateDTO,
)
from bitvmx_protocol_library.script_generation.entities.dtos.bitvmx_bitcoin_scripts_dto import (
    BitVMXBitcoinScriptsDTO,
)
from bitvmx_protocol_library.script_generation.services.bitvmx_bitcoin_scripts_generator_service import (
    BitVMXBitcoinScriptsGeneratorService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
    transaction_info_service,
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
        input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        amount_of_input_words = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        )
        static_addresses = input_and_constant_addresses_generation_service(
            input_length=amount_of_input_words
        )

        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        current_address = self._get_address(
            bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto
        )

        current_script_index = self._trigger_input_equivocation_challenge_index(
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            address=current_address,
            base_input_address=static_addresses.input.address,
            amount_of_input_words=amount_of_input_words,
        )

        trace_witness = self._get_trace_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )

        trace_address_witness = self._get_address_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            trace_witness=trace_witness,
        )

        publish_hash_value_witness = self._get_publish_hash_value_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            input_index=bitvmx_bitcoin_scripts_dto.get_index_from_address(
                address=current_address, base_input_address=static_addresses.input.address
            ),
        )

        trace_value_witness = self._get_trace_value_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            trace_witness=trace_witness,
        )

        trigger_input_equivocation_witness = (
            trace_value_witness + publish_hash_value_witness + trace_address_witness
        )

        # TODO: we should load this address from protocol dict as we add more challenges
        trigger_challenge_taptree = bitvmx_bitcoin_scripts_dto.trigger_challenge_taptree()
        trigger_challenge_scripts_address = (
            bitvmx_protocol_setup_properties_dto.unspendable_public_key.get_taproot_address(
                trigger_challenge_taptree
            )
        )

        current_script = bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list[
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
    def _trigger_input_equivocation_challenge_index(
        self,
        bitvmx_bitcoin_scripts_dto: BitVMXBitcoinScriptsDTO,
        address: str,
        base_input_address: str,
        amount_of_input_words: int,
    ):
        pass

    def _get_trace_witness(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        trace_tx = transaction_info_service(
            tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.get_txid()
        )
        trace_witness = trace_tx.inputs[0].witness
        while len(trace_witness[0]) == 128:
            trace_witness = trace_witness[1:]
        # Erase the previous step confirmation
        trace_witness = trace_witness[8:]
        return trace_witness

    def _get_publish_hash_witness(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        publish_hash_tx = transaction_info_service(
            tx_id=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx.get_txid()
        )
        publish_hash_tx = publish_hash_tx.inputs[0].witness
        while len(publish_hash_tx[0]) == 128:
            publish_hash_tx = publish_hash_tx[1:]
        return publish_hash_tx

    def _get_address_witness(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        trace_witness: List[str],
    ):
        trace_words_public_keys = (
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys
        )
        address_position = self._get_address_position(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        current_index = 0
        current_init = 0
        while current_index < address_position:
            current_init += len(trace_words_public_keys[-1 - current_index]) * 2
            current_index += 1
        return trace_witness[
            current_init : current_init + (len(trace_words_public_keys[-1 - current_index]) * 2)
        ]

    def _get_trace_value_witness(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        trace_witness: List[str],
    ):
        trace_words_public_keys = (
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys
        )
        value_position = self._get_trace_value_position(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        current_index = 0
        current_init = 0
        while current_index < value_position:
            current_init += len(trace_words_public_keys[-1 - current_index]) * 2
            current_index += 1
        return trace_witness[
            current_init : current_init + (len(trace_words_public_keys[-1 - current_index]) * 2)
        ]

    def _get_publish_hash_value_witness(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        input_index: int,
    ):
        publish_hash_witness = self._get_publish_hash_witness(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        publish_hash_witness = publish_hash_witness[
            len(
                bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys
            )
            * 2 :
        ]
        publish_hash_witness = publish_hash_witness[
            len(
                bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys
            )
            * 2 :
        ]
        input_public_keys = (
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.input_public_keys
        )
        counter = 0
        while counter < input_index:
            publish_hash_witness = publish_hash_witness[len(input_public_keys[counter]) * 2 :]
            counter += 1
        return publish_hash_witness[: len(input_public_keys[input_index]) * 2]

    @abstractmethod
    def _get_address_position(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        pass

    @abstractmethod
    def _get_trace_value_position(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        pass

    @abstractmethod
    def _get_address(self, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO):
        pass


class TriggerReadInput1EquivocationChallengeTransactionService(
    GenericTriggerReadInputEquivocationChallengeTransactionService
):
    def _get_address(self, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO):
        return bitvmx_protocol_verifier_dto.published_execution_trace.read_1_address

    def _trigger_input_equivocation_challenge_index(
        self,
        bitvmx_bitcoin_scripts_dto: BitVMXBitcoinScriptsDTO,
        address: str,
        base_input_address: str,
        amount_of_input_words: int,
    ):
        return bitvmx_bitcoin_scripts_dto.trigger_input_1_equivocation_challenge_index(
            address=address,
            base_input_address=base_input_address,
            amount_of_input_words=amount_of_input_words,
        )

    def _get_address_position(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_1_address_position
        )

    def _get_trace_value_position(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_1_value_position
        )


class TriggerReadInput2EquivocationChallengeTransactionService(
    GenericTriggerReadInputEquivocationChallengeTransactionService
):
    def _get_address(self, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO):
        return bitvmx_protocol_verifier_dto.published_execution_trace.read_2_address

    def _trigger_input_equivocation_challenge_index(
        self,
        bitvmx_bitcoin_scripts_dto: BitVMXBitcoinScriptsDTO,
        address: str,
        base_input_address: str,
        amount_of_input_words: int,
    ):
        return bitvmx_bitcoin_scripts_dto.trigger_input_2_equivocation_challenge_index(
            address=address,
            base_input_address=base_input_address,
            amount_of_input_words=amount_of_input_words,
        )

    def _get_address_position(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_2_address_position
        )

    def _get_trace_value_position(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_2_value_position
        )
