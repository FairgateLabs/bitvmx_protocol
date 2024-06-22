import asyncio
import hashlib
import json
import pickle
import secrets
from typing import List

import httpx
from bitcoinutils.keys import PrivateKey, PublicKey
from fastapi import Body, FastAPI
from pydantic import BaseModel

from transactions.enums import TransactionStepType
from transactions.publication_services.trigger_protocol_transaction_service import (
    TriggerProtocolTransactionService,
)
from transactions.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from verifier_app.config import protocol_properties
from winternitz_keys_handling.services.generate_verifier_public_keys_service import (
    GenerateVerifierPublicKeysService,
)

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
    protocol_dict = {
        "secret_key": private_key.to_bytes().hex(),
        "last_confirmed_step": None,
        "last_confirmed_step_tx_id": None,
    }
    with open(f"verifier_keys/{setup_uuid}.pkl", "xb") as f:
        pickle.dump(protocol_dict, f)
    return InitSetupResponse(
        public_key=private_key.get_public_key().to_x_only_hex(),
    )


class PublicKeysBody(BaseModel):
    setup_uuid: str
    seed_destroyed_public_key_hex: str
    prover_public_key: str
    hash_result_public_keys: List[str]
    hash_search_public_keys_list: List[List[List[str]]]
    choice_search_prover_public_keys_list: List[List[List[str]]]
    trace_words_lengths: List[int]
    trace_prover_public_keys: List[List[str]]
    amount_of_wrong_step_search_iterations: int
    amount_of_bits_wrong_step_search: int
    amount_of_bits_per_digit_checksum: int
    funding_amount_satoshis: int
    step_fees_satoshis: int
    funds_tx_id: str
    funds_index: int
    amount_of_nibbles_hash: int


class PublicKeysResponse(BaseModel):
    ## TO BE ERASED ##
    verifier_secret_key: str
    ## END TO BE ERASED ##
    choice_search_verifier_public_keys_list: List[List[List[str]]]


@app.post("/public_keys")
async def public_keys(public_keys_body: PublicKeysBody) -> PublicKeysResponse:
    setup_uuid = public_keys_body.setup_uuid
    with open(f"verifier_keys/{setup_uuid}.pkl", "rb") as f:
        protocol_dict = pickle.load(f)

    verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["secret_key"]))

    if (
        verifier_private_key.get_public_key().to_x_only_hex()
        not in public_keys_body.seed_destroyed_public_key_hex
    ):
        raise Exception("Seed does not contain public key")

    destroyed_public_key_hex = hashlib.sha256(
        bytes.fromhex(public_keys_body.seed_destroyed_public_key_hex)
    ).hexdigest()
    destroyed_public_key = PublicKey(hex_str="02" + destroyed_public_key_hex)
    protocol_dict["seed_destroyed_public_key_hex"] = public_keys_body.seed_destroyed_public_key_hex
    protocol_dict["destroyed_public_key"] = destroyed_public_key.to_hex()
    protocol_dict["prover_public_key"] = public_keys_body.prover_public_key
    protocol_dict["hash_result_public_keys"] = public_keys_body.hash_result_public_keys
    protocol_dict["hash_search_public_keys_list"] = public_keys_body.hash_search_public_keys_list
    protocol_dict["choice_search_prover_public_keys_list"] = (
        public_keys_body.choice_search_prover_public_keys_list
    )
    protocol_dict["trace_words_lengths"] = public_keys_body.trace_words_lengths
    protocol_dict["trace_prover_public_keys"] = public_keys_body.trace_prover_public_keys
    protocol_dict["amount_of_wrong_step_search_iterations"] = (
        public_keys_body.amount_of_wrong_step_search_iterations
    )
    protocol_dict["amount_of_bits_wrong_step_search"] = (
        public_keys_body.amount_of_bits_wrong_step_search
    )
    protocol_dict["amount_of_bits_per_digit_checksum"] = (
        public_keys_body.amount_of_bits_per_digit_checksum
    )
    protocol_dict["funding_amount_satoshis"] = public_keys_body.funding_amount_satoshis
    protocol_dict["step_fees_satoshis"] = public_keys_body.step_fees_satoshis
    protocol_dict["funds_tx_id"] = public_keys_body.funds_tx_id
    protocol_dict["funds_index"] = public_keys_body.funds_index
    protocol_dict["amount_of_nibbles_hash"] = public_keys_body.amount_of_nibbles_hash

    generate_verifier_public_keys_service = GenerateVerifierPublicKeysService(verifier_private_key)
    generate_verifier_public_keys_service(protocol_dict)

    # Transaction construction
    transaction_generator_from_public_keys_service = TransactionGeneratorFromPublicKeysService()
    transaction_generator_from_public_keys_service(protocol_dict)

    with open(f"verifier_keys/{setup_uuid}.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    return PublicKeysResponse(
        verifier_secret_key=verifier_private_key.to_bytes().hex(),
        choice_search_verifier_public_keys_list=protocol_dict[
            "choice_search_verifier_public_keys_list"
        ],
    )


class CreateSetupBody(BaseModel):
    amount_of_steps: int
    setup_uuid: str
    amount_of_bits_choice: int
    amount_of_bits_per_digit_checksum: int

    model_config = {"json_schema_extra": {"examples": [{"amount_of_steps": 16}]}}


# @app.post("/create_setup")
# async def create_setup(create_setup_body: CreateSetupBody) -> dict[str, str]:
#     setup("testnet")
#     amount_of_steps = create_setup_body.amount_of_steps
#     amount_of_bits_choice = create_setup_body.amount_bits_choice
#     setup_uuid = create_setup_body.setup_uuid
#     amount_of_bits_per_digit_checksum = create_setup_body.amount_of_bits_per_digit_checksum
#
#     amount_of_nibbles_hash = 64
#     amount_of_search_hashes_per_iteration = 2**amount_of_bits_choice - 1
#     amount_of_iterations = math.ceil(math.ceil(math.log2(amount_of_steps)) / amount_of_bits_choice)
#
#     protocol_dict = {}
#     protocol_dict["last_confirmed_step"] = None
#     protocol_dict["last_confirmed_step_tx_id"] = None
#
#     with open(f"verifier_keys/{setup_uuid}.pkl", "xb") as f:
#         pickle.dump(protocol_dict, f)
#
#     return {"id": setup_uuid}


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


@app.post("/publish_next_step")
async def publish_next_step(publish_next_step_body: PublishNextStepBody = Body()) -> dict[str, str]:
    setup_uuid = publish_next_step_body.setup_uuid
    with open(f"verifier_keys/{setup_uuid}.pkl", "rb") as f:
        protocol_dict = pickle.load(f)

    last_confirmed_step = protocol_dict["last_confirmed_step"]
    last_confirmed_step_tx_id = protocol_dict["last_confirmed_step_tx_id"]

    if last_confirmed_step is None:
        # VERIFY THAT THE FIRST HASH HAS BEEN PUBLISHED #
        trigger_protocol_transaction_service = TriggerProtocolTransactionService()
        last_confirmed_step_tx = trigger_protocol_transaction_service(protocol_dict)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.TRIGGER_PROTOCOL
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step

    if last_confirmed_step in [TransactionStepType.TRIGGER_PROTOCOL]:
        asyncio.create_task(_trigger_next_step_prover(publish_next_step_body))

    with open(f"verifier_keys/{setup_uuid}.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    return {"id": setup_uuid, "executed_step": last_confirmed_step}
