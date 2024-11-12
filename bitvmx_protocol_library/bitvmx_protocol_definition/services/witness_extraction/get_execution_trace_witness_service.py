from abc import abstractmethod
from typing import Generic, List, TypeVar

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.execution_trace_witness_dto import (
    ExecutionTraceWitnessDTO,
    ReadExecutionTraceWitnessDTO,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)

ReturnType = TypeVar("ReturnType", ExecutionTraceWitnessDTO, ReadExecutionTraceWitnessDTO)


class GenericGetExecutionTraceWitnessService(Generic[ReturnType]):
    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> ReturnType:
        execution_transaction = transaction_info_service(
            tx_id=self._get_execution_transaction(
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
            ).get_txid()
        )
        public_keys = self._get_public_keys(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        vectorized_witness = self.vectorize_witness(
            witness=execution_transaction.inputs[0].witness.copy(), public_keys=public_keys
        )
        return self._get_return_value(vectorized_witness=vectorized_witness)

    @staticmethod
    def vectorize_witness(witness: List[str], public_keys: List[List[str]]) -> List[List[str]]:
        # Remove signatures
        while len(witness[0]) == 128:
            witness = witness[1:]
        # Remove the cross signing of the choice
        witness = witness[8:]
        vectorized_witness = []
        for word in reversed(public_keys):
            current_length = 2 * len(word)
            current_witness = witness[:current_length]
            assert len(current_witness) == current_length
            witness = witness[current_length:]
            vectorized_witness.append(current_witness)
        assert len(witness) == 2
        return vectorized_witness

    @abstractmethod
    def _get_execution_transaction(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        pass

    @abstractmethod
    def _get_public_keys(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        pass

    @abstractmethod
    def _get_return_value(self, vectorized_witness: List[List[str]]) -> ReturnType:
        pass

    def _get_read_execution_trace_witness_dto(
        self, vectorized_witness: List[List[str]]
    ) -> ReadExecutionTraceWitnessDTO:
        return ReadExecutionTraceWitnessDTO(
            write_address=vectorized_witness[
                BitVMXProtocolPropertiesDTO.read_write_address_position
            ],
            write_value=vectorized_witness[BitVMXProtocolPropertiesDTO.read_write_value_position],
            write_PC_address=vectorized_witness[
                BitVMXProtocolPropertiesDTO.read_write_pc_address_position
            ],
            write_micro=vectorized_witness[
                BitVMXProtocolPropertiesDTO.read_write_pc_micro_position
            ],
        )

    def _get_execution_trace_witness_dto(
        self, vectorized_witness: List[List[str]]
    ) -> ExecutionTraceWitnessDTO:
        read_execution_trace_witness_dto = self._get_read_execution_trace_witness_dto(
            vectorized_witness=vectorized_witness
        )
        return ExecutionTraceWitnessDTO(
            read_1_address=vectorized_witness[BitVMXProtocolPropertiesDTO.read_1_address_position],
            read_1_value=vectorized_witness[BitVMXProtocolPropertiesDTO.read_1_value_position],
            read_1_last_step=vectorized_witness[
                BitVMXProtocolPropertiesDTO.read_1_last_step_position
            ],
            read_2_address=vectorized_witness[BitVMXProtocolPropertiesDTO.read_2_address_position],
            read_2_value=vectorized_witness[BitVMXProtocolPropertiesDTO.read_2_value_position],
            read_2_last_step=vectorized_witness[
                BitVMXProtocolPropertiesDTO.read_2_last_step_position
            ],
            opcode=vectorized_witness[BitVMXProtocolPropertiesDTO.read_pc_opcode_position],
            read_PC_address=vectorized_witness[
                BitVMXProtocolPropertiesDTO.read_pc_address_position
            ],
            read_micro=vectorized_witness[BitVMXProtocolPropertiesDTO.read_pc_micro_position],
            **read_execution_trace_witness_dto.dict(),
        )


class GetExecutionTraceWitnessService(
    GenericGetExecutionTraceWitnessService[ExecutionTraceWitnessDTO]
):
    def _get_execution_transaction(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx

    def _get_public_keys(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.trace_prover_public_keys
        )

    def _get_return_value(self, vectorized_witness: List[List[str]]) -> ExecutionTraceWitnessDTO:
        return self._get_execution_trace_witness_dto(vectorized_witness=vectorized_witness)


class GetReadExecutionTraceWitnessService(
    GenericGetExecutionTraceWitnessService[ReadExecutionTraceWitnessDTO]
):
    def _get_execution_transaction(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_trace_tx

    def _get_public_keys(
        self, bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO
    ):
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_prover_winternitz_public_keys_dto.read_trace_prover_public_keys
        )

    def _get_return_value(
        self, vectorized_witness: List[List[str]]
    ) -> ReadExecutionTraceWitnessDTO:
        return self._get_read_execution_trace_witness_dto(vectorized_witness=vectorized_witness)
