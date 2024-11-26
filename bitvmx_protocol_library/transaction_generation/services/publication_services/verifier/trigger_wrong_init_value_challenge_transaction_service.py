from abc import abstractmethod
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
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.execution_trace_witness_dto import (
    ExecutionTraceWitnessDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_execution_trace_witness_service import (
    GetExecutionTraceWitnessService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class GenericTriggerWrongInitValueChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.get_execution_trace_witness_service = GetExecutionTraceWitnessService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        trigger_wrong_init_value_challenge_taptree = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_challenge_taptree()
        )
        trigger_wrong_init_value_challenge_scripts_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list.get_taproot_address(
            public_key=bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        current_index = self._get_index(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        current_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list[
            current_index
        ]

        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )
        wrong_init_value_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_wrong_init_value_challenge_taptree,
            index=current_index,
            is_odd=trigger_wrong_init_value_challenge_scripts_address.is_odd(),
        )
        wrong_init_value_challenge_signature = private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx,
            0,
            [trigger_wrong_init_value_challenge_scripts_address.to_script_pub_key()],
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

        trigger_wrong_init_value_signatures = [wrong_init_value_challenge_signature]

        execution_trace_witness_dto = self.get_execution_trace_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        trace_last_step = self._get_last_step_witness(
            execution_trace_witness_dto=execution_trace_witness_dto
        )
        trace_address = self._get_trace_address_witness(
            execution_trace_witness_dto=execution_trace_witness_dto
        )
        trace_value = self._get_trace_value_witness(
            execution_trace_witness_dto=execution_trace_witness_dto
        )

        trigger_wrong_init_witness = trace_address + trace_value + trace_last_step
        # trigger_wrong_init_witness = []

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.witnesses.append(
            TxWitnessInput(
                trigger_wrong_init_witness
                + trigger_wrong_init_value_signatures
                + [
                    current_script.to_hex(),
                    wrong_init_value_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.serialize()
        )

        print(
            "Trigger wrong init value challenge transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.get_txid()
        )
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx

    @abstractmethod
    def _get_index(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> int:
        pass

    @abstractmethod
    def _get_last_step_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        pass

    @abstractmethod
    def _get_trace_address_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        pass

    @abstractmethod
    def _get_trace_value_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        pass


class TriggerWrongInitValue1ChallengeTransactionService(
    GenericTriggerWrongInitValueChallengeTransactionService
):

    def _get_index(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> int:
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_wrong_init_value_1_challenge_index()
        )

    def _get_last_step_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_1_last_step

    def _get_trace_address_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_1_address

    def _get_trace_value_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_1_value


class TriggerWrongInitValue2ChallengeTransactionService(
    GenericTriggerWrongInitValueChallengeTransactionService
):
    def _get_index(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> int:
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_wrong_init_value_2_challenge_index()
        )

    def _get_last_step_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_2_last_step

    def _get_trace_address_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_2_address

    def _get_trace_value_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_2_value
