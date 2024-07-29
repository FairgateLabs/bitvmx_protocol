from typing import Optional

from pydantic import BaseModel


class FundPostV1Input(BaseModel):
    amount: int
    # Mutinynet faucet address
    destination_address: Optional[str] = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"amount": 1000000, "address": "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"}
            ]
        }
    }


class FundPostV1Output(BaseModel):
    tx_id: str
    index: Optional[int] = None
