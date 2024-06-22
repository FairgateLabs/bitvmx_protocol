import asyncio
import json
import pickle
import secrets
from typing import List

import httpx
from bitcoinutils.keys import PrivateKey
from fastapi import Body, FastAPI
from pydantic import BaseModel

from transactions.enums import TransactionStepType
from transactions.publication_services.trigger_protocol_transaction_service import (
    TriggerProtocolTransactionService,
)
from verifier_app.config import protocol_properties
from winternitz_keys_handling.services.generate_winternitz_keys_single_word_service import (
    GenerateWinternitzKeysSingleWordService,
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
    destroyed_public_key: str
    prover_public_key: str
    hash_result_public_keys: List[str]
    hash_search_public_keys_list: List[List[List[str]]]
    trace_prover_public_keys: List[List[str]]
    amount_of_wrong_step_search_iterations: int
    amount_of_bits_wrong_step_search: int


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

    protocol_dict["destroyed_public_key"] = public_keys_body.destroyed_public_key
    protocol_dict["prover_public_key"] = public_keys_body.prover_public_key
    protocol_dict["hash_result_public_keys"] = public_keys_body.hash_result_public_keys
    protocol_dict["hash_search_public_keys_list"] = public_keys_body.hash_search_public_keys_list
    protocol_dict["trace_prover_public_keys"] = public_keys_body.trace_prover_public_keys
    protocol_dict["amount_of_wrong_step_search_iterations"] = (
        public_keys_body.amount_of_wrong_step_search_iterations
    )
    protocol_dict["amount_of_bits_wrong_step_search"] = (
        public_keys_body.amount_of_bits_wrong_step_search
    )

    amount_of_wrong_step_search_iterations = public_keys_body.amount_of_wrong_step_search_iterations
    amount_of_bits_wrong_step_search = public_keys_body.amount_of_bits_wrong_step_search

    verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["secret_key"]))

    verifier_winternitz_keys_single_word_service = GenerateWinternitzKeysSingleWordService(
        private_key=verifier_private_key
    )
    choice_search_verifier_public_keys_list = []
    for iter_count in range(amount_of_wrong_step_search_iterations):
        current_iteration_keys = []
        current_iteration_keys.append(
            verifier_winternitz_keys_single_word_service(
                step=(3 + iter_count * 2 + 1),
                case=0,
                amount_of_bits=amount_of_bits_wrong_step_search,
            )
        )
        current_iteration_public_keys = []
        for keys_list_of_lists in current_iteration_keys:
            current_iteration_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )

        choice_search_verifier_public_keys_list.append(current_iteration_public_keys)

    protocol_dict["choice_search_verifier_public_keys_list"] = (
        choice_search_verifier_public_keys_list
    )

    with open(f"verifier_keys/{setup_uuid}.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    return PublicKeysResponse(
        verifier_secret_key=verifier_private_key.to_bytes().hex(),
        choice_search_verifier_public_keys_list=choice_search_verifier_public_keys_list,
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
        trigger_protocol_transaction_service = TriggerProtocolTransactionService()
        # last_confirmed_step_tx = trigger_protocol_transaction_service(protocol_dict)
        # last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.TRIGGER_PROTOCOL
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step

    if last_confirmed_step in [TransactionStepType.TRIGGER_PROTOCOL]:
        asyncio.create_task(_trigger_next_step_prover(publish_next_step_body))

    return {"id": setup_uuid, "executed_step": last_confirmed_step}
