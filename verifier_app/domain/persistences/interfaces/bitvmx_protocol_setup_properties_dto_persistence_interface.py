from abc import ABC, abstractmethod

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)


class BitVMXProtocolSetupPropertiesDTOPersistenceInterface(ABC):
    @abstractmethod
    def create(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> bool:
        pass

    @abstractmethod
    def get(self, setup_uuid: str) -> BitVMXProtocolSetupPropertiesDTO:
        pass
