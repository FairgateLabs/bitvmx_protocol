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
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.commit_read_search_choice_script_generator_service import (
    CommitReadSearchChoiceScriptGeneratorService,
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
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_constant_equivocation_challenge_scripts_generator_service import (
    TriggerConstantEquivocationChallengeScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_input_equivocation_challenge_scripts_generator_service import (
    TriggerInputEquivocationChallengeScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_list_generator_services.verifier.trigger_read_challenge_scripts_generator_service import (
    TriggerReadChallengeScriptsGeneratorService,
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
        self.commit_read_search_choice_script_generator_service = (
            CommitReadSearchChoiceScriptGeneratorService()
        )
        self.trigger_read_challenge_scripts_generator_service = (
            TriggerReadChallengeScriptsGeneratorService()
        )
        self.trigger_input_equivocation_challenge_scripts_generator_service = (
            TriggerInputEquivocationChallengeScriptsGeneratorService()
        )
        self.trigger_constant_equivocation_challenge_scripts_generator_service = (
            TriggerConstantEquivocationChallengeScriptsGeneratorService()
        )
        self.input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )

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

        hash_result_script = self.hash_result_script_generator(
            signature_public_keys=signature_public_keys,
            hash_result_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.hash_result_public_keys,
            halt_step_public_keys=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.halt_step_public_keys,
            input_public_keys_list=bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.input_public_keys,
            n0=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
            amount_of_nibbles_halt_step=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step,
            bits_per_digit_checksum=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_per_digit_checksum,
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

        trigger_read_challenge_scripts = self.trigger_read_challenge_scripts_generator_service(
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
        trigger_constant_1_equivocation_challenge_scripts_generator_service = (
            self.trigger_constant_equivocation_challenge_scripts_generator_service(
                signature_public_keys=[
                    bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
                ],
            )
        )
        trigger_constant_2_equivocation_challenge_scripts_generator_service = (
            self.trigger_constant_equivocation_challenge_scripts_generator_service(
                signature_public_keys=[
                    bitvmx_protocol_setup_properties_dto.verifier_signature_public_key
                ],
            )
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
            input_1_equivocation_challenge_scripts=trigger_input_1_equivocation_challenge_scripts_generator_service,
            input_2_equivocation_challenge_scripts=trigger_input_2_equivocation_challenge_scripts_generator_service,
            constants_1_equivocation_challenge_scripts=trigger_constant_1_equivocation_challenge_scripts_generator_service,
            constants_2_equivocation_challenge_scripts=trigger_constant_2_equivocation_challenge_scripts_generator_service,
            hash_read_search_scripts=hash_read_search_scripts,
            choice_read_search_scripts=choice_read_search_scripts,
            read_trace_script=read_trace_script,
            trigger_read_challenge_scripts=trigger_read_challenge_scripts,
        )
