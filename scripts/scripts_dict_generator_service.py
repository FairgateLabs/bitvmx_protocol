import hashlib

from bitcoinutils.keys import PublicKey

from scripts.services.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from scripts.services.commit_search_hashes_script_generator_service import (
    CommitSearchHashesScriptGeneratorService,
)
from scripts.services.execution_trace_script_generator_service import (
    ExecutionTraceScriptGeneratorService,
)
from scripts.services.hash_result_script_generator_service import HashResultScriptGeneratorService
from scripts.services.trigger_protocol_script_generator_service import (
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

    def __call__(self, protocol_dict):

        amount_of_bits_per_digit_checksum = protocol_dict["amount_of_bits_per_digit_checksum"]
        amount_of_wrong_step_search_iterations = protocol_dict[
            "amount_of_wrong_step_search_iterations"
        ]
        amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]
        amount_of_wrong_step_search_hashes_per_iteration = protocol_dict[
            "amount_of_wrong_step_search_hashes_per_iteration"
        ]
        amount_of_nibbles_hash = protocol_dict["amount_of_nibbles_hash"]
        seed_destroyed_public_key_hex = protocol_dict["seed_destroyed_public_key_hex"]
        destroyed_public_key_hex = hashlib.sha256(
            bytes.fromhex(seed_destroyed_public_key_hex)
        ).hexdigest()
        destroyed_public_key = PublicKey(hex_str="02" + destroyed_public_key_hex)
        prover_public_key = protocol_dict["prover_public_key"]
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

        scripts_dict = {}

        scripts_dict["hash_result_script"] = self.hash_result_script_generator(
            prover_public_key,
            hash_result_public_keys,
            amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum,
        )

        scripts_dict["trigger_protocol_script"] = self.trigger_protocol_script_generator()

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
                    current_hash_public_keys,
                    amount_of_nibbles_hash,
                    amount_of_bits_per_digit_checksum,
                    amount_of_bits_wrong_step_search,
                    current_choice_prover_public_keys[0],
                    previous_choice_verifier_public_keys[0],
                )
            else:
                current_search_script = self.commit_search_hashes_script_generator_service(
                    current_hash_public_keys,
                    amount_of_nibbles_hash,
                    amount_of_bits_per_digit_checksum,
                )

            hash_search_scripts.append(current_search_script)

            # Choice
            current_choice_public_keys = choice_search_verifier_public_keys_list[iter_count]
            current_choice_script = self.commit_search_choice_script_generator_service(
                current_choice_public_keys[0],
                amount_of_bits_wrong_step_search,
            )
            choice_search_scripts.append(current_choice_script)

        scripts_dict["hash_search_scripts"] = hash_search_scripts
        scripts_dict["choice_search_scripts"] = choice_search_scripts

        # hash_search_scripts_addresses = list(
        #     map(
        #         lambda search_script: destroyed_public_key.get_taproot_address([[search_script]]),
        #         hash_search_scripts,
        #     )
        # )
        #
        # choice_search_scripts_addresses = list(
        #     map(
        #         lambda choice_script: destroyed_public_key.get_taproot_address([[choice_script]]),
        #         choice_search_scripts,
        #     )
        # )

        scripts_dict["trace_script"] = self.execution_trace_script_generator_service(
            trace_prover_public_keys,
            trace_words_lengths,
            amount_of_bits_per_digit_checksum,
            amount_of_bits_wrong_step_search,
            choice_search_prover_public_keys_list[-1][0],
            choice_search_verifier_public_keys_list[-1][0],
        )
        # trace_script_address = destroyed_public_key.get_taproot_address([[trace_script]])

        return scripts_dict