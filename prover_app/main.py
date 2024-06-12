from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from mutinyet_api.services.faucet_service import FaucetService

app = FastAPI(
    title="Prover service",
    description="Microservice to perform all the operations related to the prover",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


class FundAddressInput(BaseModel):
    amount: int
    destination_address: Optional[str] = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"amount": 1000000, "address": "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"}
            ]
        }
    }


@app.post("/post_final_hash")
async def fund_address(fund_input: FundAddressInput) -> dict[str, str]:
    faucet_service = FaucetService()
    income_tx, index = faucet_service(
        amount=fund_input.amount, destination_address=fund_input.destination_address
    )
    return {"tx_id": income_tx, "index": index}
