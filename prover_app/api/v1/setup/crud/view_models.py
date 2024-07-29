from pydantic import BaseModel


class SetupPostV1Input(BaseModel):
    amount_of_steps: int

    model_config = {"json_schema_extra": {"examples": [{"amount_of_steps": 1000}]}}
