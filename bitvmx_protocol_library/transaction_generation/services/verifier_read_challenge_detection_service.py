from bitvmx_protocol_library.bitvmx_execution.entities.read_execution_trace_dto import (
    ReadExecutionTraceDTO,
)
from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_query_service import (
    ExecutionTraceQueryService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_read_challenge_detection.verifier_wrong_hash_read_challenge_detection_service import (
    VerifierWrongHashReadChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_read_challenge_detection.verifier_wrong_latter_step_challenge_detection_service import (
    VerifierWrongLatterStepChallengeDetectionService,
)
from bitvmx_protocol_library.transaction_generation.services.verifier_read_challenge_detection.verifier_wrong_value_address_read_challenge_detection_service import (
    VerifierWrongValueAddressReadChallengeDetectionService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class VerifierReadChallengeDetectionService:
    def __init__(self):
        self.verifier_read_challenge_detection_services = [
            VerifierWrongHashReadChallengeDetectionService(),
            VerifierWrongValueAddressReadChallengeDetectionService(),
            VerifierWrongLatterStepChallengeDetectionService(),
        ]
        self.execution_trace_query_service = ExecutionTraceQueryService("verifier_files/")

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        read_trace_tx_id = (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_trace_tx.get_txid()
        )
        read_trace_transaction_info = transaction_info_service(read_trace_tx_id)
        previous_trace_witness = read_trace_transaction_info.inputs[0].witness

        # Ugly hardcoding here that should be computed somehow but it depends a lot on the structure of the
        # previous script
        # -> Make static call that gets checked when the script gets generated
        amount_of_signatures = bitvmx_protocol_verifier_dto.amount_of_signatures
        read_trace_witness_length = (
            sum(
                list(
                    map(
                        lambda x: len(x),
                        bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.read_trace_verifier_public_keys,
                    )
                )
            )
            * 2
        )
        # The 8 comes from publishing a nibble with its checksum twice (so it can be cross signed)
        prover_read_trace_witness = previous_trace_witness[
            amount_of_signatures + 8 : amount_of_signatures + 8 + read_trace_witness_length
        ]
        bitvmx_protocol_verifier_dto.prover_read_trace_witness = prover_read_trace_witness

        write_trace_words_lengths = bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.write_trace_words_lengths[
            ::-1
        ]

        consumed_items = 0
        trace_values = []
        for i in range(
            len(
                bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.read_trace_verifier_public_keys
            )
        ):
            current_public_keys = bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto.read_trace_verifier_public_keys[
                i
            ]
            current_length = write_trace_words_lengths[i]
            current_witness = prover_read_trace_witness[
                len(prover_read_trace_witness)
                - (len(current_public_keys) * 2 + consumed_items) : len(prover_read_trace_witness)
                - consumed_items
            ]
            consumed_items += len(current_public_keys) * 2
            current_witness_values = current_witness[1 : 2 * current_length : 2]
            current_digits = list(
                map(lambda elem: elem[1] if len(elem) > 0 else "0", current_witness_values)
            )
            current_value = "".join(reversed(current_digits))
            trace_values.append(current_value)

        bitvmx_protocol_verifier_dto.published_read_execution_trace = (
            ReadExecutionTraceDTO.from_trace_values_list(trace_values)
        )

        read_revealed_step = int(
            "".join(
                map(
                    lambda digit: bin(digit)[2:].zfill(
                        bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search
                    ),
                    bitvmx_protocol_verifier_dto.read_search_choices,
                )
            ),
            2,
        )
        bitvmx_protocol_verifier_dto.read_revealed_step = read_revealed_step

        for verifier_challenge_detection_service in self.verifier_read_challenge_detection_services:
            trigger_challenge_transaction_service, transaction_step_type = (
                verifier_challenge_detection_service(
                    setup_uuid=bitvmx_protocol_setup_properties_dto.setup_uuid,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
            )
            if (
                trigger_challenge_transaction_service is not None
                and transaction_step_type is not None
            ):
                return trigger_challenge_transaction_service, transaction_step_type

        raise Exception("No challenge detected")
