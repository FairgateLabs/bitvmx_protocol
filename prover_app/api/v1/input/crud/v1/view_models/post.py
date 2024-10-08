from pydantic import BaseModel


class InputPostV1Input(BaseModel):
    input_hex: str
    setup_uuid: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "input_hex": "00001234deadbeef",
                    "setup_uuid": "394c2c91-f156-4fdc-a00a-69492b5c4e11",
                }
            ]
        }
    }


class InputPostV1Output(BaseModel):
    pass
