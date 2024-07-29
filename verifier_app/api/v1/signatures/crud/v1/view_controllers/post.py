import pickle

from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.setup import setup

from bitvmx_protocol_library.enums import BitcoinNetwork
from verifier_app.api.v1.signatures.crud.v1.view_models.post import (
    SignaturesPostV1Input,
    SignaturesPostV1Output,
)


class SignaturesPostViewControllerV1:
    def __init__(
        self,
        scripts_dict_generator_service,
        transaction_generator_from_public_keys_service,
        generate_signatures_service_class,
        verify_prover_signatures_service_class,
    ):
        self.scripts_dict_generator_service = scripts_dict_generator_service
        self.transaction_generator_from_public_keys_service = (
            transaction_generator_from_public_keys_service
        )
        self.generate_signatures_service_class = generate_signatures_service_class
        self.verify_prover_signatures_service_class = verify_prover_signatures_service_class

    async def __call__(
        self, setup_post_view_input: SignaturesPostV1Input
    ) -> SignaturesPostV1Output:
        setup_uuid = setup_post_view_input.setup_uuid
        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
            protocol_dict = pickle.load(f)
        if protocol_dict["network"] == BitcoinNetwork.MUTINYNET:
            setup("testnet")
        else:
            setup(protocol_dict["network"].value)
        verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))

        # funding_amount_satoshis = protocol_dict["funding_amount_satoshis"]
        # step_fees_satoshis = protocol_dict["step_fees_satoshis"]
        protocol_dict["trigger_protocol_prover_signature"] = (
            setup_post_view_input.trigger_protocol_signature
        )
        protocol_dict["search_choice_prover_signatures"] = (
            setup_post_view_input.search_choice_signatures
        )
        protocol_dict["trigger_execution_signature"] = (
            setup_post_view_input.trigger_execution_signature
        )

        # Transaction construction
        self.transaction_generator_from_public_keys_service(protocol_dict)

        # Scripts construction
        scripts_dict = self.scripts_dict_generator_service(protocol_dict)

        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])

        verify_prover_signatures_service = self.verify_prover_signatures_service_class(
            destroyed_public_key
        )
        verify_prover_signatures_service(
            protocol_dict,
            scripts_dict,
            protocol_dict["prover_public_key"],
            protocol_dict["trigger_protocol_prover_signature"],
            protocol_dict["search_choice_prover_signatures"],
            protocol_dict["trigger_execution_signature"],
        )

        generate_signatures_service = self.generate_signatures_service_class(
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
        protocol_dict["trigger_execution_signatures"] = [
            signatures_dict["trigger_execution_signature"],
            protocol_dict["trigger_execution_signature"],
        ]
        # execution_challenge_signature = signatures_dict["execution_challenge_signature"]

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
            pickle.dump(protocol_dict, f)

        return SignaturesPostV1Output(
            verifier_hash_result_signature=hash_result_signature_verifier,
            verifier_search_hash_signatures=search_hash_signatures,
            verifier_trace_signature=trace_signature,
            # verifier_execution_challenge_signature=execution_challenge_signature,
        )
