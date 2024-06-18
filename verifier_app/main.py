import json
import math
import secrets

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import setup
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Verifier service",
    description="Microservice to perform all the operations related to the verifier",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


class InitSetupBody(BaseModel):
    setup_uuid: str


class InitSetupResponse(BaseModel):
    public_key: str


@app.post("/init_setup")
async def init_setup(body: InitSetupBody) -> InitSetupResponse:
    private_key = PrivateKey(b=secrets.token_bytes(32))
    setup_uuid = body.setup_uuid
    keys_dict = {
        "secret_key": private_key.to_bytes().hex(),
    }
    with open(f"verifier_keys/{setup_uuid}.json", "x") as f:
        f.write(json.dumps(keys_dict))
    return InitSetupResponse(
        public_key=private_key.get_public_key().to_x_only_hex(),
    )


class CreateSetupBody(BaseModel):
    amount_of_steps: int
    setup_uuid: str
    amount_of_bits_choice: int
    amount_of_bits_per_digit_checksum: int

    model_config = {"json_schema_extra": {"examples": [{"amount_of_steps": 16}]}}


@app.post("/create_setup")
async def create_setup(create_setup_body: CreateSetupBody) -> dict[str, str]:
    setup("testnet")
    amount_of_steps = create_setup_body.amount_of_steps
    amount_of_bits_choice = create_setup_body.amount_bits_choice
    setup_uuid = create_setup_body.setup_uuid
    amount_of_bits_per_digit_checksum = create_setup_body.amount_of_bits_per_digit_checksum

    amount_of_nibbles_hash = 64
    amount_of_search_hashes_per_iteration = 2**amount_of_bits_choice - 1
    amount_of_iterations = math.ceil(math.ceil(math.log2(amount_of_steps)) / amount_of_bits_choice)

    return {"id": setup_uuid}
