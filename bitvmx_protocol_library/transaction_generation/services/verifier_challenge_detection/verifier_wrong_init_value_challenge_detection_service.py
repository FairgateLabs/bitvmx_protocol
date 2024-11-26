from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.input_and_constant_addresses_generation_service import (
    InputAndConstantAddressesGenerationService,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from bitvmx_protocol_library.transaction_generation.services.publication_services.verifier.trigger_wrong_init_value_challenge_transaction_service import (
    TriggerWrongInitValue1ChallengeTransactionService,
    TriggerWrongInitValue2ChallengeTransactionService,
)


class VerifierWrongInitValueChallengeDetectionService:
    def __init__(self):
        pass

    @staticmethod
    def _address_in_interval(address: str, init: str, end: str) -> bool:
        return int(address, 16) >= int(init, 16) and int(address, 16) <= int(end, 16)

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        input_and_constant_addresses = input_and_constant_addresses_generation_service(
            input_length=bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
        )
        memory_regions = input_and_constant_addresses.memory_regions()
        execution_trace = bitvmx_protocol_verifier_dto.published_execution_trace

        if int(execution_trace.read_1_value, 16) != 0 and int(
            execution_trace.read_1_last_step, 16
        ) == int(execution_trace.not_written_last_step(), 16):
            address_in_interval = False
            for memory_region in memory_regions:
                address_in_interval = address_in_interval or self._address_in_interval(
                    address=execution_trace.read_1_address,
                    init=memory_region.init,
                    end=memory_region.end,
                )
            if not address_in_interval:
                return (
                    TriggerWrongInitValue1ChallengeTransactionService,
                    TransactionVerifierStepType.TRIGGER_WRONG_INPUT_VALUE_CHALLENGE_1,
                )
        elif int(execution_trace.read_2_value, 16) != 0 and int(
            execution_trace.read_2_last_step, 16
        ) == int(execution_trace.not_written_last_step(), 16):
            address_in_interval = False
            for memory_region in memory_regions:
                address_in_interval = address_in_interval or self._address_in_interval(
                    address=execution_trace.read_2_address,
                    init=memory_region.init,
                    end=memory_region.end,
                )
            if not address_in_interval:
                return (
                    TriggerWrongInitValue2ChallengeTransactionService,
                    TransactionVerifierStepType.TRIGGER_WRONG_INPUT_VALUE_CHALLENGE_2,
                )
        return None, None
