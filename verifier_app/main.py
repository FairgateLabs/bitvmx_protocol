import json
import math
import secrets
import pickle

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import setup
from fastapi import FastAPI
from pydantic import BaseModel
from verifier_app.config import protocol_properties
import httpx

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

    protocol_dict = {}
    protocol_dict["last_confirmed_step"] = None
    protocol_dict["last_confirmed_step_tx_id"] = None

    with open(f"prover_keys/{setup_uuid}.pkl", "xb") as f:
        pickle.dump(protocol_dict, f)

    return {"id": setup_uuid}


# This should be put in a common directory
class PublishNextStepBody(BaseModel):
    setup_uuid: str

    model_config = {
        "json_schema_extra": {"examples": [{"setup_uuid": "289a04aa-5e35-4854-a71c-8131db874440"}]}
    }

async def _trigger_next_step_prover(publish_hash_body: PublishNextStepBody):
    prover_host = protocol_properties.prover_host
    url = f"http://{prover_host}/publish_next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Make the POST request
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=json.loads(publish_hash_body.json()))
