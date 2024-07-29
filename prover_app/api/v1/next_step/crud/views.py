import asyncio
import json
import pickle

import httpx
from bitcoinutils.keys import PrivateKey
from fastapi import Body

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
from prover_app.api.v1.next_step.crud.view_models import NextStepPostV1Input
from prover_app.config import protocol_properties


async def _trigger_next_step_verifier(publish_hash_body: NextStepPostV1Input):
    verifier_host = protocol_properties.verifier_list[0]
    url = f"{verifier_host}/publish_next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Make the POST request
    async with httpx.AsyncClient(timeout=1200.0) as client:
        await client.post(url, headers=headers, json=json.loads(publish_hash_body.json()))


async def next_step_post_view(
    next_step_post_view_input: NextStepPostV1Input = Body(),
) -> dict[str, str]:
    setup_uuid = next_step_post_view_input.setup_uuid
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
        asyncio.create_task(_trigger_next_step_verifier(next_step_post_view_input))

    return {"setup_uuid": setup_uuid, "executed_step": last_confirmed_step}
