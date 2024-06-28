import asyncio
import hashlib
import json
import os
import pickle
import secrets
from typing import List

import httpx
from bitcoinutils.keys import PrivateKey, PublicKey
from fastapi import Body, FastAPI
from pydantic import BaseModel

from mutinyet_api.services.transaction_info_service import TransactionInfoService
from scripts.scripts_dict_generator_service import ScriptsDictGeneratorService
from transactions.enums import TransactionStepType
from transactions.generate_signatures_service import GenerateSignaturesService
from transactions.publication_services.publish_choice_search_transaction_service import (
    PublishChoiceSearchTransactionService,
)
from transactions.publication_services.trigger_protocol_transaction_service import (
    TriggerProtocolTransactionService,
)
from transactions.signatures.verify_prover_signatures_service import VerifyProverSignaturesService
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
        "verifier_private_key": private_key.to_bytes().hex(),
        "last_confirmed_step": None,
        "last_confirmed_step_tx_id": None,
        "setup_uuid": setup_uuid,
        "search_choices": [],
        "search_hashes": {},
    }
    os.makedirs(f"verifier_files/{setup_uuid}")
    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "xb") as f:
        pickle.dump(protocol_dict, f)
    return InitSetupResponse(
        public_key=private_key.get_public_key().to_hex(),
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
    choice_search_verifier_public_keys_list: List[List[List[str]]]
    verifier_public_key: str


@app.post("/public_keys")
async def public_keys(public_keys_body: PublicKeysBody) -> PublicKeysResponse:
    setup_uuid = public_keys_body.setup_uuid
    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
        protocol_dict = pickle.load(f)

    verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))

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
    protocol_dict["amount_of_nibbles_hash_with_checksum"] = len(
        public_keys_body.hash_result_public_keys
    )

    protocol_dict["amount_of_trace_steps"] = (
        2 ** protocol_dict["amount_of_bits_wrong_step_search"]
    ) ** protocol_dict["amount_of_wrong_step_search_iterations"]

    generate_verifier_public_keys_service = GenerateVerifierPublicKeysService(verifier_private_key)
    generate_verifier_public_keys_service(protocol_dict)

    protocol_dict["verifier_public_key"] = verifier_private_key.get_public_key().to_hex()

    protocol_dict["public_keys"] = [
        protocol_dict["verifier_public_key"],
        protocol_dict["prover_public_key"],
    ]

    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    return PublicKeysResponse(
        choice_search_verifier_public_keys_list=protocol_dict[
            "choice_search_verifier_public_keys_list"
        ],
        verifier_public_key=verifier_private_key.get_public_key().to_hex(),
    )


class SignaturesBody(BaseModel):
    setup_uuid: str
    trigger_protocol_signature: str
    search_choice_signatures: List[str]


class SignaturesResponse(BaseModel):
    verifier_hash_result_signature: str
    verifier_search_hash_signatures: List[str]
    verifier_trace_signature: str


