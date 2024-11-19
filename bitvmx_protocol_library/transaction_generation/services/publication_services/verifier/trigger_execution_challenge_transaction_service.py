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
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_generic_challenge_script_generator_service import (
    TriggerGenericChallengeScriptGeneratorService,
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
        self.bitvmx_bitcoin_scripts_generator_service = BitVMXBitcoinScriptsGeneratorService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):

        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )

        trigger_execution_challenge_signature = (
            bitvmx_protocol_verifier_dto.trigger_execution_challenge_signatures
        )

        consumed_items = 0
        trace_values = []
        for i in range(
            len(
                bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys
            )
        ):
            current_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys[
                i
            ]
            current_length = trace_words_lengths[i]
            current_witness = bitvmx_protocol_verifier_dto.prover_trace_witness[
                len(bitvmx_protocol_verifier_dto.prover_trace_witness)
                - (len(current_public_keys) * 2 + consumed_items) : len(
                    bitvmx_protocol_verifier_dto.prover_trace_witness
                )
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
                step=3
                + bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                * 2,
                case=len(trace_words_lengths) - word_count - 1,
                input_numbers=input_number,
                bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            )

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

        challenge_scripts_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_challenge_taptree,
            index=bitvmx_bitcoin_scripts_dto.trigger_challenge_index(0),
            is_odd=trigger_challenge_scripts_address.is_odd(),
        )

        trigger_challenge_witness = []

        processed_values = 0
        for i in reversed(range(len(trace_words_lengths))):
            trigger_challenge_witness += bitvmx_protocol_verifier_dto.prover_trace_witness[
                processed_values : processed_values
                + len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
                        i
                    ]
                )
                * 2
            ]
            trigger_challenge_witness += verifier_trigger_challenge_witness[
                processed_values : processed_values
                + len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys[
                        i
                    ]
                )
                * 2
            ]
            processed_values += (
                len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
                        i
                    ]
                )
                * 2
            )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_execution_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_execution_challenge_signature
                + trigger_challenge_witness
                + [
                    bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list[0].to_hex(),
                    challenge_scripts_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_execution_challenge_tx.serialize()
        )
        print(
            "Trigger execution challenge transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_execution_challenge_tx.get_txid()
        )
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_execution_challenge_tx
        )
