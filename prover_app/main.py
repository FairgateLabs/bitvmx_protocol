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
from bitcoinutils.constants import TAPROOT_SIGHASH_ALL
from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.setup import setup
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock
from fastapi import Body, FastAPI
from pydantic import BaseModel

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from mutinyet_api.services.faucet_service import FaucetService
from prover_app.config import protocol_properties
from scripts.scripts_dict_generator_service import ScriptsDictGeneratorService
from scripts.services.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from scripts.services.commit_search_hashes_script_generator_service import (
    CommitSearchHashesScriptGeneratorService,
)
from scripts.services.execution_trace_script_generator_service import (
    ExecutionTraceScriptGeneratorService,
)
from transactions.enums import TransactionStepType
from transactions.publication_services.publish_hash_transaction_service import (
    PublishHashTransactionService,
)
from transactions.publication_services.trigger_protocol_transaction_service import (
    TriggerProtocolTransactionService,
)
from transactions.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from winternitz_keys_handling.services.generate_winternitz_keys_nibbles_service import (
    GenerateWinternitzKeysNibblesService,
)
from winternitz_keys_handling.services.generate_winternitz_keys_single_word_service import (
    GenerateWinternitzKeysSingleWordService,
)
from winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from winternitz_keys_handling.services.generate_witness_from_input_single_word_service import (
    GenerateWitnessFromInputSingleWordService,
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

    # Do this by composing the exchanged keys // remove when ended debugging
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
    public_keys.append(prover_public_key.to_x_only_hex())

    destroyed_public_key = None
    destroyed_public_key_hex = ""
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
            public_keys[-1] = prover_public_key.to_x_only_hex()

    protocol_dict["seed_destroyed_public_key_hex"] = seed_destroyed_public_key_hex
    protocol_dict["destroyed_public_key"] = destroyed_public_key.to_hex()
    protocol_dict["prover_secret_key"] = prover_private_key.to_bytes().hex()
    protocol_dict["prover_public_key"] = prover_public_key

    prover_hash_private_key = PrivateKey(b=bytes.fromhex(prover_private_key.to_bytes().hex()))

    prover_winternitz_keys_nibbles_service = GenerateWinternitzKeysNibblesService(
        private_key=prover_hash_private_key
    )
    prover_winternitz_keys_single_word_service = GenerateWinternitzKeysSingleWordService(
        private_key=prover_hash_private_key
    )
    hash_result_keys = prover_winternitz_keys_nibbles_service(
        step=1, case=0, n0=amount_of_nibbles_hash
    )
    hash_result_public_keys = list(map(lambda key_list: key_list[-1], hash_result_keys))
    protocol_dict["hash_result_public_keys"] = hash_result_public_keys

    hash_search_public_keys_list = []
    choice_search_prover_public_keys_list = []
    for iter_count in range(amount_of_wrong_step_search_iterations):
        current_iteration_hash_keys = []

        for word_count in range(amount_of_wrong_step_search_hashes_per_iteration):
            current_iteration_hash_keys.append(
                prover_winternitz_keys_nibbles_service(
                    step=(3 + iter_count * 2), case=word_count, n0=amount_of_nibbles_hash
                )
            )
        current_iteration_hash_public_keys = []
        for keys_list_of_lists in current_iteration_hash_keys:
            current_iteration_hash_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )
        hash_search_public_keys_list.append(current_iteration_hash_public_keys)

        current_iteration_prover_choice_keys = []
        current_iteration_prover_choice_keys.append(
            prover_winternitz_keys_single_word_service(
                step=(3 + iter_count * 2 + 1),
                case=0,
                amount_of_bits=amount_of_bits_wrong_step_search,
            )
        )
        current_iteration_prover_choice_public_keys = []
        for keys_list_of_lists in current_iteration_prover_choice_keys:
            current_iteration_prover_choice_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )
        choice_search_prover_public_keys_list.append(current_iteration_prover_choice_public_keys)

    protocol_dict["hash_search_public_keys_list"] = hash_search_public_keys_list
    protocol_dict["choice_search_prover_public_keys_list"] = choice_search_prover_public_keys_list

    trace_words_lengths = [8, 8, 8] + [8, 8, 8] + [8, 2, 8] + [8, 8, 8, 2]
    trace_words_lengths.reverse()

    protocol_dict["trace_words_lengths"] = trace_words_lengths

    current_step = 3 + 2 * amount_of_wrong_step_search_iterations
    trace_prover_keys = []
    for i in range(len(trace_words_lengths)):
        trace_prover_keys.append(
            prover_winternitz_keys_nibbles_service(
                step=current_step, case=i, n0=trace_words_lengths[i]
            )
        )
    trace_prover_public_keys = []
    for keys_list_of_lists in trace_prover_keys:
        trace_prover_public_keys.append(
            list(map(lambda key_list: key_list[-1], keys_list_of_lists))
        )

    protocol_dict["trace_prover_public_keys"] = trace_prover_public_keys

    # Think how to iterate all verifiers here -> Maybe worth to make a call per verifier
    url = f"http://{verifier_list[0]}/public_keys"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {
        "setup_uuid": setup_uuid,
        "destroyed_public_key": destroyed_public_key_hex,
        "prover_public_key": prover_public_key.to_hex(),
        "hash_result_public_keys": hash_result_public_keys,
        "hash_search_public_keys_list": hash_search_public_keys_list,
        "trace_prover_public_keys": trace_prover_public_keys,
        "amount_of_wrong_step_search_iterations": amount_of_wrong_step_search_iterations,
        "amount_of_bits_wrong_step_search": amount_of_bits_wrong_step_search,
    }

    public_keys_response = requests.post(url, headers=headers, json=data)
    if public_keys_response.status_code != 200:
        raise Exception("Some error with the public keys verifier call")
    public_keys_response_json = public_keys_response.json()

    choice_search_verifier_public_keys_list = public_keys_response_json[
        "choice_search_verifier_public_keys_list"
    ]

    ###### TO BE ERASED ########
    verifier_private_key = PrivateKey(
        b=bytes.fromhex(public_keys_response_json["verifier_secret_key"])
    )
    protocol_dict["verifier_secret_key"] = verifier_private_key.to_bytes().hex()
    protocol_dict["choice_search_verifier_public_keys_list"] = (
        choice_search_verifier_public_keys_list
    )
    ##### END TO BE ERASED #####

    ## Scripts building ##

    scripts_dict_generator_service = ScriptsDictGeneratorService()
    scripts_dict = scripts_dict_generator_service(protocol_dict)

    hash_result_script = scripts_dict["hash_result_script"]

    initial_amount_satoshis = 100000
    step_fees_satoshis = 10000

    protocol_dict["initial_amount_satoshis"] = initial_amount_satoshis
    protocol_dict["step_fees_satoshis"] = step_fees_satoshis

    # We need to know the origin of the funds or change the signature to only sign the output (it's possible and gives more flexibility)

    faucet_service = FaucetService()

    faucet_tx_id, faucet_index = faucet_service(
        amount=initial_amount_satoshis + step_fees_satoshis,
        destination_address=prover_public_key.get_segwit_address().to_string(),
    )

    protocol_dict["faucet_tx_id"] = faucet_tx_id
    protocol_dict["faucet_index"] = faucet_index

    print("Faucet tx: " + faucet_tx_id)

    funding_result_output_amount = initial_amount_satoshis
    protocol_dict["funding_amount_satoshis"] = funding_result_output_amount

    # Transaction construction
    transaction_generator_from_public_keys_service = TransactionGeneratorFromPublicKeysService()
    transaction_generator_from_public_keys_service(protocol_dict)

    # Witness computation

    hash_result_tx = protocol_dict["hash_result_tx"]
    hash_result_script_address = destroyed_public_key.get_taproot_address(
        [[scripts_dict["hash_result_script"]]]
    )

    hash_result_witness = []

    generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
        prover_hash_private_key
    )

    input_number_first_alice = []
    first_revealed_hash = "1111111111111111111111111111111111111111111111111111111111111112"
    for letter in first_revealed_hash:
        input_number_first_alice.append(int(letter, 16))

    hash_result_witness += generate_witness_from_input_nibbles_service(
        step=1,
        case=0,
        input_numbers=input_number_first_alice,
        bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
    )

    hash_result_signature_prover = prover_private_key.sign_taproot_input(
        hash_result_tx,
        0,
        [hash_result_script_address.to_script_pub_key()],
        [funding_result_output_amount],
        script_path=True,
        tapleaf_script=hash_result_script,
        sighash=TAPROOT_SIGHASH_ALL,
        tweak=False,
    )

    protocol_dict["hash_result_signatures"] = [hash_result_signature_prover]

    ## Signature verification
    from bitcoinutils.schnorr import schnorr_verify

    tx_digest = hash_result_tx.get_transaction_taproot_digest(
        0,
        [hash_result_script_address.to_script_pub_key()],
        [funding_result_output_amount],
        1,
        script=hash_result_script,
        sighash=TAPROOT_SIGHASH_ALL,
    )

    assert schnorr_verify(
        tx_digest,
        bytes.fromhex(prover_public_key.to_x_only_hex()),
        bytes.fromhex(hash_result_signature_prover),
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

    # This should be a configuration
    amount_of_nibbles_hash = protocol_dict["amount_of_nibbles_hash"]

    prover_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["prover_secret_key"]))
    prover_public_key = prover_private_key.get_public_key()

    initial_amount_of_satoshis = protocol_dict["initial_amount_satoshis"]
    amount_of_bits_per_digit_checksum = protocol_dict["amount_of_bits_per_digit_checksum"]
    amount_of_wrong_step_search_iterations = protocol_dict["amount_of_wrong_step_search_iterations"]
    amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]
    amount_of_wrong_step_search_hashes_per_iteration = protocol_dict[
        "amount_of_wrong_step_search_hashes_per_iteration"
    ]
    last_confirmed_step = protocol_dict["last_confirmed_step"]
    last_confirmed_step_tx_id = protocol_dict["last_confirmed_step_tx_id"]

    hash_result_tx = protocol_dict["hash_result_tx"]

    hash_result_witness = []

    generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
        prover_private_key
    )

    destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])

    broadcast_transaction_service = BroadcastTransactionService()

    ## TO BE ERASED ##
    verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_secret_key"]))
    generate_verifier_witness_from_input_single_word_service = (
        GenerateWitnessFromInputSingleWordService(verifier_private_key)
    )
    ## END TO BE ERASED ##
    generate_prover_witness_from_input_single_word_service = (
        GenerateWitnessFromInputSingleWordService(prover_private_key)
    )

    if last_confirmed_step is None:
        publish_hash_transaction_service = PublishHashTransactionService(prover_private_key)
        last_confirmed_step_tx = publish_hash_transaction_service(protocol_dict)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.HASH_RESULT
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step == TransactionStepType.HASH_RESULT:
        trigger_protocol_transaction_service = TriggerProtocolTransactionService()
        last_confirmed_step_tx = trigger_protocol_transaction_service(protocol_dict)
        last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
        last_confirmed_step = TransactionStepType.TRIGGER_PROTOCOL
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step
    elif last_confirmed_step == TransactionStepType.TRIGGER_PROTOCOL:
        search_hash_tx_list = protocol_dict["search_hash_tx_list"]
        choice_hash_tx_list = protocol_dict["choice_hash_tx_list"]

        hash_search_public_keys_list = protocol_dict["hash_search_public_keys_list"]
        choice_search_prover_public_keys_list = protocol_dict[
            "choice_search_prover_public_keys_list"
        ]
        choice_search_verifier_public_keys_list = protocol_dict[
            "choice_search_verifier_public_keys_list"
        ]

        commit_search_hashes_script_generator_service = CommitSearchHashesScriptGeneratorService()
        commit_search_choice_script_generator_service = CommitSearchChoiceScriptGeneratorService()

        for i in range(amount_of_wrong_step_search_iterations):

            iteration_hashes = 3 * [
                "1111111111111111111111111111111111111111111111111111111111111112"
            ]
            hash_search_witness = []

            current_hash_public_keys = hash_search_public_keys_list[i]

            if i > 0:
                previous_choice_verifier_public_keys = choice_search_verifier_public_keys_list[
                    i - 1
                ]
                current_choice_prover_public_keys = choice_search_prover_public_keys_list[i - 1]
                current_hash_search_script = commit_search_hashes_script_generator_service(
                    current_hash_public_keys,
                    amount_of_nibbles_hash,
                    amount_of_bits_per_digit_checksum,
                    amount_of_bits_wrong_step_search,
                    current_choice_prover_public_keys[0],
                    previous_choice_verifier_public_keys[0],
                )

                current_choice = 2
                hash_search_witness += generate_verifier_witness_from_input_single_word_service(
                    step=(3 + (i - 1) * 2 + 1),
                    case=0,
                    input_number=current_choice,
                    amount_of_bits=amount_of_bits_wrong_step_search,
                )
                hash_search_witness += generate_prover_witness_from_input_single_word_service(
                    step=(3 + (i - 1) * 2 + 1),
                    case=0,
                    input_number=current_choice,
                    amount_of_bits=amount_of_bits_wrong_step_search,
                )

            else:
                current_hash_search_script = commit_search_hashes_script_generator_service(
                    current_hash_public_keys,
                    amount_of_nibbles_hash,
                    amount_of_bits_per_digit_checksum,
                )

            current_choice_public_keys = choice_search_verifier_public_keys_list[i]
            current_choice_search_script = commit_search_choice_script_generator_service(
                current_choice_public_keys[0],
                amount_of_bits_wrong_step_search,
            )

            for word_count in range(amount_of_wrong_step_search_hashes_per_iteration):

                input_number = []
                for letter in iteration_hashes[len(iteration_hashes) - word_count - 1]:
                    input_number.append(int(letter, 16))

                hash_search_witness += generate_witness_from_input_nibbles_service(
                    step=(3 + i * 2),
                    case=2 - word_count,
                    input_numbers=input_number,
                    bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
                )

            current_hash_search_scripts_address = destroyed_public_key.get_taproot_address(
                [[current_hash_search_script]]
            )
            current_hash_search_control_block = ControlBlock(
                destroyed_public_key,
                scripts=[[current_hash_search_script]],
                index=0,
                is_odd=current_hash_search_scripts_address.is_odd(),
            )

            search_hash_tx_list[i].witnesses.append(
                TxWitnessInput(
                    hash_search_witness
                    + [
                        # third_signature_bob,
                        # third_signature_alice,
                        current_hash_search_script.to_hex(),
                        current_hash_search_control_block.to_hex(),
                    ]
                )
            )

            broadcast_transaction_service(transaction=search_hash_tx_list[i].serialize())
            print(
                "Search hash iteration transaction "
                + str(i)
                + ": "
                + search_hash_tx_list[i].get_txid()
            )

            choice_search_witness = []
            current_choice = 2
            choice_search_witness += generate_verifier_witness_from_input_single_word_service(
                step=(3 + i * 2 + 1),
                case=0,
                input_number=current_choice,
                amount_of_bits=amount_of_bits_wrong_step_search,
            )
            current_choice_search_scripts_address = destroyed_public_key.get_taproot_address(
                [[current_choice_search_script]]
            )
            current_choice_search_control_block = ControlBlock(
                destroyed_public_key,
                scripts=[[current_hash_search_script]],
                index=0,
                is_odd=current_choice_search_scripts_address.is_odd(),
            )

            choice_hash_tx_list[i].witnesses.append(
                TxWitnessInput(
                    choice_search_witness
                    + [
                        # third_signature_bob,
                        # third_signature_alice,
                        current_choice_search_script.to_hex(),
                        current_choice_search_control_block.to_hex(),
                    ]
                )
            )

            broadcast_transaction_service(transaction=choice_hash_tx_list[i].serialize())
            print(
                "Choice hash iteration transaction "
                + str(i)
                + ": "
                + choice_hash_tx_list[i].get_txid()
            )

        trace_words_lengths = protocol_dict["trace_words_lengths"]

        trace_array = []
        for word_length in trace_words_lengths:
            trace_array.append("1" * word_length)

        trace_witness = []

        current_choice = 2
        trace_witness += generate_verifier_witness_from_input_single_word_service(
            step=(3 + (amount_of_wrong_step_search_iterations - 1) * 2 + 1),
            case=0,
            input_number=current_choice,
            amount_of_bits=amount_of_bits_wrong_step_search,
        )
        trace_witness += generate_prover_witness_from_input_single_word_service(
            step=(3 + (amount_of_wrong_step_search_iterations - 1) * 2 + 1),
            case=0,
            input_number=current_choice,
            amount_of_bits=amount_of_bits_wrong_step_search,
        )

        for word_count in range(len(trace_words_lengths)):

            input_number = []
            for letter in trace_array[len(trace_array) - word_count - 1]:
                input_number.append(int(letter, 16))

            trace_witness += generate_witness_from_input_nibbles_service(
                step=3 + amount_of_wrong_step_search_iterations * 2,
                case=len(trace_words_lengths) - word_count - 1,
                input_numbers=input_number,
                bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            )

        trace_tx = protocol_dict["trace_tx"]
        trace_prover_public_keys = protocol_dict["trace_prover_public_keys"]

        execution_trace_script_generator_service = ExecutionTraceScriptGeneratorService()
        trace_script = execution_trace_script_generator_service(
            trace_prover_public_keys,
            trace_words_lengths,
            amount_of_bits_per_digit_checksum,
            amount_of_bits_wrong_step_search,
            choice_search_prover_public_keys_list[-1][0],
            choice_search_verifier_public_keys_list[-1][0],
        )
        trace_script_address = destroyed_public_key.get_taproot_address([[trace_script]])

        trace_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[trace_script]],
            index=0,
            is_odd=trace_script_address.is_odd(),
        )

        trace_tx.witnesses.append(
            TxWitnessInput(
                trace_witness
                + [
                    # third_signature_bob,
                    # third_signature_alice,
                    trace_script.to_hex(),
                    trace_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(transaction=trace_tx.serialize())
        print("Trace transaction: " + trace_tx.get_txid())

        last_confirmed_step_tx_id = trace_tx.get_txid()
        last_confirmed_step = TransactionStepType.TRACE
        protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
        protocol_dict["last_confirmed_step"] = last_confirmed_step

    with open(f"prover_keys/{setup_uuid}.pkl", "wb") as f:
        pickle.dump(protocol_dict, f)

    if last_confirmed_step in [
        TransactionStepType.HASH_RESULT,
        TransactionStepType.TRIGGER_PROTOCOL,
    ]:
        asyncio.create_task(_trigger_next_step_verifier(publish_next_step_body))

    return {"id": setup_uuid, "executed_step": last_confirmed_step}
