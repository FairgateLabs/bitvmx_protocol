import hashlib
import pickle

from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.setup import setup

from bitvmx_protocol_library.enums import BitcoinNetwork
from verifier_app.api.v1.public_keys.crud.view_models import (
    PublicKeysPostV1Input,
    PublicKeysPostV1Output,
)
from winternitz_keys_handling.services.generate_verifier_public_keys_service import (
    GenerateVerifierPublicKeysService,
)


async def public_keys_post_view(
    public_keys_post_view_input: PublicKeysPostV1Input,
) -> PublicKeysPostV1Output:
    setup_uuid = public_keys_post_view_input.setup_uuid
    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
        protocol_dict = pickle.load(f)
    if protocol_dict["network"] == BitcoinNetwork.MUTINYNET:
        setup("testnet")
    else:
        setup(protocol_dict["network"].value)
    verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))

    if (
        verifier_private_key.get_public_key().to_x_only_hex()
        not in public_keys_post_view_input.seed_destroyed_public_key_hex
    ):
        raise Exception("Seed does not contain public key")

    destroyed_public_key_hex = hashlib.sha256(
        bytes.fromhex(public_keys_post_view_input.seed_destroyed_public_key_hex)
    ).hexdigest()
    destroyed_public_key = PublicKey(hex_str="02" + destroyed_public_key_hex)
    protocol_dict["seed_destroyed_public_key_hex"] = (
        public_keys_post_view_input.seed_destroyed_public_key_hex
    )
    protocol_dict["destroyed_public_key"] = destroyed_public_key.to_hex()
    protocol_dict["prover_public_key"] = public_keys_post_view_input.prover_public_key
    protocol_dict["hash_result_public_keys"] = public_keys_post_view_input.hash_result_public_keys
    protocol_dict["hash_search_public_keys_list"] = (
        public_keys_post_view_input.hash_search_public_keys_list
    )
    protocol_dict["choice_search_prover_public_keys_list"] = (
        public_keys_post_view_input.choice_search_prover_public_keys_list
    )
    protocol_dict["trace_words_lengths"] = public_keys_post_view_input.trace_words_lengths
    protocol_dict["trace_prover_public_keys"] = public_keys_post_view_input.trace_prover_public_keys
    protocol_dict["amount_of_wrong_step_search_iterations"] = (
        public_keys_post_view_input.amount_of_wrong_step_search_iterations
    )
    protocol_dict["amount_of_bits_wrong_step_search"] = (
        public_keys_post_view_input.amount_of_bits_wrong_step_search
    )
    protocol_dict["amount_of_bits_per_digit_checksum"] = (
        public_keys_post_view_input.amount_of_bits_per_digit_checksum
    )
    protocol_dict["funding_amount_satoshis"] = public_keys_post_view_input.funding_amount_satoshis
    protocol_dict["step_fees_satoshis"] = public_keys_post_view_input.step_fees_satoshis
    protocol_dict["funds_tx_id"] = public_keys_post_view_input.funds_tx_id
    protocol_dict["funds_index"] = public_keys_post_view_input.funds_index
    protocol_dict["amount_of_nibbles_hash"] = public_keys_post_view_input.amount_of_nibbles_hash
    protocol_dict["amount_of_nibbles_hash_with_checksum"] = len(
        public_keys_post_view_input.hash_result_public_keys
    )
    protocol_dict["controlled_prover_address"] = (
        public_keys_post_view_input.controlled_prover_address
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

    return PublicKeysPostV1Output(
        choice_search_verifier_public_keys_list=protocol_dict[
            "choice_search_verifier_public_keys_list"
        ],
        trace_verifier_public_keys=protocol_dict["trace_verifier_public_keys"],
        verifier_public_key=verifier_private_key.get_public_key().to_hex(),
    )