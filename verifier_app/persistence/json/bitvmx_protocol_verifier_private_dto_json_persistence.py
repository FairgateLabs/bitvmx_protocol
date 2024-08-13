import json
import os

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_private_dto import (
    BitVMXProtocolVerifierPrivateDTO,
)
from verifier_app.domain.persistences.interfaces.bitvmx_protocol_verifier_private_dto_persistence_interface import (
    BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
)


class BitVMXProtocolVerifierPrivateDTOJsonPersistence(
    BitVMXProtocolVerifierPrivateDTOPersistenceInterface
):

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.file_name = "bitvmx_protocol_verifier_private_dto.json"
        self.private_keys_dict = {}

    def create(
        self,
        setup_uuid: str,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
    ) -> bool:
        folder_path = f"{self.base_path}/{setup_uuid}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        private_key = bitvmx_protocol_verifier_private_dto.destroyed_private_key
        bitvmx_protocol_verifier_private_dto.destroyed_private_key = None
        with open(f"{folder_path}/{self.file_name}", "w") as file:
            json.dump(bitvmx_protocol_verifier_private_dto.model_dump(), file)
        self.private_keys_dict[setup_uuid] = private_key
        return True

    def get(self, setup_uuid: str) -> BitVMXProtocolVerifierPrivateDTO:
        file_path = f"{self.base_path}/{setup_uuid}/{self.file_name}"
        with open(file_path, "r") as file:
            json_data = json.load(file)
        return BitVMXProtocolVerifierPrivateDTO(
            winternitz_private_key=json_data["winternitz_private_key"],
            destroyed_private_key=(
                self.private_keys_dict[setup_uuid] if setup_uuid in self.private_keys_dict else None
            ),
            verifier_signature_private_key=json_data["verifier_signature_private_key"],
        )

    def delete_private_key(self, setup_uuid: str) -> bool:
        private_key = self.private_keys_dict.pop(setup_uuid, None)
        if private_key is None:
            return False
        return True
