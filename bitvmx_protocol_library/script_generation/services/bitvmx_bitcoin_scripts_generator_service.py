from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.input_and_constant_addresses_generation_service import (
    InputAndConstantAddressesGenerationService,
)
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
from bitvmx_protocol_library.script_generation.services.script_generation.prover.trigger_wrong_read_trace_step_script_generator_service import (
    TriggerWrongReadTraceStepScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.trigger_wrong_trace_step_script_generator_service import (
    TriggerWrongTraceStepScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.verifier_timeout_script_generator_service import (
    VerifierTimeoutScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.commit_read_search_choice_script_generator_service import (
    CommitReadSearchChoiceScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.prover_timeout_script_generator_service import (
    ProverTimeoutScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_generic_challenge_script_generator_service import (
    TriggerGenericChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_no_halt_in_halt_step_challenge_script_generator_service import (
    TriggerNoHaltInHaltStepChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_protocol_script_generator_service import (
    TriggerProtocolScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_halt_step_challenge_script_generator_service import (
    TriggerWrongHaltStepChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_init_value_script_generator_service import (
    TriggerWrongInitValue1ScriptGeneratorService,
    TriggerWrongInitValue2ScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_latter_step_challenge_script_generator_service import (
    TriggerWrongLatterStep1ChallengeScriptGeneratorService,
    TriggerWrongLatterStep2ChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_value_address_read_challenge_script_generator_service import (
    TriggerWrongValueAddressRead1ChallengeScriptGeneratorService,
    TriggerWrongValueAddressRead2ChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.prover.execution_challenge_script_list_generator_service import (
    ExecutionChallengeScriptListGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_constant_equivocation_challenge_scripts_generator_service import (
    TriggerConstantEquivocationChallengeScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_input_equivocation_challenge_scripts_generator_service import (
    TriggerInputEquivocationChallengeScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_last_hash_equivocation_challenge_scripts_generator_service import (
    TriggerLastHashEquivocationChallengeScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_read_challenge_scripts_generator_service import (
    TriggerReadChallengeScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_read_search_equivocation_scripts_generator_service import (
    TriggerReadSearchEquivocationScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_wrong_hash_script_list_generator_service import (
    TriggerWrongHashScriptListGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_wrong_program_counter_challenge_scripts_generator_service import (
    TriggerWrongProgramCounterChallengeScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_wrong_read_hash_challenge_scripts_generator_service import (
    TriggerWrongReadHashChallengeScriptsGeneratorService,
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
        self.trigger_wrong_program_counter_script_list_generator_service = (
            TriggerWrongProgramCounterChallengeScriptsGeneratorService()
        )
        self.commit_read_search_choice_script_generator_service = (
            CommitReadSearchChoiceScriptGeneratorService()
        )
        self.trigger_read_challenge_scripts_generator_service = (
            TriggerReadChallengeScriptsGeneratorService()
        )
        self.trigger_wrong_read_hash_challenge_scripts_generator_service = (
            TriggerWrongReadHashChallengeScriptsGeneratorService()
        )
        self.trigger_last_hash_equivocation_challenge_scripts_generator_service = (
            TriggerLastHashEquivocationChallengeScriptsGeneratorService()
        )
        self.trigger_input_equivocation_challenge_scripts_generator_service = (
            TriggerInputEquivocationChallengeScriptsGeneratorService()
        )
        self.trigger_constant_equivocation_challenge_scripts_generator_service = (
            TriggerConstantEquivocationChallengeScriptsGeneratorService()
        )
        self.trigger_wrong_latter_step_1_challenge_script_generator_service = (
            TriggerWrongLatterStep1ChallengeScriptGeneratorService()
        )
        self.trigger_wrong_latter_step_2_challenge_script_generator_service = (
            TriggerWrongLatterStep2ChallengeScriptGeneratorService()
        )
        self.trigger_wrong_value_address_read_1_challenge_script_generator_service = (
            TriggerWrongValueAddressRead1ChallengeScriptGeneratorService()
        )
        self.trigger_wrong_value_address_read_2_challenge_script_generator_service = (
            TriggerWrongValueAddressRead2ChallengeScriptGeneratorService()
        )
        self.trigger_wrong_halt_step_challenge_script_generator_service = (
            TriggerWrongHaltStepChallengeScriptGeneratorService()
        )
        self.trigger_no_halt_in_halt_step_challenge_script_generator_service = (
            TriggerNoHaltInHaltStepChallengeScriptGeneratorService()
        )
        self.trigger_wrong_trace_step_script_generator_service = (
            TriggerWrongTraceStepScriptGeneratorService()
        )
        self.trigger_wrong_read_trace_step_script_generator_service = (
            TriggerWrongReadTraceStepScriptGeneratorService()
        )
        self.trigger_read_search_equivocation_scripts_generator_service = (
            TriggerReadSearchEquivocationScriptsGeneratorService()
        )
        self.trigger_wrong_init_value_1_script_generator_service = (
            TriggerWrongInitValue1ScriptGeneratorService()
        )
        self.trigger_wrong_init_value_2_script_generator_service = (
            TriggerWrongInitValue2ScriptGeneratorService()
        )
        self.prover_timeout_script_generator_service = ProverTimeoutScriptGeneratorService()
        self.verifier_timeout_script_generator_service = VerifierTimeoutScriptGeneratorService()

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> BitVMXBitcoinScriptsDTO:
        signature_public_keys = bitvmx_protocol_setup_properties_dto.signature_public_keys
        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
        )
        read_trace_words_lengths = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.write_trace_words_lengths[
            ::-1
        ]

        hash_result_script = self.hash_result_script_generator(
            signature_public_keys=signature_public_keys,
            hash_result_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys,
            halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys,
            input_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.input_public_keys,
            n0=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            amount_of_nibbles_halt_step=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_protocol_script = self.trigger_protocol_script_generator(
            signature_public_keys=signature_public_keys,
            prover_halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys,
            verifier_halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.halt_step_public_keys,
            amount_of_nibbles_halt_step=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

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

        trigger_wrong_trace_step_script = self.trigger_wrong_trace_step_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.prover_signature_public_key
            ],
            verifier_halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.halt_step_public_keys,
            amount_of_nibbles_halt_step=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            choice_search_verifier_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list,
        )

        trigger_wrong_read_trace_step_script = self.trigger_wrong_read_trace_step_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.prover_signature_public_key
            ],
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            choice_search_verifier_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_search_verifier_public_keys_list,
            choice_read_search_verifier_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_read_search_verifier_public_keys_list,
        )

        trigger_execution_script = self.verifier_challenge_execution_script_generator_service(
            prover_trace_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            verifier_trace_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys,
            signature_public_keys=signature_public_keys,
            trace_words_lengths=trace_words_lengths,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
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

        wrong_program_counter_challenge_scripts_list = self.trigger_wrong_program_counter_script_list_generator_service(
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

        last_hash_equivocation_challenge_scripts_list = self.trigger_last_hash_equivocation_challenge_scripts_generator_service(
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

        hash_read_search_scripts = []
        choice_read_search_scripts = []
        for iter_count in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
            - 1
        ):
            # Hash
            current_hash_read_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_read_search_public_keys_list[
                iter_count
            ]
            previous_read_choice_verifier_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_read_search_verifier_public_keys_list[
                iter_count
            ]
            current_read_choice_prover_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list[
                iter_count
            ]
            current_read_search_script = self.commit_search_hashes_script_generator_service(
                signature_public_keys,
                current_hash_read_public_keys,
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
                current_read_choice_prover_public_keys[0],
                previous_read_choice_verifier_public_keys[0],
            )

            hash_read_search_scripts.append(current_read_search_script)

        for iter_count in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            # Choice
            current_read_choice_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_read_search_verifier_public_keys_list[
                iter_count
            ]
            current_read_choice_script = self.commit_read_search_choice_script_generator_service(
                signature_public_keys,
                current_read_choice_public_keys[0],
                bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            )
            choice_read_search_scripts.append(current_read_choice_script)

        write_trace_words_lengths = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.write_trace_words_lengths[
            ::-1
        ]

        read_trace_script = self.execution_trace_script_generator_service(
            signature_public_keys,
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.read_trace_prover_public_keys,
            write_trace_words_lengths,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list[
                -1
            ][
                0
            ],
            bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.choice_read_search_verifier_public_keys_list[
                -1
            ][
                0
            ],
        )

        trigger_read_wrong_hash_challenge_scripts = self.trigger_wrong_read_hash_challenge_scripts_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            read_trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.read_trace_prover_public_keys,
            trace_words_lengths=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ],
            write_trace_words_lengths=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.write_trace_words_lengths[
                ::-1
            ],
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            hash_read_search_public_keys_list=[
                bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list[
                    0
                ]
            ]
            + bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_read_search_public_keys_list,
            choice_read_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list,
            hash_result_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys,
            amount_of_nibbles_hash=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        self.input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        static_addresses = self.input_and_constant_addresses_generation_service(
            input_length=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        )

        address_1_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
            -1
            - bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_1_address_position
        ]
        address_1_amount_of_nibbles = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_1_address_position
        ]
        value_1_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
            -1
            - bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_1_value_position
        ]
        value_1_amount_of_nibbles = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_1_value_position
        ]

        address_2_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
            -1
            - bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_2_address_position
        ]
        address_2_amount_of_nibbles = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_2_address_position
        ]
        value_2_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys[
            -1
            - bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_2_value_position
        ]
        value_2_amount_of_nibbles = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.read_2_value_position
        ]

        trigger_input_1_equivocation_challenge_scripts_generator_service = self.trigger_input_equivocation_challenge_scripts_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            base_input_address=static_addresses.input.address,
            amount_of_input_words=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words,
            address_public_keys=address_1_public_keys,
            address_amount_of_nibbles=address_1_amount_of_nibbles,
            trace_value_public_keys=value_1_public_keys,
            publish_hash_value_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.input_public_keys,
            value_amount_of_nibbles=value_1_amount_of_nibbles,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_input_2_equivocation_challenge_scripts_generator_service = self.trigger_input_equivocation_challenge_scripts_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            base_input_address=static_addresses.input.address,
            amount_of_input_words=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words,
            address_public_keys=address_2_public_keys,
            address_amount_of_nibbles=address_2_amount_of_nibbles,
            trace_value_public_keys=value_2_public_keys,
            publish_hash_value_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.input_public_keys,
            value_amount_of_nibbles=value_2_amount_of_nibbles,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        trigger_constant_1_equivocation_challenge_scripts_generator_service = self.trigger_constant_equivocation_challenge_scripts_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            constant_memory_regions=static_addresses.constants,
            address_public_keys=address_1_public_keys,
            address_amount_of_nibbles=address_1_amount_of_nibbles,
            trace_value_public_keys=value_1_public_keys,
            value_amount_of_nibbles=value_1_amount_of_nibbles,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        trigger_constant_2_equivocation_challenge_scripts_generator_service = self.trigger_constant_equivocation_challenge_scripts_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            constant_memory_regions=static_addresses.constants,
            address_public_keys=address_2_public_keys,
            address_amount_of_nibbles=address_2_amount_of_nibbles,
            trace_value_public_keys=value_2_public_keys,
            value_amount_of_nibbles=value_2_amount_of_nibbles,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_wrong_value_address_read_1_challenge_script = self.trigger_wrong_value_address_read_1_challenge_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            read_trace_words_lengths=read_trace_words_lengths,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            choice_read_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            read_trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.read_trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        trigger_wrong_value_address_read_2_challenge_script = self.trigger_wrong_value_address_read_2_challenge_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            read_trace_words_lengths=read_trace_words_lengths,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            choice_read_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            read_trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.read_trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        trigger_wrong_latter_step_1_challenge_script = self.trigger_wrong_latter_step_1_challenge_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            read_trace_words_lengths=read_trace_words_lengths,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            choice_read_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            read_trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.read_trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        trigger_wrong_latter_step_2_challenge_script = self.trigger_wrong_latter_step_2_challenge_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            read_trace_words_lengths=read_trace_words_lengths,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            choice_read_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            read_trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.read_trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_wrong_halt_step_challenge_script = self.trigger_wrong_halt_step_challenge_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys,
            amount_of_nibbles_halt_step=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
            choice_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )
        trigger_no_halt_in_halt_step_challenge_script = self.trigger_no_halt_in_halt_step_challenge_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys,
            amount_of_nibbles_halt_step=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
            choice_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_read_search_equivocation_scripts = self.trigger_read_search_equivocation_scripts_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            hash_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_search_public_keys_list,
            hash_read_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_read_search_public_keys_list,
            amount_of_nibbles_hash=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            choice_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_search_prover_public_keys_list,
            choice_read_search_prover_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.choice_read_search_prover_public_keys_list,
            amount_of_bits_wrong_step_search=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        input_and_constant_addresses = input_and_constant_addresses_generation_service(
            input_length=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        )
        read_only_memory_regions = input_and_constant_addresses.memory_regions()

        trigger_wrong_init_value_1_script = self.trigger_wrong_init_value_1_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            read_only_memory_regions=read_only_memory_regions,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        trigger_wrong_init_value_2_script = self.trigger_wrong_init_value_2_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            trace_words_lengths=trace_words_lengths,
            read_only_memory_regions=read_only_memory_regions,
            trace_prover_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys,
            amount_of_bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
        )

        prover_timeout_script = self.prover_timeout_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
            ],
            timeout_wait_time=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.timeout_wait_time,
        )
        verifier_timeout_script = self.verifier_timeout_script_generator_service(
            signature_public_keys=[
                bitvmx_protocol_setup_properties_dto.prover_signature_public_key
            ],
            timeout_wait_time=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.timeout_wait_time,
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
            last_hash_equivocation_script_list=last_hash_equivocation_challenge_scripts_list,
            wrong_program_counter_challenge_scripts_list=wrong_program_counter_challenge_scripts_list,
            input_1_equivocation_challenge_scripts=trigger_input_1_equivocation_challenge_scripts_generator_service,
            input_2_equivocation_challenge_scripts=trigger_input_2_equivocation_challenge_scripts_generator_service,
            constants_1_equivocation_challenge_scripts=trigger_constant_1_equivocation_challenge_scripts_generator_service,
            constants_2_equivocation_challenge_scripts=trigger_constant_2_equivocation_challenge_scripts_generator_service,
            wrong_init_value_1_challenge_script=trigger_wrong_init_value_1_script,
            wrong_init_value_2_challenge_script=trigger_wrong_init_value_2_script,
            hash_read_search_scripts=hash_read_search_scripts,
            choice_read_search_scripts=choice_read_search_scripts,
            trigger_read_search_equivocation_scripts=trigger_read_search_equivocation_scripts,
            read_trace_script=read_trace_script,
            trigger_wrong_trace_step_script=trigger_wrong_trace_step_script,
            trigger_wrong_read_trace_step_script=trigger_wrong_read_trace_step_script,
            trigger_read_wrong_hash_challenge_scripts=trigger_read_wrong_hash_challenge_scripts,
            trigger_wrong_value_address_read_1_challenge_script=trigger_wrong_value_address_read_1_challenge_script,
            trigger_wrong_value_address_read_2_challenge_script=trigger_wrong_value_address_read_2_challenge_script,
            trigger_wrong_latter_step_1_challenge_script=trigger_wrong_latter_step_1_challenge_script,
            trigger_wrong_latter_step_2_challenge_script=trigger_wrong_latter_step_2_challenge_script,
            trigger_wrong_halt_step_challenge_script=trigger_wrong_halt_step_challenge_script,
            trigger_no_halt_in_halt_step_challenge_script=trigger_no_halt_in_halt_step_challenge_script,
            prover_timeout_script=prover_timeout_script,
            verifier_timeout_script=verifier_timeout_script,
        )
