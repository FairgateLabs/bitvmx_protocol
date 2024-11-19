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
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_execution_trace_witness_service import (
    GetExecutionTraceWitnessService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_full_prover_choice_witness_service import (
    GetFullProverChoiceWitnessService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.services.witness_extraction.get_hash_publication_witness_service import (
    GetHashPublicationWitnessService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class TriggerWrongHaltStepChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.get_choice_witness_service = GetFullProverChoiceWitnessService()
        self.get_execution_trace_witness_service = GetExecutionTraceWitnessService()
        self.get_hash_publication_witness_service = GetHashPublicationWitnessService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        trigger_challenge_taptree = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_challenge_taptree()
        )
        trigger_challenge_scripts_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list.get_taproot_address(
            public_key=bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )

        current_script_index = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_wrong_halt_step_challenge_index()
        )

        current_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list[
            current_script_index
        ]

        trigger_wrong_halt_step_control_block = ControlBlock(
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

        choices_witness = self.get_choice_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        execution_trace_witness = self.get_execution_trace_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )

        hash_publication_witness = self.get_hash_publication_witness_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )

        trigger_wrong_halt_step_witness = (
            execution_trace_witness.opcode
            + execution_trace_witness.read_2_value
            + execution_trace_witness.read_1_value
            + hash_publication_witness.halt_step
            + choices_witness
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.witnesses.append(
            TxWitnessInput(
                trigger_wrong_halt_step_witness
                + trigger_input_equivocation_signatures
                + [
                    current_script.to_hex(),
                    trigger_wrong_halt_step_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.serialize()
        )

        print(
            "Trigger wrong halt step challenge transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx.get_txid()
        )
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_equivocation_tx
