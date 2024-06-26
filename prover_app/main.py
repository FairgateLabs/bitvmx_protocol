import asyncio
import hashlib
import json
import math
import pickle
import secrets
import uuid
from typing import Optional

import httpx
import requests
from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.setup import setup
from bitcoinutils.transactions import TxWitnessInput
from fastapi import Body, FastAPI
from pydantic import BaseModel

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from mutinyet_api.services.faucet_service import FaucetService
from mutinyet_api.services.transaction_published_service import TransactionPublishedService
from prover_app.config import protocol_properties
from scripts.scripts_dict_generator_service import ScriptsDictGeneratorService
from transactions.enums import TransactionStepType
from transactions.generate_signatures_service import GenerateSignaturesService
from transactions.publication_services.publish_hash_search_transaction_service import (
    PublishHashSearchTransactionService,
)
from transactions.publication_services.publish_hash_transaction_service import (
    PublishHashTransactionService,
)
from transactions.publication_services.publish_trace_transaction_service import (
    PublishTraceTransactionService,
)
from transactions.signatures.verify_verifier_signatures_service import (
    VerifyVerifierSignaturesService,
)
from transactions.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from winternitz_keys_handling.services.generate_prover_public_keys_service import (
    GenerateProverPublicKeysService,
)

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
    setup("testnet")

    setup_uuid = str(uuid.uuid4())
    # Variable parameters
    amount_of_steps = create_setup_body.amount_of_steps
    # Constant parameters
    amount_of_bits_wrong_step_search = protocol_properties.amount_bits_choice
    amount_of_bits_per_digit_checksum = protocol_properties.amount_of_bits_per_digit_checksum
    verifier_list = protocol_properties.verifier_list
    # This is hardcoded since it depends on the hashing function
    amount_of_nibbles_hash = 64
    # Computed parameters
    amount_of_wrong_step_search_hashes_per_iteration = 2**amount_of_bits_wrong_step_search - 1
    amount_of_wrong_step_search_iterations = math.ceil(
        math.ceil(math.log2(amount_of_steps)) / amount_of_bits_wrong_step_search
    )

    protocol_dict = {}
    protocol_dict["amount_of_bits_per_digit_checksum"] = amount_of_bits_per_digit_checksum
    protocol_dict["amount_of_wrong_step_search_iterations"] = amount_of_wrong_step_search_iterations
    protocol_dict["amount_of_bits_wrong_step_search"] = amount_of_bits_wrong_step_search
    protocol_dict["amount_of_wrong_step_search_hashes_per_iteration"] = (
        amount_of_wrong_step_search_hashes_per_iteration
    )
    protocol_dict["amount_of_nibbles_hash"] = amount_of_nibbles_hash

    public_keys = []
    for verifier in verifier_list:
        url = f"http://{verifier}/init_setup"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {"setup_uuid": setup_uuid}

        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        public_keys.append(response_json["public_key"])

    # Generate prover private key
    prover_private_key = PrivateKey(b=secrets.token_bytes(32))

    prover_public_key = prover_private_key.get_public_key()
    public_keys.append(prover_public_key.to_hex())

    destroyed_public_key = None
    seed_destroyed_public_key_hex = ""
    while destroyed_public_key is None:
        try:
            seed_destroyed_public_key_hex = "".join(public_keys)
            destroyed_public_key_hex = hashlib.sha256(
                bytes.fromhex(seed_destroyed_public_key_hex)
            ).hexdigest()
            destroyed_public_key = PublicKey(hex_str="02" + destroyed_public_key_hex)
            continue
        except IndexError:
            prover_private_key = PrivateKey(b=secrets.token_bytes(32))
            prover_public_key = prover_private_key.get_public_key()
            public_keys[-1] = prover_public_key.to_hex()

    protocol_dict["seed_destroyed_public_key_hex"] = seed_destroyed_public_key_hex
    protocol_dict["destroyed_public_key"] = destroyed_public_key.to_hex()
    protocol_dict["prover_secret_key"] = prover_private_key.to_bytes().hex()
    protocol_dict["prover_public_key"] = prover_public_key.to_hex()
    protocol_dict["public_keys"] = public_keys

    prover_private_key = PrivateKey(b=bytes.fromhex(prover_private_key.to_bytes().hex()))

    generate_prover_public_keys_service = GenerateProverPublicKeysService(prover_private_key)
    generate_prover_public_keys_service(protocol_dict)

    initial_amount_satoshis = 100000
    step_fees_satoshis = 10000

    faucet_service = FaucetService()
    faucet_tx_id, faucet_index = faucet_service(
        amount=initial_amount_satoshis + step_fees_satoshis,
        destination_address=prover_public_key.get_segwit_address().to_string(),
    )

    protocol_dict["funds_tx_id"] = faucet_tx_id
    protocol_dict["funds_index"] = faucet_index

    print("Faucet tx: " + faucet_tx_id)

    # Think how to iterate all verifiers here -> Maybe worth to make a call per verifier
    url = f"http://{verifier_list[0]}/public_keys"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {
        "setup_uuid": setup_uuid,
        "seed_destroyed_public_key_hex": seed_destroyed_public_key_hex,
        "prover_public_key": prover_public_key.to_hex(),
        "hash_result_public_keys": protocol_dict["hash_result_public_keys"],
        "hash_search_public_keys_list": protocol_dict["hash_search_public_keys_list"],
        "choice_search_prover_public_keys_list": protocol_dict[
            "choice_search_prover_public_keys_list"
        ],
        "trace_words_lengths": protocol_dict["trace_words_lengths"],
        "trace_prover_public_keys": protocol_dict["trace_prover_public_keys"],
        "amount_of_wrong_step_search_iterations": amount_of_wrong_step_search_iterations,
        "amount_of_bits_wrong_step_search": amount_of_bits_wrong_step_search,
        "amount_of_bits_per_digit_checksum": amount_of_bits_per_digit_checksum,
        "funding_amount_satoshis": initial_amount_satoshis,
        "step_fees_satoshis": step_fees_satoshis,
        "funds_tx_id": faucet_tx_id,
        "funds_index": faucet_index,
        "amount_of_nibbles_hash": amount_of_nibbles_hash,
    }

    public_keys_response = requests.post(url, headers=headers, json=data)
    if public_keys_response.status_code != 200:
        raise Exception("Some error with the public keys verifier call")
    public_keys_response_json = public_keys_response.json()

    choice_search_verifier_public_keys_list = public_keys_response_json[
        "choice_search_verifier_public_keys_list"
    ]
    protocol_dict["choice_search_verifier_public_keys_list"] = (
        choice_search_verifier_public_keys_list
    )
    verifier_public_key = public_keys_response_json["verifier_public_key"]
    protocol_dict["verifier_public_key"] = verifier_public_key

    ## Scripts building ##

    scripts_dict_generator_service = ScriptsDictGeneratorService()
    scripts_dict = scripts_dict_generator_service(protocol_dict)

    protocol_dict["initial_amount_satoshis"] = initial_amount_satoshis
    protocol_dict["step_fees_satoshis"] = step_fees_satoshis

    # We need to know the origin of the funds or change the signature to only sign the output (it's possible and gives more flexibility)

    funding_result_output_amount = initial_amount_satoshis
    protocol_dict["funding_amount_satoshis"] = funding_result_output_amount

    # Transaction construction
    transaction_generator_from_public_keys_service = TransactionGeneratorFromPublicKeysService()
    transaction_generator_from_public_keys_service(protocol_dict)

    # Signature computation

    generate_signatures_service = GenerateSignaturesService(
        prover_private_key, destroyed_public_key
    )
    signatures_dict = generate_signatures_service(protocol_dict, scripts_dict)

    #
    # hash_result_signature_prover = prover_private_key.sign_taproot_input(
    #     hash_result_tx,
    #     0,
    #     [hash_result_script_address.to_script_pub_key()],
    #     [funding_result_output_amount],
    #     script_path=True,
    #     tapleaf_script=hash_result_script,
    #     sighash=TAPROOT_SIGHASH_ALL,
    #     tweak=False,
    # )

    # Think how to iterate all verifiers here -> Maybe worth to make a call per verifier
    hash_result_signatures = [signatures_dict["hash_result_signature"]]
    for verifier in verifier_list:
        url = f"http://{verifier}/signatures"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {
            "setup_uuid": setup_uuid,
            "trigger_protocol_signature": signatures_dict["trigger_protocol_signature"],
            # "trigger_signature": trigger_signature_prover,
            # "hash_search_signatures": hash_result_signatures_prover,
            # "choice_search_signatures": choice_search_signatures_prover,
            # "trace_signature": trace_signature_prover,
        }
        signatures_response = requests.post(url, headers=headers, json=data)
        if signatures_response.status_code != 200:
            raise Exception("Some error when exchanging the signatures")

        signatures_response_json = signatures_response.json()

        hash_result_signatures.append(signatures_response_json["verifier_hash_result_signature"])

    hash_result_signatures.reverse()
    protocol_dict["hash_result_signatures"] = hash_result_signatures

    verify_verifier_signatures_service = VerifyVerifierSignaturesService(destroyed_public_key)
    for i in range(len(protocol_dict["public_keys"]) - 1):
        verify_verifier_signatures_service(
            protocol_dict=protocol_dict,
            scripts_dict=scripts_dict,
            public_key=protocol_dict["public_keys"][i],
            hash_result_signature=protocol_dict["hash_result_signatures"][
                len(protocol_dict["public_keys"]) - i - 2
            ],
        )

    with open(f"prover_keys/{setup_uuid}.pkl", "xb") as f:
        pickle.dump(protocol_dict, f)

    #################################################################
    funding_tx = protocol_dict["funding_tx"]

    funding_sig = prover_private_key.sign_segwit_input(
        funding_tx,
        0,
        prover_public_key.get_address().to_script_pub_key(),
        initial_amount_satoshis + step_fees_satoshis,
    )

    funding_tx.witnesses.append(TxWitnessInput([funding_sig, prover_public_key.to_hex()]))

    broadcast_transaction_service = BroadcastTransactionService()
    broadcast_transaction_service(transaction=funding_tx.serialize())
    print("Funding transaction: " + funding_tx.get_txid())

    return {"id": setup_uuid}


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


