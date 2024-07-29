import hashlib
import math
import os
import pickle
import secrets
import uuid

import requests
from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.setup import setup
from bitcoinutils.transactions import TxWitnessInput

from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.script_generation.services.scripts_dict_generator_service import (
    ScriptsDictGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.generate_signatures_service import (
    GenerateSignaturesService,
)
from bitvmx_protocol_library.transaction_generation.signatures.verify_verifier_signatures_service import (
    VerifyVerifierSignaturesService,
)
from bitvmx_protocol_library.transaction_generation.transaction_generator_from_public_keys_service import (
    TransactionGeneratorFromPublicKeysService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)
from blockchain_query_services.services.mutinynet_api.faucet_service import FaucetService
from prover_app.api.v1.setup.crud.view_models import CreateSetupBody
from prover_app.config import protocol_properties
from winternitz_keys_handling.services.generate_prover_public_keys_service import (
    GenerateProverPublicKeysService,
)


async def setup_post_view(create_setup_body: CreateSetupBody):
    if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
        setup("testnet")
    else:
        setup(common_protocol_properties.network.value)

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
    protocol_dict["setup_uuid"] = setup_uuid
    protocol_dict["amount_of_trace_steps"] = (
        2**amount_of_bits_wrong_step_search
    ) ** amount_of_wrong_step_search_iterations
    protocol_dict["amount_of_bits_per_digit_checksum"] = amount_of_bits_per_digit_checksum
    protocol_dict["amount_of_wrong_step_search_iterations"] = amount_of_wrong_step_search_iterations
    protocol_dict["amount_of_bits_wrong_step_search"] = amount_of_bits_wrong_step_search
    protocol_dict["amount_of_wrong_step_search_hashes_per_iteration"] = (
        amount_of_wrong_step_search_hashes_per_iteration
    )
    protocol_dict["amount_of_nibbles_hash"] = amount_of_nibbles_hash
    protocol_dict["search_choices"] = []
    protocol_dict["published_hashes_dict"] = {}

    public_keys = []
    for verifier in verifier_list:
        url = f"{verifier}/init_setup"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {"setup_uuid": setup_uuid, "network": common_protocol_properties.network.value}

        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        public_keys.append(response_json["public_key"])

    # Generate prover private key
    if protocol_properties.prover_private_key is None:
        controlled_prover_private_key = PrivateKey(b=secrets.token_bytes(32))
    else:
        controlled_prover_private_key = PrivateKey(
            b=bytes.fromhex(protocol_properties.prover_private_key)
        )

    controlled_prover_public_key = controlled_prover_private_key.get_public_key()
    controlled_prover_address = controlled_prover_public_key.get_segwit_address().to_string()
    # public_keys.append(prover_public_key.to_hex())

    protocol_dict["controlled_prover_secret_key"] = controlled_prover_private_key.to_bytes().hex()
    protocol_dict["controlled_prover_public_key"] = controlled_prover_public_key.to_hex()
    protocol_dict["controlled_prover_address"] = controlled_prover_address

    destroyed_public_key = None
    seed_destroyed_public_key_hex = ""
    prover_private_key = PrivateKey(b=secrets.token_bytes(32))
    prover_public_key = prover_private_key.get_public_key()
    public_keys.append(prover_public_key.to_hex())
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
    protocol_dict["network"] = common_protocol_properties.network

    # prover_private_key = PrivateKey(b=bytes.fromhex(prover_private_key.to_bytes().hex()))

    generate_prover_public_keys_service = GenerateProverPublicKeysService(prover_private_key)
    generate_prover_public_keys_service(protocol_dict)

    initial_amount_satoshis = common_protocol_properties.initial_amount_satoshis
    step_fees_satoshis = common_protocol_properties.step_fees_satoshis

    if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
        faucet_service = FaucetService()
        funding_tx_id, funding_index = faucet_service(
            amount=initial_amount_satoshis + step_fees_satoshis,
            destination_address=controlled_prover_public_key.get_segwit_address().to_string(),
        )
    else:
        funding_tx_id = protocol_properties.funding_tx_id
        funding_index = protocol_properties.funding_index

    protocol_dict["funds_tx_id"] = funding_tx_id
    protocol_dict["funds_index"] = funding_index

    print("Funding tx: " + funding_tx_id)

    # Think how to iterate all verifiers here -> Maybe worth to make a call per verifier
    url = f"{verifier_list[0]}/public_keys"
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
        "funds_tx_id": funding_tx_id,
        "funds_index": funding_index,
        "amount_of_nibbles_hash": amount_of_nibbles_hash,
        "controlled_prover_address": controlled_prover_address,
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
    trace_verifier_public_keys = public_keys_response_json["trace_verifier_public_keys"]
    protocol_dict["trace_verifier_public_keys"] = trace_verifier_public_keys

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

    # Think how to iterate all verifiers here -> Maybe worth to make a call per verifier
    hash_result_signatures = [signatures_dict["hash_result_signature"]]
    search_hash_signatures = [
        [signature] for signature in signatures_dict["search_hash_signatures"]
    ]
    trace_signatures = [signatures_dict["trace_signature"]]
    # execution_challenge_signatures = [signatures_dict["execution_challenge_signature"]]
    for verifier in verifier_list:
        url = f"{verifier}/signatures"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {
            "setup_uuid": setup_uuid,
            "trigger_protocol_signature": signatures_dict["trigger_protocol_signature"],
            "search_choice_signatures": signatures_dict["search_choice_signatures"],
            "trigger_execution_signature": signatures_dict["trigger_execution_signature"],
        }
        signatures_response = requests.post(url, headers=headers, json=data)
        if signatures_response.status_code != 200:
            raise Exception("Some error when exchanging the signatures")

        signatures_response_json = signatures_response.json()
        for j in range(len(signatures_response_json["verifier_search_hash_signatures"])):
            search_hash_signatures[j].append(
                signatures_response_json["verifier_search_hash_signatures"][j]
            )

        hash_result_signatures.append(signatures_response_json["verifier_hash_result_signature"])
        trace_signatures.append(signatures_response_json["verifier_trace_signature"])
        # execution_challenge_signatures.append(
        #     signatures_response_json["verifier_execution_challenge_signature"]
        # )

    hash_result_signatures.reverse()
    for signature_list in search_hash_signatures:
        signature_list.reverse()
    trace_signatures.reverse()
    # execution_challenge_signatures.reverse()

    protocol_dict["hash_result_signatures"] = hash_result_signatures
    protocol_dict["search_hash_signatures"] = search_hash_signatures
    protocol_dict["trace_signatures"] = trace_signatures
    # protocol_dict["execution_challenge_signatures"] = execution_challenge_signatures

    verify_verifier_signatures_service = VerifyVerifierSignaturesService(destroyed_public_key)
    for i in range(len(protocol_dict["public_keys"]) - 1):
        verify_verifier_signatures_service(
            protocol_dict=protocol_dict,
            scripts_dict=scripts_dict,
            public_key=protocol_dict["public_keys"][i],
            hash_result_signature=protocol_dict["hash_result_signatures"][
                len(protocol_dict["public_keys"]) - i - 2
            ],
            search_hash_signatures=[
                signatures_list[len(protocol_dict["public_keys"]) - i - 2]
                for signatures_list in protocol_dict["search_hash_signatures"]
            ],
            trace_signature=protocol_dict["trace_signatures"][
                len(protocol_dict["public_keys"]) - i - 2
            ],
            # execution_challenge_signature=protocol_dict["execution_challenge_signatures"][
            #     len(protocol_dict["public_keys"]) - i - 2
            # ],
        )

    os.makedirs(f"prover_files/{setup_uuid}")

    with open(f"prover_files/{setup_uuid}/file_database.pkl", "xb") as f:
        pickle.dump(protocol_dict, f)

    #################################################################
    funding_tx = protocol_dict["funding_tx"]

    funding_sig = controlled_prover_private_key.sign_segwit_input(
        funding_tx,
        0,
        controlled_prover_public_key.get_address().to_script_pub_key(),
        initial_amount_satoshis + step_fees_satoshis,
    )

    funding_tx.witnesses.append(
        TxWitnessInput([funding_sig, controlled_prover_public_key.to_hex()])
    )

    broadcast_transaction_service(transaction=funding_tx.serialize())
    print("Funding transaction: " + funding_tx.get_txid())

    return {"setup_uuid": setup_uuid}
