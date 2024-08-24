from typing import List

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)
from bitvmx_protocol_library.script_generation.entities.dtos.bitvmx_bitcoin_scripts_dto import (
    BitVMXBitcoinScriptsDTO,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.commit_search_hashes_script_generator_service import (
    CommitSearchHashesScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.execution_trace_script_generator_service import (
    ExecutionTraceScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.hash_result_script_generator_service import (
    HashResultScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_generic_challenge_script_generator_service import (
    TriggerGenericChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_protocol_script_generator_service import (
    TriggerProtocolScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.prover.execution_challenge_script_list_generator_service import (
    ExecutionChallengeScriptListGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_wrong_hash_script_list_generator_service import (
    TriggerWrongHashScriptListGeneratorService,
)


class BitVMXBitcoinScriptsGeneratorService:

    def __init__(self):
        self.hash_result_script_generator = HashResultScriptGeneratorService()
        self.trigger_protocol_script_generator = TriggerProtocolScriptGeneratorService()
        self.commit_search_hashes_script_generator_service = (
            CommitSearchHashesScriptGeneratorService()
        )
        self.commit_search_choice_script_generator_service = (
            CommitSearchChoiceScriptGeneratorService()
        )
        self.execution_trace_script_generator_service = ExecutionTraceScriptGeneratorService()
        self.verifier_challenge_execution_script_generator_service = (
            TriggerGenericChallengeScriptGeneratorService()
        )
        self.execution_challenge_script_list_generator_service = (
            ExecutionChallengeScriptListGeneratorService()
        )
        self.trigger_wrong_hash_script_list_generator_service = (
            TriggerWrongHashScriptListGeneratorService()
        )

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        signature_public_keys: List[str],
    ) -> BitVMXBitcoinScriptsDTO:
        assert signature_public_keys == bitvmx_protocol_setup_properties_dto.signature_public_keys
        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )

        hash_result_script = self.hash_result_script_generator(
            signature_public_keys,
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_protocol_script = self.trigger_protocol_script_generator(signature_public_keys)

        hash_search_scripts = []
        choice_search_scripts = []
        for iter_count in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            # Hash
            current_hash_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[
                iter_count
            ]
            if iter_count > 0:
                previous_choice_verifier_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list[
                    iter_count - 1
                ]
                current_choice_prover_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list[
                    iter_count - 1
                ]
                current_search_script = self.commit_search_hashes_script_generator_service(
                    signature_public_keys,
                    current_hash_public_keys,
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
                    current_choice_prover_public_keys[0],
                    previous_choice_verifier_public_keys[0],
                )
            else:
                current_search_script = self.commit_search_hashes_script_generator_service(
                    signature_public_keys,
                    current_hash_public_keys,
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
                    bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
                )

            hash_search_scripts.append(current_search_script)

            # Choice
            current_choice_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list[
                iter_count
            ]
            current_choice_script = self.commit_search_choice_script_generator_service(
                signature_public_keys,
                current_choice_public_keys[0],
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            )
            choice_search_scripts.append(current_choice_script)

        hash_search_scripts = hash_search_scripts
        choice_search_scripts = choice_search_scripts

        trace_script = self.execution_trace_script_generator_service(
            signature_public_keys,
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            trace_words_lengths,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list[
                -1
            ][
                0
            ],
            bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list[
                -1
            ][
                0
            ],
        )

        trigger_execution_script = self.verifier_challenge_execution_script_generator_service(
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys,
            signature_public_keys,
            trace_words_lengths,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_challenge_scripts = BitcoinScriptList(trigger_execution_script)

        execution_challenge_script_list = self.execution_challenge_script_list_generator_service(
            signature_public_keys=signature_public_keys,
            public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys,
            trace_words_lengths=trace_words_lengths,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            prover_signature_public_key=bitvmx_protocol_setup_properties_dto.prover_signature_public_key,
        )

        wrong_hash_challenge_scripts_list = self.trigger_wrong_hash_script_list_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ],
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            hash_search_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list,
            choice_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            hash_result_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys,
            amount_of_nibbles_hash=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        return BitVMXBitcoinScriptsDTO(
            hash_result_script=hash_result_script,
            trigger_protocol_script=trigger_protocol_script,
            hash_search_scripts=hash_search_scripts,
            choice_search_scripts=choice_search_scripts,
            trace_script=trace_script,
            trigger_challenge_scripts=trigger_challenge_scripts,
            execution_challenge_script_list=execution_challenge_script_list,
            wrong_hash_challenge_script_list=wrong_hash_challenge_scripts_list,
        )