async def _trigger_next_step_verifier(publish_hash_body: PublishNextStepBody):
    verifier_host = protocol_properties.verifier_list[0]
    url = f"http://{verifier_host}/publish_next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Make the POST request
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=json.loads(publish_hash_body.json()))


@app.post("/publish_next_step")
async def publish_next_step(publish_next_step_body: PublishNextStepBody = Body()) -> dict[str, str]:
    setup_uuid = publish_next_step_body.setup_uuid
    with open(f"prover_keys/{setup_uuid}.pkl", "rb") as f:
        protocol_dict = pickle.load(f)

    prover_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["prover_secret_key"]))
    last_confirmed_step = protocol_dict["last_confirmed_step"]

    transaction_published_service = TransactionPublishedService()

    if last_confirmed_step is None:
        publish_hash_transaction_service = PublishHashTransactionService(prover_private_key)
        last_confirmed_step_tx = publish_hash_transaction_service(protocol_dict)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.HASH_RESULT
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step == TransactionStepType.HASH_RESULT and transaction_published_service(
        protocol_dict["trigger_protocol_tx"].get_txid()
    ):
        publish_hash_search_transaction_service = PublishHashSearchTransactionService(
            prover_private_key
        )
        last_confirmed_step_tx = publish_hash_search_transaction_service(protocol_dict, 0)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.SEARCH_STEP_HASH
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step == TransactionStepType.SEARCH_STEP_HASH:
        if (
            protocol_dict["search_hash_tx_list"][-1].get_txid()
            == protocol_dict["last_confirmed_step_tx_id"]
        ) and transaction_published_service(protocol_dict["search_choice_tx_list"][-1].get_txid()):
            publish_trace_transaction_service = PublishTraceTransactionService(prover_private_key)
            last_confirmed_step_tx = publish_trace_transaction_service(protocol_dict)
            last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            last_confirmed_step = TransactionStepType.TRACE
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
                last_confirmed_step = TransactionStepType.SEARCH_STEP_HASH
                protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
                protocol_dict["last_confirmed_step"] = last_confirmed_step

    with open(f"prover_keys/{setup_uuid}.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    if last_confirmed_step in [
        TransactionStepType.HASH_RESULT,
        TransactionStepType.SEARCH_STEP_HASH,
        TransactionStepType.SEARCH_STEP_CHOICE,
    ]:
        asyncio.create_task(_trigger_next_step_verifier(publish_next_step_body))

    return {"id": setup_uuid, "executed_step": last_confirmed_step}
