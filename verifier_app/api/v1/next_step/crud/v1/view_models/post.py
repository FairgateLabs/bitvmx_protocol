from pydantic import BaseModel

from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType


class NextStepPostV1Input(BaseModel):
    setup_uuid: str

    model_config = {
        "json_schema_extra": {"examples": [{"setup_uuid": "289a04aa-5e35-4854-a71c-8131db874440"}]}
    }


class NextStepPostV1Output(BaseModel):
    setup_uuid: str
    executed_step: TransactionVerifierStepType
