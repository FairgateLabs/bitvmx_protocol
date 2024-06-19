import hashlib
import json
import math
import secrets
import uuid
from typing import Optional

import requests
from bitcoinutils.constants import TAPROOT_SIGHASH_ALL
from bitcoinutils.keys import P2wpkhAddress, PrivateKey, PublicKey
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.utils import ControlBlock
from fastapi import Body, FastAPI
from pydantic import BaseModel

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from mutinyet_api.services.faucet_service import FaucetService
from prover_app.config import protocol_properties
from scripts.bitcoin_script import BitcoinScript
from scripts.services.commit_search_choice_script_generator_service import (
    CommitSearchChoiceScriptGeneratorService,
)
from scripts.services.commit_search_hashes_script_generator_service import (
    CommitSearchHashesScriptGeneratorService,
)
from scripts.services.execution_trace_script_generator_service import (
    ExecutionTraceScriptGeneratorService,
)
from scripts.services.hash_result_script_generator_service import HashResultScriptGeneratorService
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
    amount_of_bits_choice = protocol_properties.amount_bits_choice
    amount_of_bits_per_digit_checksum = protocol_properties.amount_of_bits_per_digit_checksum
    verifier_list = protocol_properties.verifier_list
    # This is hardcoded since it depends on the hashing function
    amount_of_nibbles_hash = 64
    # Computed parameters
    amount_of_search_hashes_per_iteration = 2**amount_of_bits_choice - 1
    amount_of_iterations = math.ceil(math.ceil(math.log2(amount_of_steps)) / amount_of_bits_choice)

    # Do this by composing the exchanged keys // remove when ended debugging
    public_keys = []
    # destroyed_keys.append(secrets.token_hex(32))
    # destroyed_key = PrivateKey(b=secrets.token_bytes(32))
    # destroyed_key = PrivateKey(
    #     b=bytes.fromhex("6eda6ac008a9b39f4aec5502f27c309a5ead41b7b45a8321a37e9901a3515bd3")
    # )
    # destroyed_public_key = destroyed_key.get_public_key()

    for verifier in verifier_list:
        url = f"http://{verifier}/init_setup"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {"setup_uuid": setup_uuid}

        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        public_keys.append(response_json["public_key"])

    # Generate prover private key
    prover_private_key = PrivateKey(b=secrets.token_bytes(32))
    # prover_private_key = PrivateKey(
    #     b=bytes.fromhex("5cb928bbdfcf6b37732ef1efb6dd7d44e2b2af8d24fdc0f534adee4d495afd84")
    # )
    prover_public_key = prover_private_key.get_public_key()
    public_keys.append(prover_public_key.to_x_only_hex())

    destroyed_public_key = None
    while destroyed_public_key is None:
        try:
            public_destroyed_key_hex = hashlib.sha256(
                bytes.fromhex("".join(public_keys))
            ).hexdigest()
            destroyed_public_key = PublicKey(hex_str="02" + public_destroyed_key_hex)
            continue
        except IndexError:
            prover_private_key = PrivateKey(b=secrets.token_bytes(32))
            # prover_private_key = PrivateKey(
            #     b=bytes.fromhex("5cb928bbdfcf6b37732ef1efb6dd7d44e2b2af8d24fdc0f534adee4d495afd84")
            # )
            prover_public_key = prover_private_key.get_public_key()
            public_keys[-1] = prover_public_key.to_x_only_hex()

    keys_dict = {"secret_key": prover_private_key.to_bytes().hex()}
    with open(f"prover_keys/{setup_uuid}.json", "x") as f:
        f.write(json.dumps(keys_dict))

    prover_hash_private_key = PrivateKey(b=bytes.fromhex(prover_private_key.to_bytes().hex()))

    prover_winternitz_keys_nibbles_service = GenerateWinternitzKeysNibblesService(
        private_key=prover_hash_private_key
    )
    prover_winternitz_keys_single_word_service = GenerateWinternitzKeysSingleWordService(
        private_key=prover_hash_private_key
    )
    hash_result_script_generator = HashResultScriptGeneratorService()

    ###### TO BE ERASED ########
    verifier_private_key = PrivateKey(b=secrets.token_bytes(32))
    verifier_public_key = prover_private_key.get_public_key()
    verifier_winternitz_keys_single_word_service = GenerateWinternitzKeysSingleWordService(
        private_key=verifier_private_key
    )
    choice_search_verifier_public_keys = []
    for iter_count in range(amount_of_iterations):
        current_iteration_keys = []
        current_iteration_keys.append(
            verifier_winternitz_keys_single_word_service(
                step=(3 + iter_count * 2 + 1), case=0, amount_of_bits=amount_of_bits_choice
            )
        )
        current_iteration_public_keys = []
        for keys_list_of_lists in current_iteration_keys:
            current_iteration_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )

        choice_search_verifier_public_keys.append(current_iteration_public_keys)

    ##### END TO BE ERASED #####

    hash_result_keys = prover_winternitz_keys_nibbles_service(
        step=1, case=0, n0=amount_of_nibbles_hash
    )
    hash_result_public_keys = list(map(lambda key_list: key_list[-1], hash_result_keys))

    hash_search_public_keys = []
    choice_search_prover_public_keys = []
    for iter_count in range(amount_of_iterations):
        current_iteration_hash_keys = []

        for word_count in range(amount_of_search_hashes_per_iteration):
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
        hash_search_public_keys.append(current_iteration_hash_public_keys)

        current_iteration_prover_choice_keys = []
        current_iteration_prover_choice_keys.append(
            prover_winternitz_keys_single_word_service(
                step=(3 + iter_count * 2 + 1), case=0, amount_of_bits=amount_of_bits_choice
            )
        )
        current_iteration_prover_choice_public_keys = []
        for keys_list_of_lists in current_iteration_prover_choice_keys:
            current_iteration_prover_choice_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )
        choice_search_prover_public_keys.append(current_iteration_prover_choice_public_keys)

    trace_words_lengths = [8, 8, 8] + [8, 8, 8] + [8, 2, 8] + [8, 8, 8, 2]
    trace_words_lengths.reverse()
    current_step = 3 + 2 * amount_of_iterations
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

    ## Scripts building ##

    hash_result_script = hash_result_script_generator(
        prover_public_key,
        hash_result_public_keys,
        amount_of_nibbles_hash,
        amount_of_bits_per_digit_checksum,
    )

    trigger_protocol_script = BitcoinScript()
    # trigger_protocol_script.extend(
    #     [prover_public_key.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
    # )
    # trigger_protocol_script.extend(
    #     [verifier_public_key.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
    # )
    trigger_protocol_script.append(1)

    commit_search_hashes_script_generator_service = CommitSearchHashesScriptGeneratorService()
    commit_search_choice_script_generator_service = CommitSearchChoiceScriptGeneratorService()

    hash_search_scripts = []
    choice_search_scripts = []
    for iter_count in range(amount_of_iterations):
        # Hash
        current_hash_public_keys = hash_search_public_keys[iter_count]
        if iter_count > 0:
            previous_choice_verifier_public_keys = choice_search_verifier_public_keys[
                iter_count - 1
            ]
            current_choice_prover_public_keys = choice_search_prover_public_keys[iter_count - 1]
            current_search_script = commit_search_hashes_script_generator_service(
                current_hash_public_keys,
                amount_of_nibbles_hash,
                amount_of_bits_per_digit_checksum,
                amount_of_bits_choice,
                current_choice_prover_public_keys[0],
                previous_choice_verifier_public_keys[0],
            )
        else:
            current_search_script = commit_search_hashes_script_generator_service(
                current_hash_public_keys, amount_of_nibbles_hash, amount_of_bits_per_digit_checksum
            )

        hash_search_scripts.append(current_search_script)

        # Choice
        current_choice_public_keys = choice_search_verifier_public_keys[iter_count]
        current_choice_script = commit_search_choice_script_generator_service(
            current_choice_public_keys[0],
            amount_of_bits_choice,
        )
        choice_search_scripts.append(current_choice_script)

    hash_search_scripts_addresses = list(
        map(
            lambda search_script: destroyed_public_key.get_taproot_address([[search_script]]),
            hash_search_scripts,
        )
    )

    choice_search_scripts_addresses = list(
        map(
            lambda choice_script: destroyed_public_key.get_taproot_address([[choice_script]]),
            choice_search_scripts,
        )
    )

    execution_trace_script_generator_service = ExecutionTraceScriptGeneratorService()

    trace_script = execution_trace_script_generator_service(
        trace_prover_public_keys, trace_words_lengths, amount_of_bits_per_digit_checksum
    )
    trace_script_address = destroyed_public_key.get_taproot_address([[trace_script]])

    initial_amount_satoshis = 100000
    step_fees_satoshis = 10000

    faucet_service = FaucetService()

    faucet_tx, faucet_index = faucet_service(
        amount=initial_amount_satoshis,
        destination_address=prover_public_key.get_segwit_address().to_string(),
    )

    print("Faucet tx: " + faucet_tx)

    # Transaction construction
    transaction_dict = {}

    funding_txin = TxInput(faucet_tx, faucet_index)
    hash_result_script_address = destroyed_public_key.get_taproot_address([[hash_result_script]])
    funding_result_output_amount = initial_amount_satoshis - step_fees_satoshis
    funding_txout = TxOutput(
        funding_result_output_amount, hash_result_script_address.to_script_pub_key()
    )
    funding_tx = Transaction([funding_txin], [funding_txout], has_segwit=True)

    transaction_dict["funding_transaction_id"] = [funding_tx.get_txid(), 0]

    trigger_protocol_script_address = destroyed_public_key.get_taproot_address(
        [[trigger_protocol_script]]
    )

    hash_result_txin = TxInput(funding_tx.get_txid(), 0)
    hash_result_output_amount = funding_result_output_amount - step_fees_satoshis
    # first_txOut = TxOutput(first_output_amount, P2wpkhAddress.from_address(address=faucet_address).to_script_pub_key())
    hash_result_txOut = TxOutput(
        hash_result_output_amount, trigger_protocol_script_address.to_script_pub_key()
    )

    hash_result_tx = Transaction([hash_result_txin], [hash_result_txOut], has_segwit=True)

    transaction_dict["hash_result"] = hash_result_tx

    hash_result_control_block = ControlBlock(
        destroyed_public_key,
        scripts=[[hash_result_script]],
        index=0,
        is_odd=hash_result_script_address.is_odd(),
    )

    trigger_protocol_output_amount = hash_result_output_amount - step_fees_satoshis
    trigger_protocol_txin = TxInput(hash_result_tx.get_txid(), 0)
    trigger_protocol_txOut = TxOutput(
        trigger_protocol_output_amount, hash_search_scripts_addresses[0].to_script_pub_key()
    )

    trigger_protocol_tx = Transaction(
        [trigger_protocol_txin], [trigger_protocol_txOut], has_segwit=True
    )

    transaction_dict["trigger_protocol"] = hash_result_tx

    trigger_protocol_control_block = ControlBlock(
        destroyed_public_key,
        scripts=[[trigger_protocol_script]],
        index=0,
        is_odd=trigger_protocol_script_address.is_odd(),
    )

    previous_tx_id = trigger_protocol_tx.get_txid()
    current_output_amount = trigger_protocol_output_amount
    search_hash_tx = []
    choice_hash_tx = []
    hash_search_control_blocks = []
    choice_search_control_blocks = []

    for i in range(amount_of_iterations):

        # HASH
        current_txin = TxInput(previous_tx_id, 0)
        current_output_amount -= step_fees_satoshis
        current_output_address = choice_search_scripts_addresses[i]
        current_txout = TxOutput(current_output_amount, current_output_address.to_script_pub_key())

        current_tx = Transaction([current_txin], [current_txout], has_segwit=True)

        search_hash_tx.append(current_tx)
        current_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[hash_search_scripts[i]]],
            index=0,
            is_odd=hash_search_scripts_addresses[i].is_odd(),
        )
        hash_search_control_blocks.append(current_control_block)

        # CHOICE
        current_txin = TxInput(current_tx.get_txid(), 0)
        current_output_amount -= step_fees_satoshis
        if i == amount_of_iterations - 1:
            faucet_address = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"
            current_output_address = P2wpkhAddress.from_address(address=faucet_address)
        else:
            current_output_address = hash_search_scripts_addresses[i + 1]
        current_txout = TxOutput(current_output_amount, current_output_address.to_script_pub_key())

        current_tx = Transaction([current_txin], [current_txout], has_segwit=True)

        choice_hash_tx.append(current_tx)
        current_control_block = ControlBlock(
            destroyed_public_key,
            scripts=[[choice_search_scripts[i]]],
            index=0,
            is_odd=choice_search_scripts_addresses[i].is_odd(),
        )
        choice_search_control_blocks.append(current_control_block)

        previous_tx_id = current_tx.get_txid()

    transaction_dict["search_hash"] = search_hash_tx
    transaction_dict["choice_hash"] = choice_hash_tx

    # Witness computation

    hash_result_witness = []

    generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
        prover_hash_private_key
    )
    generate_verifier_witness_from_input_single_word_service = (
        GenerateWitnessFromInputSingleWordService(verifier_private_key)
    )
    generate_prover_witness_from_input_single_word_service = (
        GenerateWitnessFromInputSingleWordService(prover_hash_private_key)
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

    #################################################################

    funding_sig = prover_private_key.sign_segwit_input(
        funding_tx, 0, prover_public_key.get_address().to_script_pub_key(), initial_amount_satoshis
    )

    funding_tx.witnesses.append(TxWitnessInput([funding_sig, prover_public_key.to_hex()]))

    broadcast_transaction_service = BroadcastTransactionService()
    broadcast_transaction_service(transaction=funding_tx.serialize())
    print("Funding transaction: " + funding_tx.get_txid())

    hash_result_tx.witnesses.append(
        TxWitnessInput(
            hash_result_witness
            + [
                # first_signature_bob,
                hash_result_signature_prover,
                hash_result_script.to_hex(),
                hash_result_control_block.to_hex(),
            ]
        )
    )

    broadcast_transaction_service(transaction=hash_result_tx.serialize())
    print("Hash result revelation transaction: " + hash_result_tx.get_txid())

    trigger_protocol_witness = []
    trigger_protocol_tx.witnesses.append(
        TxWitnessInput(
            trigger_protocol_witness
            + [
                # first_signature_bob,
                # hash_result_signature_prover,
                trigger_protocol_script.to_hex(),
                trigger_protocol_control_block.to_hex(),
            ]
        )
    )

    broadcast_transaction_service(transaction=trigger_protocol_tx.serialize())
    print("Trigger protocol transaction: " + trigger_protocol_tx.get_txid())

    for i in range(amount_of_iterations):

        iteration_hashes = 3 * ["1111111111111111111111111111111111111111111111111111111111111112"]
        hash_search_witness = []

        if i > 0:
            current_choice = 2
            hash_search_witness += generate_verifier_witness_from_input_single_word_service(
                step=(3 + (i - 1) * 2 + 1),
                case=0,
                input_number=current_choice,
                amount_of_bits=amount_of_bits_choice,
            )
            hash_search_witness += generate_prover_witness_from_input_single_word_service(
                step=(3 + (i - 1) * 2 + 1),
                case=0,
                input_number=current_choice,
                amount_of_bits=amount_of_bits_choice,
            )

        for word_count in range(amount_of_search_hashes_per_iteration):

            input_number = []
            for letter in iteration_hashes[len(iteration_hashes) - word_count - 1]:
                input_number.append(int(letter, 16))

            hash_search_witness += generate_witness_from_input_nibbles_service(
                step=(3 + i * 2),
                case=2 - word_count,
                input_numbers=input_number,
                bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            )

        search_hash_tx[i].witnesses.append(
            TxWitnessInput(
                hash_search_witness
                + [
                    # third_signature_bob,
                    # third_signature_alice,
                    hash_search_scripts[i].to_hex(),
                    hash_search_control_blocks[i].to_hex(),
                ]
            )
        )

        broadcast_transaction_service(transaction=search_hash_tx[i].serialize())
        print("Search hash iteration transaction " + str(i) + ": " + search_hash_tx[i].get_txid())

        choice_search_witness = []
        current_choice = 2
        choice_search_witness += generate_verifier_witness_from_input_single_word_service(
            step=(3 + i * 2 + 1),
            case=0,
            input_number=current_choice,
            amount_of_bits=amount_of_bits_choice,
        )
        choice_hash_tx[i].witnesses.append(
            TxWitnessInput(
                choice_search_witness
                + [
                    # third_signature_bob,
                    # third_signature_alice,
                    choice_search_scripts[i].to_hex(),
                    choice_search_control_blocks[i].to_hex(),
                ]
            )
        )

        broadcast_transaction_service(transaction=choice_hash_tx[i].serialize())
        print("Choice hash iteration transaction " + str(i) + ": " + choice_hash_tx[i].get_txid())

    return {"id": setup_uuid}


@app.post("/publish_hash")
async def publish_hash(create_setup_body: CreateSetupBody = Body()) -> dict[str, str]:
    pass
