from fastapi import HTTPException

from prover_app.domain.persistences.interfaces.bitvmx_protocol_prover_dto_persistence_interface import (
    BitVMXProtocolProverDTOPersistenceInterface,
)
from prover_app.domain.persistences.interfaces.bitvmx_protocol_setup_properties_dto_persistence_interface import (
    BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
)


class InputController:
    def __init__(
        self,
        bitvmx_protocol_setup_properties_dto_persistence: BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
        bitvmx_protocol_prover_dto_persistence: BitVMXProtocolProverDTOPersistenceInterface,
    ):
        self.bitvmx_protocol_setup_properties_dto_persistence = (
            bitvmx_protocol_setup_properties_dto_persistence
        )
        self.bitvmx_protocol_prover_dto_persistence = bitvmx_protocol_prover_dto_persistence

    def __call__(self, setup_uuid: str, input_hex: str):
        bitvmx_protocol_setup_properties_dto = (
            self.bitvmx_protocol_setup_properties_dto_persistence.get(setup_uuid=setup_uuid)
        )
        if (
            not bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words
            * 8
            == len(input_hex)
        ):
            raise HTTPException(
                status_code=417,
                detail=f"Input hex should be {bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_input_words * 8} chars long",
            )

        try:
            int(input_hex, 16)
        except ValueError:
            raise HTTPException(status_code=417, detail="Input hex should be a valid hex string")

        bitvmx_protocol_prover_dto = self.bitvmx_protocol_prover_dto_persistence.get(
            setup_uuid=setup_uuid
        )
        bitvmx_protocol_prover_dto.input_hex = input_hex
        self.bitvmx_protocol_prover_dto_persistence.update(
            setup_uuid=setup_uuid, bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto
        )
