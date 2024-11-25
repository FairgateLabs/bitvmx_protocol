from bitvmx_protocol_library.bitvmx_execution.entities.execution_trace_dto import ExecutionTraceDTO
from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_execution_challenge_detection_service import (
    VerifierExecutionChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_last_hash_equivocation_challenge_detection_service import (
    VerifierLastHashEquivocationChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_no_halt_in_halt_step_challenge_detection_service import (
    VerifierNoHaltInHaltStepChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_read_constant_equivocation_challenge_detection_service import (
    VerifierReadConstantEquivocationChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_read_input_equivocation_challenge_detection_service import (
    VerifierReadInputEquivocationChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_read_search_challenge_detection_service import (
    VerifierReadSearchChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_wrong_halt_step_challenge_detection_service import (
    VerifierWrongHaltStepChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_wrong_hash_challenge_detection_service import (
    VerifierWrongHashChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_wrong_init_value_challenge_detection_service import (
    VerifierWrongInitValueChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_challenge_detection.verifier_wrong_program_counter_challenge_detection_service import (
    VerifierWrongProgramCounterChallengeDetectionService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class VerifierChallengeDetectionService:
    def __init__(self):
        self.verifier_challenge_detection_services = [
            VerifierWrongInitValueChallengeDetectionService(),
            VerifierWrongHashChallengeDetectionService(),
            VerifierLastHashEquivocationChallengeDetectionService(),
            VerifierWrongHaltStepChallengeDetectionService(),
            VerifierNoHaltInHaltStepChallengeDetectionService(),
            VerifierWrongProgramCounterChallengeDetectionService(),
            VerifierReadInputEquivocationChallengeDetectionService(),
            VerifierReadConstantEquivocationChallengeDetectionService(),
            VerifierReadSearchChallengeDetectionService(),
            VerifierExecutionChallengeDetectionService(),
        ]
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        trace_tx_id = (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx.get_txid()
        )
        trace_transaction_info = transaction_info_service(trace_tx_id)
        previous_trace_witness = trace_transaction_info.inputs[0].witness

        # Ugly hardcoding here that should be computed somehow but it depends a lot on the structure of the
        # previous script
        # -> Make static call that gets checked when the script gets generated
        amount_of_signatures = bitvmx_protocol_verifier_dto.amount_of_signatures
        trace_witness_length = (
            sum(
                list(
                    map(
                        lambda x: len(x),
                        bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.trace_verifier_public_keys,
                    )
                )
            )
            * 2
        )
        # The 8 comes from publishing a nibble with its checksum twice (so it can be cross signed)
        prover_trace_witness = previous_trace_witness[
            amount_of_signatures + 8 : amount_of_signatures + 8 + trace_witness_length
        ]
        bitvmx_protocol_verifier_dto.prover_trace_witness = prover_trace_witness

        trace_words_lengths = (
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.trace_words_lengths[
                ::-1
            ]
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

        bitvmx_protocol_verifier_dto.published_execution_trace = (
            ExecutionTraceDTO.from_trace_values_list(trace_values)
        )

        first_wrong_step = int(
            "".join(
                map(
                    lambda digit: bin(digit)[2:].zfill(
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    ),
                    bitvmx_protocol_verifier_dto.search_choices,
                )
            ),
            2,
        )
        bitvmx_protocol_verifier_dto.first_wrong_step = first_wrong_step

        real_execution_trace_series = self.execution_trace_query_service(
            setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid,
            index=first_wrong_step,
            input_hex=bitvmx_protocol_verifier_dto.input_hex,
        )
        bitvmx_protocol_verifier_dto.real_execution_trace = ExecutionTraceDTO.from_pandas_series(
            execution_trace=real_execution_trace_series, trace_words_lengths=trace_words_lengths
        )

        for verifier_challenge_detection_service in self.verifier_challenge_detection_services:
            trigger_challenge_transaction_service, transaction_step_type = (
                verifier_challenge_detection_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
            )
            if (
                trigger_challenge_transaction_service is not None
                and transaction_step_type is not None
            ):
                return trigger_challenge_transaction_service, transaction_step_type

        raise Exception("No challenge detected")
