import pickle
from typing import List

from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.setup import NETWORK

from bitvmx_protocol_library.enums import BitcoinNetwork


class GenerateSignaturesController:
    def __init__(
        self,
        bitvmx_bitcoin_scripts_generator_service,
        transaction_generator_from_public_keys_service,
        generate_signatures_service_class,
        verify_prover_signatures_service_class,
    ):
        self.bitvmx_bitcoin_scripts_generator_service = bitvmx_bitcoin_scripts_generator_service
        self.transaction_generator_from_public_keys_service = (
            transaction_generator_from_public_keys_service
        )
        self.generate_signatures_service_class = generate_signatures_service_class
        self.verify_prover_signatures_service_class = verify_prover_signatures_service_class

    def __call__(
        self,
        setup_uuid: str,
        trigger_protocol_signature: str,
        search_choice_signatures: List[str],
        trigger_execution_signature: str,
    ):

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
            protocol_dict = pickle.load(f)
        if protocol_dict["network"] == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == protocol_dict["network"].value
        verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))

        # funding_amount_satoshis = protocol_dict["funding_amount_satoshis"]
        # step_fees_satoshis = protocol_dict["step_fees_satoshis"]
        protocol_dict["trigger_protocol_prover_signature"] = trigger_protocol_signature
        protocol_dict["search_choice_prover_signatures"] = search_choice_signatures
        protocol_dict["trigger_execution_signature"] = trigger_execution_signature

        bitvmx_protocol_properties_dto = protocol_dict["bitvmx_protocol_properties_dto"]
        bitvmx_protocol_setup_properties_dto = protocol_dict["bitvmx_protocol_setup_properties_dto"]
        bitvmx_prover_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_prover_winternitz_public_keys_dto"
        ]
        bitvmx_verifier_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_verifier_winternitz_public_keys_dto"
        ]

        # Transaction construction
        self.transaction_generator_from_public_keys_service(
            protocol_dict,
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
        )

        # Scripts construction
        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
            signature_public_keys=protocol_dict["public_keys"],
        )

        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])

        verify_prover_signatures_service = self.verify_prover_signatures_service_class(
            destroyed_public_key
        )
        verify_prover_signatures_service(
            protocol_dict=protocol_dict,
            public_key=protocol_dict["prover_public_key"],
            trigger_protocol_signature=protocol_dict["trigger_protocol_prover_signature"],
            search_choice_signatures=protocol_dict["search_choice_prover_signatures"],
            trigger_execution_signature=protocol_dict["trigger_execution_signature"],
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        generate_signatures_service = self.generate_signatures_service_class(
            verifier_private_key, destroyed_public_key
        )
        signatures_dict = generate_signatures_service(
            protocol_dict=protocol_dict,
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

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

        return hash_result_signature_verifier, search_hash_signatures, trace_signature
