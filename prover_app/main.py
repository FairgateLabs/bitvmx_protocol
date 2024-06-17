import math
import secrets
import uuid
from typing import Optional
from bitcoinutils.setup import setup
import hashlib

from bitcoinutils.keys import PrivateKey, P2trAddress, P2wshAddress, P2pkhAddress, P2wpkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.utils import ControlBlock
from fastapi import Body, FastAPI
from pydantic import BaseModel

from mutinyet_api.services.broadcast_transaction_service import BroadcastTransactionService
from scripts.services.commit_search_hashes_script_generator_service import CommitSearchHashesScriptGeneratorService
from winternitz_keys_handling.services.generate_winternitz_keys_nibbles_service import (
    GenerateWinternitzKeysNibblesService,
)
from mutinyet_api.services.faucet_service import FaucetService
from prover_app.config import protocol_properties
from scripts.services.hash_result_script_generator_service import HashResultScriptGeneratorService
from winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import \
    GenerateWitnessFromInputNibblesService

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
    amount_of_steps = create_setup_body.amount_of_steps
    amount_of_bits_choice = protocol_properties.amount_bits_choice
    # For now, hardcoded to 16 and 2
    amount_of_steps = 16
    amount_of_bits_choice = 2
    amount_of_search_hashes_per_iteration = 2**amount_of_bits_choice - 1
    amount_of_nibbles_hash = 64
    amount_of_iterations = math.ceil(math.ceil(math.log2(amount_of_steps)) / amount_of_bits_choice)
    amount_of_bits_per_digit_checksum = 4

    # Do this by composing the exchanged keys
    destroyed_key = PrivateKey(b=secrets.token_bytes(32))
    destroyed_key = PrivateKey(b=bytes.fromhex("6eda6ac008a9b39f4aec5502f27c309a5ead41b7b45a8321a37e9901a3515bd3"))
    destroyed_public_key = destroyed_key.get_public_key()

    # Generate prover private key
    prover_private_key = PrivateKey(b=secrets.token_bytes(32))
    prover_private_key = PrivateKey(
        b=bytes.fromhex("5cb928bbdfcf6b37732ef1efb6dd7d44e2b2af8d24fdc0f534adee4d495afd84")
    )
    prover_public_key = prover_private_key.get_public_key()

    private_key_hash_step_hex = hashlib.sha256(
            bytes.fromhex(
                prover_private_key.to_bytes().hex() + hashlib.sha256(bytes.fromhex(format(1, "04x"))).hexdigest())
        ).hexdigest()

    prover_hash_private_key = PrivateKey(b=bytes.fromhex(private_key_hash_step_hex))

    prover_winternitz_keys_generator = GenerateWinternitzKeysNibblesService(
        private_key=prover_hash_private_key
    )
    hash_result_script_generator = HashResultScriptGeneratorService()

    with open(f"prover_keys/{setup_uuid}.txt", "x") as f:
        f.write(prover_private_key.to_bytes().hex())

    d0 = protocol_properties.d0

    hash_result_keys = prover_winternitz_keys_generator(
        step=1, case=0, n0=amount_of_nibbles_hash
    )
    hash_result_public_keys = list(map(lambda key_list: key_list[-1], hash_result_keys))

    search_public_keys = []
    for iter_count in range(amount_of_iterations):
        current_iteration_public_keys = []
        for word_count in range(amount_of_search_hashes_per_iteration):
            current_iteration_public_keys.append(
                prover_winternitz_keys_generator(
                    step=(3 + iter_count * 2), case=word_count, n0=amount_of_nibbles_hash
                )
            )
        search_public_keys.append(current_iteration_public_keys)

    hash_result_script = hash_result_script_generator(
        prover_public_key, hash_result_public_keys, amount_of_nibbles_hash, amount_of_bits_per_digit_checksum
    )

    commit_search_hashes_script_generator_service = CommitSearchHashesScriptGeneratorService()

    search_scripts = []
    for iter_count in range(amount_of_iterations):
        current_iteration_keys = search_public_keys[iter_count]
        current_public_keys = []
        for keys_list_of_lists in current_iteration_keys:
            current_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )
        search_scripts.append(
            commit_search_hashes_script_generator_service(
                current_public_keys, amount_of_nibbles_hash, amount_of_bits_per_digit_checksum
            )
        )

    third_output_address = destroyed_public_key.get_taproot_address([[search_scripts[0]]])

    initial_amount_satoshis = 100000
    step_fees_satoshis = 10000

    hash_result_script_address = destroyed_public_key.get_taproot_address([[hash_result_script]])

    faucet_service = FaucetService()

    hash_result_tx, hash_result_index = faucet_service(
        amount=initial_amount_satoshis, destination_address=hash_result_script_address.to_string()
    )

    print("Funding tx: " + hash_result_tx)

    # Transaction construction
    first_txin = TxInput(hash_result_tx, hash_result_index)
    faucet_address = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"
    first_output_amount = initial_amount_satoshis - step_fees_satoshis
    # first_txOut = TxOutput(first_output_amount, P2wpkhAddress.from_address(address=faucet_address).to_script_pub_key())
    first_txOut = TxOutput(first_output_amount, third_output_address.to_script_pub_key())

    first_tx = Transaction([first_txin], [first_txOut], has_segwit=True)
    first_control_block = ControlBlock(
        destroyed_public_key,
        scripts=[[hash_result_script]],
        index=0,
        is_odd=hash_result_script_address.is_odd(),
    )

    third_txin = TxInput(first_tx.get_txid(), 0)
    third_output_amount = first_output_amount - step_fees_satoshis
    third_txout = TxOutput(third_output_amount, P2wpkhAddress.from_address(address=faucet_address).to_script_pub_key())

    third_tx = Transaction([third_txin], [third_txout], has_segwit=True)
    third_control_block = ControlBlock(
        destroyed_public_key,
        scripts=[[search_scripts[0]]],
        index=0,
        is_odd=third_output_address.is_odd(),
    )

    # Witness computation

    first_message_witness = []

    generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
        prover_hash_private_key
    )

    input_number_first_alice = []
    first_revealed_hash = "1111111111111111111111111111111111111111111111111111111111111112"
    for letter in first_revealed_hash:
        input_number_first_alice.append(int(letter, 16))

    first_message_witness += generate_witness_from_input_nibbles_service(
        step=1,
        case=0,
        input_numbers=input_number_first_alice,
        bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
    )

    first_signature_alice = prover_private_key.sign_taproot_input(
        first_tx,
        0,
        [hash_result_script_address.to_script_pub_key()],
        [initial_amount_satoshis],
        script_path=True,
        tapleaf_script=hash_result_script,
        tapleaf_scripts=[hash_result_script],
        tweak=False,
    )

    first_tx.witnesses.append(
        TxWitnessInput(
            first_message_witness
            + [
                # first_signature_bob,
                first_signature_alice,
                hash_result_script.to_hex(),
                first_control_block.to_hex(),
            ]
        )
    )

    broadcast_transaction_service = BroadcastTransactionService()
    broadcast_transaction_service(transaction=first_tx.serialize())
    print("Hash result revelation transaction: " + first_tx.get_txid())


    third_message_witness = []
    third_hashes = 3 * ["1111111111111111111111111111111111111111111111111111111111111112"]
    third_message_witness = []

    for word_count in range(amount_of_search_hashes_per_iteration):

        input_number = []
        for letter in third_hashes[len(third_hashes) - word_count - 1]:
            input_number.append(int(letter, 16))

        third_message_witness += generate_witness_from_input_nibbles_service(
            step=3,
            case=2-word_count,
            input_numbers=input_number,
            bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

    third_tx.witnesses.append(
        TxWitnessInput(
            third_message_witness
            + [
                # third_signature_bob,
                # third_signature_alice,
                search_scripts[0].to_hex(),
                third_control_block.to_hex(),
            ]
        )
    )

    broadcast_transaction_service(transaction=third_tx.serialize())
    print("First search iteration transaction: " + third_tx.get_txid())

    return {"id": setup_uuid}
