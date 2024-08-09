import json
import os

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from verifier_app.domain.persistences.interfaces.bitvmx_protocol_setup_properties_dto_persistence_interface import (
    BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
)


class BitVMXProtocolSetupPropertiesDTOJsonPersistence(
    BitVMXProtocolSetupPropertiesDTOPersistenceInterface
):

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.file_name = "bitvmx_protocol_setup_properties_dto.json"

    def create(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> bool:
        folder_path = f"{self.base_path}/{bitvmx_protocol_setup_properties_dto.setup_uuid}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(f"{folder_path}/{self.file_name}", "w") as file:
            json.dump(bitvmx_protocol_setup_properties_dto.model_dump(), file)
        return True

    def get(self, setup_uuid: str) -> BitVMXProtocolSetupPropertiesDTO:
        file_path = f"{self.base_path}/{setup_uuid}/{self.file_name}"
        with open(file_path, "r") as file:
            json_data = json.load(file)
        return BitVMXProtocolSetupPropertiesDTO(**json_data)
