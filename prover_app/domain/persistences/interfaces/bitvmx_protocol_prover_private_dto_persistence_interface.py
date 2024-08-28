from abc import ABC, abstractmethod

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_prover_private_dto import (
    BitVMXProtocolProverPrivateDTO,
)


class BitVMXProtocolProverPrivateDTOPersistenceInterface(ABC):

    @abstractmethod
    def create(
        self,
        setup_uuid: str,
        bitvmx_protocol_prover_private_dto: BitVMXProtocolProverPrivateDTO,
    ) -> bool:
        pass

    @abstractmethod
    def get(self, setup_uuid: str) -> BitVMXProtocolProverPrivateDTO:
        pass
