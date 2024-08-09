from abc import ABC, abstractmethod

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_private_dto import (
    BitVMXProtocolVerifierPrivateDTO,
)


class BitVMXProtocolVerifierPrivateDTOPersistenceInterface(ABC):

    @abstractmethod
    def create(
        self,
        setup_uuid: str,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
    ) -> bool:
        pass

    @abstractmethod
    def get(self, setup_uuid: str) -> BitVMXProtocolVerifierPrivateDTO:
        pass

    @abstractmethod
    def delete_private_key(self, setup_uuid: str) -> bool:
        pass
