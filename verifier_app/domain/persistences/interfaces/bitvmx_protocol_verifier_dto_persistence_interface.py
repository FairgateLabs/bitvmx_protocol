from abc import ABC, abstractmethod

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)


class BitVMXProtocolVerifierDTOPersistenceInterface(ABC):

    @abstractmethod
    def create(
        self, setup_uuid: str, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO
    ) -> bool:
        pass

    @abstractmethod
    def get(self, setup_uuid: str) -> BitVMXProtocolVerifierDTO:
        pass

    @abstractmethod
    def update(
        self, setup_uuid: str, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO
    ) -> bool:
        pass
