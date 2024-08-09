from abc import ABC, abstractmethod

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_prover_dto import (
    BitVMXProtocolProverDTO,
)


class BitVMXProtocolProverDTOPersistenceInterface(ABC):

    @abstractmethod
    def create(self, setup_uuid: str, bitvmx_protocol_prover_dto: BitVMXProtocolProverDTO) -> bool:
        pass

    @abstractmethod
    def get(self, setup_uuid: str) -> BitVMXProtocolProverDTO:
        pass

    @abstractmethod
    def update(self, setup_uuid: str, bitvmx_protocol_prover_dto: BitVMXProtocolProverDTO) -> bool:
        pass
