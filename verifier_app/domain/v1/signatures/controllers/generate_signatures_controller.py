import pickle

from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.setup import NETWORK

from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_verifier_signatures_dto import (
    BitVMXVerifierSignaturesDTO,
)


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
        bitvmx_prover_signatures_dto: BitVMXProverSignaturesDTO,
    ) -> BitVMXVerifierSignaturesDTO:

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
            protocol_dict = pickle.load(f)
        if protocol_dict["network"] == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == protocol_dict["network"].value
        verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))

        protocol_dict["bitvmx_prover_signatures_dto"] = bitvmx_prover_signatures_dto

        bitvmx_protocol_properties_dto = protocol_dict["bitvmx_protocol_properties_dto"]
        bitvmx_protocol_setup_properties_dto = protocol_dict["bitvmx_protocol_setup_properties_dto"]
        bitvmx_prover_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_prover_winternitz_public_keys_dto"
        ]
        bitvmx_verifier_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_verifier_winternitz_public_keys_dto"
        ]

        # Transaction construction
        bitvmx_transactions_dto = self.transaction_generator_from_public_keys_service(
            protocol_dict,
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
        )

        protocol_dict["bitvmx_transactions_dto"] = bitvmx_transactions_dto

        # Scripts construction
        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
            signature_public_keys=protocol_dict["public_keys"],
        )

        verify_prover_signatures_service = self.verify_prover_signatures_service_class(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        verify_prover_signatures_service(
            public_key=protocol_dict["prover_public_key"],
            bitvmx_prover_signatures_dto=bitvmx_prover_signatures_dto,
            bitvmx_transactions_dto=bitvmx_transactions_dto,
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        generate_signatures_service = self.generate_signatures_service_class(
            verifier_private_key, bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        bitvmx_signatures_dto = generate_signatures_service(
            bitvmx_transactions_dto=bitvmx_transactions_dto,
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        protocol_dict["trigger_protocol_signatures"] = [
            bitvmx_signatures_dto.trigger_protocol_signature,
            bitvmx_prover_signatures_dto.trigger_protocol_signature,
        ]

        search_choice_signatures = []
        for i in range(len(bitvmx_signatures_dto.search_choice_signatures)):
            search_choice_signatures.append(
                [
                    bitvmx_signatures_dto.search_choice_signatures[i],
                    bitvmx_prover_signatures_dto.search_choice_signatures[i],
                ]
            )
        protocol_dict["search_choice_signatures"] = search_choice_signatures

        protocol_dict["trigger_execution_signatures"] = [
            bitvmx_signatures_dto.trigger_execution_challenge_signature,
            bitvmx_prover_signatures_dto.trigger_execution_challenge_signature,
        ]
        # execution_challenge_signature = signatures_dict["execution_challenge_signature"]

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
            pickle.dump(protocol_dict, f)

        return bitvmx_signatures_dto.verifier_signatures
