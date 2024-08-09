import json
import os

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from verifier_app.domain.persistences.interfaces.bitvmx_protocol_verifier_dto_persistence_interface import (
    BitVMXProtocolVerifierDTOPersistenceInterface,
)


class BitVMXProtocolVerifierDTOJsonPersistence(BitVMXProtocolVerifierDTOPersistenceInterface):

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.file_name = "bitvmx_protocol_verifier_dto.json"

    def create(
        self,
        setup_uuid: str,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ) -> bool:
        folder_path = f"{self.base_path}/{setup_uuid}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(f"{folder_path}/{self.file_name}", "w") as file:
            json.dump(bitvmx_protocol_verifier_dto.model_dump(), file)
        return True

    def get(self, setup_uuid: str) -> BitVMXProtocolVerifierDTO:
        file_path = f"{self.base_path}/{setup_uuid}/{self.file_name}"
        with open(file_path, "r") as file:
            json_data = json.load(file)
        return BitVMXProtocolVerifierDTO(**json_data)

    def update(
        self, setup_uuid: str, bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO
    ) -> bool:
        file_path = f"{self.base_path}/{setup_uuid}/{self.file_name}"
        if not os.path.exists(file_path):
            raise Exception(f"BitVMXProtocolVerifierDTO not found for id {setup_uuid}")
        with open(file_path, "w") as file:
            json.dump(bitvmx_protocol_verifier_dto.model_dump(), file)
        return True
