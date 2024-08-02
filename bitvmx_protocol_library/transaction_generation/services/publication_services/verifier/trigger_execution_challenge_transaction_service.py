from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import \
    BitVMXProtocolSetupPropertiesDTO
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import (
    BitVMXProverWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.trigger_generic_challenge_script_generator_service import (
    TriggerGenericChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_transactions_dto import (
    BitVMXTransactionsDTO,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class TriggerExecutionChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.verifier_challenge_execution_script_generator_service = (
            TriggerGenericChallengeScriptGeneratorService()
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            verifier_private_key
        )

    def __call__(
        self,
        protocol_dict,
        bitvmx_transactions_dto: BitVMXTransactionsDTO,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_prover_winternitz_public_keys_dto: BitVMXProverWinternitzPublicKeysDTO,
        bitvmx_verifier_winternitz_public_keys_dto: BitVMXVerifierWinternitzPublicKeysDTO,
    ):

        trace_words_lengths = bitvmx_protocol_properties_dto.trace_words_lengths[::-1]

        # Ugly hardcoding here that should be computed somehow but it depends a lot on the structure of the
        # previous script
        # -> Make static call that gets checked when the script gets generated
        # prover_trigger_challenge_witness = previous_trace_witness[10:246]

        prover_trace_witness = protocol_dict["prover_trace_witness"]

        signature_public_keys = protocol_dict["public_keys"]
        trigger_execution_signatures = protocol_dict["trigger_execution_signatures"]

        consumed_items = 0
        trace_values = []
        for i in range(len(bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys)):
            current_public_keys = (
                bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys[i]
            )
            current_length = trace_words_lengths[i]
            current_witness = prover_trace_witness[
                len(prover_trace_witness)
                - (len(current_public_keys) * 2 + consumed_items) : len(prover_trace_witness)
                - consumed_items
            ]
            consumed_items += len(current_public_keys) * 2
            current_witness_values = current_witness[1 : 2 * current_length : 2]
            current_digits = list(
                map(lambda elem: elem[1] if len(elem) > 0 else "0", current_witness_values)
            )
            current_value = "".join(reversed(current_digits))
            trace_values.append(current_value)
        # ['00', '800000c8', '800002c4', 'e07ffffc', '06112623', '00', '800000c4', '00000001', '800002c4', 'f0000004', '00000002', 'e07fff90', 'f0000008']

        verifier_trigger_challenge_witness = []
        for word_count in range(len(trace_words_lengths)):

            input_number = []
            for letter in trace_values[len(trace_values) - word_count - 1]:
                input_number.append(int(letter, 16))

            verifier_trigger_challenge_witness += self.generate_witness_from_input_nibbles_service(
                step=3 + bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations * 2,
                case=len(trace_words_lengths) - word_count - 1,
                input_numbers=input_number,
                bits_per_digit_checksum=bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

        trigger_execution_script = self.verifier_challenge_execution_script_generator_service(
            bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys,
            signature_public_keys,
            trace_words_lengths,
            bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        # TODO: we should load this address from protocol dict as we add more challenges
        trigger_challenge_taptree = [[trigger_execution_script]]
        challenge_scripts_address = bitvmx_protocol_setup_properties_dto.unspendable_public_key.get_taproot_address(
            trigger_challenge_taptree
        )

        challenge_scripts_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_challenge_taptree,
            index=0,
            is_odd=challenge_scripts_address.is_odd(),
        )

        trigger_challenge_witness = []

        processed_values = 0
        for i in reversed(range(len(trace_words_lengths))):
            trigger_challenge_witness += prover_trace_witness[
                processed_values : processed_values
                + len(bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[i]) * 2
            ]
            trigger_challenge_witness += verifier_trigger_challenge_witness[
                processed_values : processed_values
                + len(bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys[i]) * 2
            ]
            processed_values += (
                len(bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[i]) * 2
            )

        bitvmx_transactions_dto.trigger_execution_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_execution_signatures
                + trigger_challenge_witness
                + [
                    trigger_execution_script.to_hex(),
                    challenge_scripts_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_transactions_dto.trigger_execution_challenge_tx.serialize()
        )
        print(
            "Trigger execution challenge transaction: "
            + bitvmx_transactions_dto.trigger_execution_challenge_tx.get_txid()
        )
        return bitvmx_transactions_dto.trigger_execution_challenge_tx
