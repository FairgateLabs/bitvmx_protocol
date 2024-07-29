import asyncio
import json
import pickle
from typing import Optional

import httpx
from bitcoinutils.keys import PrivateKey
from fastapi import Body, FastAPI
from pydantic import BaseModel

from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.transaction_generation.enums import TransactionProverStepType
from bitvmx_protocol_library.transaction_generation.publication_services.prover.execution_challenge_transaction_service import (
    ExecutionChallengeTransactionService,
)
from bitvmx_protocol_library.transaction_generation.publication_services.prover.publish_hash_search_transaction_service import (
    PublishHashSearchTransactionService,
)
from bitvmx_protocol_library.transaction_generation.publication_services.prover.publish_hash_transaction_service import (
    PublishHashTransactionService,
)
from bitvmx_protocol_library.transaction_generation.publication_services.prover.publish_trace_transaction_service import (
    PublishTraceTransactionService,
)
from blockchain_query_services.common.transaction_published_service import (
    TransactionPublishedService,
)
from blockchain_query_services.services.mutinynet_api.faucet_service import FaucetService
from prover_app.api.v1.router import router as prover_router
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
    assert common_protocol_properties.network == BitcoinNetwork.MUTINYNET
    faucet_service = FaucetService()
    income_tx, index = faucet_service(
        amount=fund_input.amount, destination_address=fund_input.destination_address
    )
    return FundAddressOutput(tx_id=income_tx, index=index)


class PublishNextStepBody(BaseModel):
    setup_uuid: str

    model_config = {
        "json_schema_extra": {"examples": [{"setup_uuid": "289a04aa-5e35-4854-a71c-8131db874440"}]}
    }


async def _trigger_next_step_prover(publish_hash_body: PublishNextStepBody):
    prover_host = protocol_properties.prover_host
    url = f"{prover_host}/publish_next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Make the POST request
    async with httpx.AsyncClient(timeout=1200.0) as client:
        await client.post(url, headers=headers, json=json.loads(publish_hash_body.json()))


async def _trigger_next_step_verifier(publish_hash_body: PublishNextStepBody):
    verifier_host = protocol_properties.verifier_list[0]
    url = f"{verifier_host}/publish_next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Make the POST request
    async with httpx.AsyncClient(timeout=1200.0) as client:
        await client.post(url, headers=headers, json=json.loads(publish_hash_body.json()))


@app.post("/publish_next_step")
async def publish_next_step(publish_next_step_body: PublishNextStepBody = Body()) -> dict[str, str]:
    setup_uuid = publish_next_step_body.setup_uuid
    with open(f"prover_files/{setup_uuid}/file_database.pkl", "rb") as f:
        protocol_dict = pickle.load(f)

    prover_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["prover_secret_key"]))
    last_confirmed_step = protocol_dict["last_confirmed_step"]

    transaction_published_service = TransactionPublishedService()

    if last_confirmed_step is None:
        publish_hash_transaction_service = PublishHashTransactionService(prover_private_key)
        last_confirmed_step_tx = publish_hash_transaction_service(protocol_dict)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionProverStepType.HASH_RESULT
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif (
        last_confirmed_step == TransactionProverStepType.HASH_RESULT
        and transaction_published_service(protocol_dict["trigger_protocol_tx"].get_txid())
    ):
        publish_hash_search_transaction_service = PublishHashSearchTransactionService(
            prover_private_key
        )
        last_confirmed_step_tx = publish_hash_search_transaction_service(protocol_dict, 0)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionProverStepType.SEARCH_STEP_HASH
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step == TransactionProverStepType.SEARCH_STEP_HASH:
        if (
            protocol_dict["search_hash_tx_list"][-1].get_txid()
            == protocol_dict["last_confirmed_step_tx_id"]
        ) and transaction_published_service(protocol_dict["search_choice_tx_list"][-1].get_txid()):
            publish_trace_transaction_service = PublishTraceTransactionService(prover_private_key)
            last_confirmed_step_tx = publish_trace_transaction_service(protocol_dict)
            last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            last_confirmed_step = TransactionProverStepType.TRACE
            protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
            protocol_dict["last_confirmed_step"] = last_confirmed_step
        else:
            i = None
            for i in range(len(protocol_dict["search_hash_tx_list"])):
                if (
                    protocol_dict["search_hash_tx_list"][i].get_txid()
                    == protocol_dict["last_confirmed_step_tx_id"]
                ):
                    break
            i += 1
            if i < len(protocol_dict["search_choice_tx_list"]) and transaction_published_service(
                protocol_dict["search_choice_tx_list"][i - 1].get_txid()
            ):
                publish_hash_search_transaction_service = PublishHashSearchTransactionService(
                    prover_private_key
                )
                last_confirmed_step_tx = publish_hash_search_transaction_service(protocol_dict, i)
                last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
                last_confirmed_step = TransactionProverStepType.SEARCH_STEP_HASH
                protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
                protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step == TransactionProverStepType.TRACE:
        # Here we should check which is the challenge that should be triggered
        if transaction_published_service(
            protocol_dict["trigger_execution_challenge_tx"].get_txid()
        ):
            execution_challenge_transaction_service = ExecutionChallengeTransactionService()
            last_confirmed_step_tx = execution_challenge_transaction_service(protocol_dict)
            last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            last_confirmed_step = TransactionProverStepType.EXECUTION_CHALLENGE
            protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
            protocol_dict["last_confirmed_step"] = last_confirmed_step

    with open(f"prover_files/{setup_uuid}/file_database.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    if last_confirmed_step in [
        TransactionProverStepType.HASH_RESULT,
        TransactionProverStepType.SEARCH_STEP_HASH,
        TransactionProverStepType.TRACE,
    ]:
        asyncio.create_task(_trigger_next_step_verifier(publish_next_step_body))

    return {"id": setup_uuid, "executed_step": last_confirmed_step}


app.include_router(prover_router, prefix="/api", tags=["Prover API"])
