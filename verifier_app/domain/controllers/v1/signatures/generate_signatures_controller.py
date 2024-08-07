import pickle

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import NETWORK

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_verifier_signatures_dto import (
    BitVMXVerifierSignaturesDTO,
)
from verifier_app.domain.persistence.interfaces.bitvmx_protocol_verifier_private_dto_persistence_interface import (
    BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
)


class GenerateSignaturesController:
    def __init__(
        self,
        bitvmx_bitcoin_scripts_generator_service,
        transaction_generator_from_public_keys_service,
        generate_signatures_service_class,
        verify_prover_signatures_service_class,
        common_protocol_properties,
        bitvmx_protocol_verifier_private_dto_persistence: BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
    ):
        self.bitvmx_bitcoin_scripts_generator_service = bitvmx_bitcoin_scripts_generator_service
        self.transaction_generator_from_public_keys_service = (
            transaction_generator_from_public_keys_service
        )
        self.generate_signatures_service_class = generate_signatures_service_class
        self.verify_prover_signatures_service_class = verify_prover_signatures_service_class
        self.common_protocol_properties = common_protocol_properties
        self.bitvmx_protocol_verifier_private_dto_persistence = (
            bitvmx_protocol_verifier_private_dto_persistence
        )

    def __call__(
        self,
        setup_uuid: str,
        bitvmx_prover_signatures_dto: BitVMXProverSignaturesDTO,
    ) -> BitVMXVerifierSignaturesDTO:

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
            protocol_dict = pickle.load(f)
        if self.common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == self.common_protocol_properties.network.value

        bitvmx_protocol_verifier_private_dto = (
            self.bitvmx_protocol_verifier_private_dto_persistence.get(setup_uuid=setup_uuid)
        )
        destroyed_private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.destroyed_private_key)
        )

        protocol_dict["bitvmx_prover_signatures_dto"] = bitvmx_prover_signatures_dto

        bitvmx_protocol_properties_dto = protocol_dict["bitvmx_protocol_properties_dto"]
        bitvmx_protocol_setup_properties_dto = protocol_dict["bitvmx_protocol_setup_properties_dto"]

        # Transaction construction
        bitvmx_transactions_dto = self.transaction_generator_from_public_keys_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        protocol_dict["bitvmx_transactions_dto"] = bitvmx_transactions_dto

        # Scripts construction
        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            signature_public_keys=bitvmx_protocol_setup_properties_dto.signature_public_keys,
        )

        verify_prover_signatures_service = self.verify_prover_signatures_service_class(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        verify_prover_signatures_service(
            public_key=bitvmx_protocol_setup_properties_dto.prover_destroyed_public_key,
            bitvmx_prover_signatures_dto=bitvmx_prover_signatures_dto,
            bitvmx_transactions_dto=bitvmx_transactions_dto,
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        generate_signatures_service = self.generate_signatures_service_class(
            destroyed_private_key, bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )
        bitvmx_signatures_dto = generate_signatures_service(
            bitvmx_transactions_dto=bitvmx_transactions_dto,
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        search_choice_signatures = []
        for i in range(len(bitvmx_signatures_dto.search_choice_signatures)):
            search_choice_signatures.append(
                [
                    bitvmx_signatures_dto.search_choice_signatures[i],
                    bitvmx_prover_signatures_dto.search_choice_signatures[i],
                ]
            )

        # execution_challenge_signature = signatures_dict["execution_challenge_signature"]

        bitvmx_verifier_signatures_dto = bitvmx_signatures_dto.prover_signatures_dto
        # This should be sent in the API call
        verifier_signatures_dtos = {
            bitvmx_protocol_setup_properties_dto.uuid: bitvmx_verifier_signatures_dto
        }

        verifier_public_keys = {
            bitvmx_protocol_setup_properties_dto.uuid: bitvmx_protocol_setup_properties_dto.verifier_destroyed_public_key
        }

        bitvmx_protocol_verifier_dto = BitVMXProtocolVerifierDTO(
            prover_public_key=bitvmx_protocol_setup_properties_dto.prover_destroyed_public_key,
            verifier_public_keys=verifier_public_keys,
            prover_signatures_dto=bitvmx_prover_signatures_dto,
            verifier_signatures_dtos=verifier_signatures_dtos,
        )

        protocol_dict["bitvmx_protocol_verifier_dto"] = bitvmx_protocol_verifier_dto

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
            pickle.dump(protocol_dict, f)

        self.bitvmx_protocol_verifier_private_dto_persistence.delete_private_key(
            setup_uuid=setup_uuid
        )

        return bitvmx_signatures_dto.verifier_signatures_dto
