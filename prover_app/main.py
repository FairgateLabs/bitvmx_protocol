import math
import secrets
import uuid
from typing import Optional

from bitcoinutils.keys import PrivateKey
from fastapi import Body, FastAPI
from pydantic import BaseModel

from keys_handling.services.generate_winternitz_keys_nibbles_service import (
    GenerateWinternitzKeysNibblesService,
)
from mutinyet_api.services.faucet_service import FaucetService
from prover_app.config import protocol_properties

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


class FundAddressOutput(BaseModel):
    tx_id: str
    index: Optional[int] = None


@app.post("/fund_address")
async def fund_address(fund_input: FundAddressInput) -> FundAddressOutput:
    faucet_service = FaucetService()
    income_tx, index = faucet_service(
        amount=fund_input.amount, destination_address=fund_input.destination_address
    )
    return FundAddressOutput(tx_id=income_tx, index=index)


class CreateSetupBody(BaseModel):
    amount_of_steps: int

    model_config = {"json_schema_extra": {"examples": [{"amount_of_steps": 16}]}}


@app.post("/create_setup")
async def create_setup(create_setup_body: CreateSetupBody = Body()) -> dict[str, str]:
    setup_uuid = str(uuid.uuid4())
    amount_of_steps = create_setup_body.amount_of_steps
    amount_of_bits_choice = protocol_properties.amount_bits_choice
    # For now, hardcoded to 16 and 2
    amount_of_steps = 16
    amount_of_bits_choice = 2
    amount_of_iterations = math.ceil(math.ceil(math.log2(amount_of_steps)) / amount_of_bits_choice)

    # Do this by composing the exchanged keys
    destroyed_key = PrivateKey(b=secrets.token_bytes(32))
    destroyed_public_key = destroyed_key.get_public_key()

    # Generate prover private key
    prover_private_key = PrivateKey(b=secrets.token_bytes(32))
    prover_public_key = prover_private_key.get_public_key()

    prover_winternitz_public_keys_generator = GenerateWinternitzKeysNibblesService(
        private_key=prover_private_key
    )

    step = 1

    with open(f"prover_keys/{setup_uuid}.txt", "x") as f:
        f.write(prover_private_key.to_bytes().hex())

    d0 = protocol_properties.d0

    hash_result_keys = prover_winternitz_public_keys_generator(step=step, n0=64)
    hash_result_public_keys = list(
        map(
            lambda key_list: key_list[-1], hash_result_keys
        )
    )

    return {"id": setup_uuid}
