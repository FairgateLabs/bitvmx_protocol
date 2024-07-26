from bitvmx_protocol_library.script_generation.services.execution_challenge_script_list_generator_service import (
    ExecutionChallengeScriptListGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.execution_trace_script_generator_service import (
    ExecutionTraceScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.hash_result_script_generator_service import (
    HashResultScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.commit_search_hashes_script_generator_service import (
    CommitSearchHashesScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.trigger_generic_challenge_script_generator_service import (
    TriggerGenericChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.trigger_protocol_script_generator_service import (
    TriggerProtocolScriptGeneratorService,
)


class ScriptsDictGeneratorService:

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

    def __call__(self, protocol_dict):

        amount_of_bits_per_digit_checksum = protocol_dict["amount_of_bits_per_digit_checksum"]
        amount_of_wrong_step_search_iterations = protocol_dict[
            "amount_of_wrong_step_search_iterations"
        ]
        amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]
        amount_of_nibbles_hash = protocol_dict["amount_of_nibbles_hash"]
        hash_result_public_keys = protocol_dict["hash_result_public_keys"]
        hash_search_public_keys_list = protocol_dict["hash_search_public_keys_list"]
        choice_search_prover_public_keys_list = protocol_dict[
            "choice_search_prover_public_keys_list"
        ]
        choice_search_verifier_public_keys_list = protocol_dict[
            "choice_search_verifier_public_keys_list"
        ]
        trace_words_lengths = protocol_dict["trace_words_lengths"]
        trace_prover_public_keys = protocol_dict["trace_prover_public_keys"]
        trace_verifier_public_keys = protocol_dict["trace_verifier_public_keys"]
        signature_public_keys = protocol_dict["public_keys"]

        scripts_dict = {}

        scripts_dict["hash_result_script"] = self.hash_result_script_generator(
            signature_public_keys,
            hash_result_public_keys,
            amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum,
        )

        scripts_dict["trigger_protocol_script"] = self.trigger_protocol_script_generator(
            signature_public_keys
        )

        hash_search_scripts = []
        choice_search_scripts = []
        for iter_count in range(amount_of_wrong_step_search_iterations):
            # Hash
            current_hash_public_keys = hash_search_public_keys_list[iter_count]
            if iter_count > 0:
                previous_choice_verifier_public_keys = choice_search_verifier_public_keys_list[
                    iter_count - 1
                ]
                current_choice_prover_public_keys = choice_search_prover_public_keys_list[
                    iter_count - 1
                ]
                current_search_script = self.commit_search_hashes_script_generator_service(
                    signature_public_keys,
                    current_hash_public_keys,
                    amount_of_nibbles_hash,
                    amount_of_bits_per_digit_checksum,
                    amount_of_bits_wrong_step_search,
                    current_choice_prover_public_keys[0],
                    previous_choice_verifier_public_keys[0],
                )
            else:
                current_search_script = self.commit_search_hashes_script_generator_service(
                    signature_public_keys,
                    current_hash_public_keys,
                    amount_of_nibbles_hash,
                    amount_of_bits_per_digit_checksum,
                )

            hash_search_scripts.append(current_search_script)

            # Choice
            current_choice_public_keys = choice_search_verifier_public_keys_list[iter_count]
            current_choice_script = self.commit_search_choice_script_generator_service(
                signature_public_keys,
                current_choice_public_keys[0],
                amount_of_bits_wrong_step_search,
            )
            choice_search_scripts.append(current_choice_script)

        scripts_dict["hash_search_scripts"] = hash_search_scripts
        scripts_dict["choice_search_scripts"] = choice_search_scripts

        scripts_dict["trace_script"] = self.execution_trace_script_generator_service(
            signature_public_keys,
            trace_prover_public_keys,
            trace_words_lengths,
            amount_of_bits_per_digit_checksum,
            amount_of_bits_wrong_step_search,
            choice_search_prover_public_keys_list[-1][0],
            choice_search_verifier_public_keys_list[-1][0],
        )

        scripts_dict["trigger_execution_script"] = (
            self.verifier_challenge_execution_script_generator_service(
                trace_prover_public_keys,
                trace_verifier_public_keys,
                signature_public_keys,
                trace_words_lengths,
                amount_of_bits_per_digit_checksum,
            )
        )

        scripts_dict["trigger_challenge_scripts"] = [[scripts_dict["trigger_execution_script"]]]

        scripts_dict["execution_challenge_script_list"] = (
            self.execution_challenge_script_list_generator_service(
                signature_public_keys,
                trace_verifier_public_keys,
                trace_words_lengths,
                amount_of_bits_per_digit_checksum,
            )
        )

        return scripts_dict