@app.post("/signatures")
async def signatures(signatures_body: SignaturesBody) -> SignaturesResponse:
    setup_uuid = signatures_body.setup_uuid
    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
        protocol_dict = pickle.load(f)

    verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))

    # funding_amount_satoshis = protocol_dict["funding_amount_satoshis"]
    # step_fees_satoshis = protocol_dict["step_fees_satoshis"]
    protocol_dict["trigger_protocol_prover_signature"] = signatures_body.trigger_protocol_signature
    protocol_dict["search_choice_prover_signatures"] = signatures_body.search_choice_signatures

    # Transaction construction
    transaction_generator_from_public_keys_service = TransactionGeneratorFromPublicKeysService()
    transaction_generator_from_public_keys_service(protocol_dict)

    # Scripts construction
    scripts_dict_generator_service = ScriptsDictGeneratorService()
    scripts_dict = scripts_dict_generator_service(protocol_dict)

    destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])

    verify_prover_signatures_service = VerifyProverSignaturesService(destroyed_public_key)
    verify_prover_signatures_service(
        protocol_dict,
        scripts_dict,
        protocol_dict["prover_public_key"],
        protocol_dict["trigger_protocol_prover_signature"],
        protocol_dict["search_choice_prover_signatures"],
    )

    generate_signatures_service = GenerateSignaturesService(
        verifier_private_key, destroyed_public_key
    )
    signatures_dict = generate_signatures_service(protocol_dict, scripts_dict)

    hash_result_signature_verifier = signatures_dict["hash_result_signature"]
    protocol_dict["trigger_protocol_signatures"] = [
        signatures_dict["trigger_protocol_signature"],
        protocol_dict["trigger_protocol_prover_signature"],
    ]
    search_hash_signatures = signatures_dict["search_hash_signatures"]
    search_choice_signatures = []
    for i in range(len(signatures_dict["search_choice_signatures"])):
        search_choice_signatures.append(
            [
                signatures_dict["search_choice_signatures"][i],
                protocol_dict["search_choice_prover_signatures"][i],
            ]
        )
    protocol_dict["search_choice_signatures"] = search_choice_signatures
    trace_signature = signatures_dict["trace_signature"]

    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    return SignaturesResponse(
        verifier_hash_result_signature=hash_result_signature_verifier,
        verifier_search_hash_signatures=search_hash_signatures,
        verifier_trace_signature=trace_signature,
    )


class CreateSetupBody(BaseModel):
    amount_of_steps: int
    setup_uuid: str
    amount_of_bits_choice: int
    amount_of_bits_per_digit_checksum: int

    model_config = {"json_schema_extra": {"examples": [{"amount_of_steps": 16}]}}


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
    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
        protocol_dict = pickle.load(f)

    last_confirmed_step = protocol_dict["last_confirmed_step"]
    last_confirmed_step_tx_id = protocol_dict["last_confirmed_step_tx_id"]
    transaction_info_service = TransactionInfoService()

    if last_confirmed_step is None and (
        hash_result_transaction := transaction_info_service(
            protocol_dict["hash_result_tx"].get_txid()
        )
    ):
        trigger_protocol_transaction_service = TriggerProtocolTransactionService()
        last_confirmed_step_tx = trigger_protocol_transaction_service(
            protocol_dict, hash_result_transaction
        )
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.TRIGGER_PROTOCOL
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step is TransactionStepType.TRIGGER_PROTOCOL:
        ## VERIFY THE PREVIOUS STEP ##
        verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))
        i = 0
        publish_choice_search_transaction_service = PublishChoiceSearchTransactionService(
            verifier_private_key
        )
        last_confirmed_step_tx = publish_choice_search_transaction_service(protocol_dict, i)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.SEARCH_STEP_CHOICE
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step is TransactionStepType.SEARCH_STEP_CHOICE:
        ## VERIFY THE PREVIOUS STEP ##
        verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))
        i = 0
        for i in range(len(protocol_dict["search_choice_tx_list"])):
            if (
                protocol_dict["search_choice_tx_list"][i].get_txid()
                == protocol_dict["last_confirmed_step_tx_id"]
            ):
                break
        i += 1
        if i < len(protocol_dict["search_choice_tx_list"]):
            publish_choice_search_transaction_service = PublishChoiceSearchTransactionService(
                verifier_private_key
            )
            last_confirmed_step_tx = publish_choice_search_transaction_service(protocol_dict, i)
            last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            last_confirmed_step = TransactionStepType.SEARCH_STEP_CHOICE
            protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
            protocol_dict["last_confirmed_step"] = last_confirmed_step

    if last_confirmed_step in [
        TransactionStepType.TRIGGER_PROTOCOL,
        TransactionStepType.SEARCH_STEP_CHOICE,
    ]:
        asyncio.create_task(_trigger_next_step_prover(publish_next_step_body))

    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    return {"id": setup_uuid, "executed_step": last_confirmed_step}
