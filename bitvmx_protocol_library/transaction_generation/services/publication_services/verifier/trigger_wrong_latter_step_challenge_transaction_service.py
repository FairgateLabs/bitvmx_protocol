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
    GetReadExecutionTraceWitnessService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_full_prover_read_choice_witness_service import (
    GetFullProverReadChoiceWitnessService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class GenericTriggerWrongLatterStepChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.get_full_read_choice_witness_service = GetFullProverReadChoiceWitnessService()
        self.get_execution_trace_witness_service = GetExecutionTraceWitnessService()
        self.get_read_execution_trace_witness_service = GetReadExecutionTraceWitnessService()

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

        read_choices_witness = self.get_full_read_choice_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )
        wrong_latter_step_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_read_challenge_taptree,
            index=current_index,
            is_odd=trigger_read_challenge_scripts_address.is_odd(),
        )
        wrong_latter_step_challenge_signature = private_key.sign_taproot_input(
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
        trigger_read_challenge_signature = [wrong_latter_step_challenge_signature]

        execution_trace_witness_dto = self.get_execution_trace_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        read_execution_trace_witness_dto = self.get_read_execution_trace_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )

        trace_last_step = self._get_last_step_witness(
            execution_trace_witness_dto=execution_trace_witness_dto
        )
        trace_address = self._get_trace_address_witness(
            execution_trace_witness_dto=execution_trace_witness_dto
        )

        read_trace_address = read_execution_trace_witness_dto.write_address

        trigger_read_challenge_witness = (
            read_trace_address + trace_address + trace_last_step + read_choices_witness
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_read_challenge_witness
                + trigger_read_challenge_signature
                + [
                    current_script.to_hex(),
                    wrong_latter_step_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_read_challenge_tx.serialize()
        )
        print(
            "Trigger wrong latter step challenge transaction: "
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


class TriggerWrongLatterStep1ChallengeTransactionService(
    GenericTriggerWrongLatterStepChallengeTransactionService
):
    def _get_index(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> int:
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_wrong_latter_step_1_index()
        )

    def _get_last_step_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_1_last_step

    def _get_trace_address_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_1_address


class TriggerWrongLatterStep2ChallengeTransactionService(
    GenericTriggerWrongLatterStepChallengeTransactionService
):
    def _get_index(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ) -> int:
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_wrong_latter_step_2_index()
        )

    def _get_last_step_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_2_last_step

    def _get_trace_address_witness(
        self, execution_trace_witness_dto: ExecutionTraceWitnessDTO
    ) -> List[str]:
        return execution_trace_witness_dto.read_2_address
