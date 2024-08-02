import pickle
from http import HTTPStatus

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import NETWORK
from fastapi import HTTPException

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import (
    BitVMXProverWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.enums import BitcoinNetwork


class GeneratePublicKeysController:

    def __init__(self, generate_verifier_public_keys_service_class):
        self.generate_verifier_public_keys_service_class = (
            generate_verifier_public_keys_service_class
        )

    async def __call__(
        self,
        setup_uuid: str,
        public_keys_post_view_input,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_prover_winternitz_public_keys_dto: BitVMXProverWinternitzPublicKeysDTO,
    ):
        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
            protocol_dict = pickle.load(f)
        if protocol_dict["network"] == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == protocol_dict["network"].value
        verifier_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["verifier_private_key"]))

        protocol_dict["verifier_public_key"] = verifier_private_key.get_public_key().to_hex()

        if (
            verifier_private_key.get_public_key().to_x_only_hex()
            not in bitvmx_protocol_setup_properties_dto.seed_unspendable_public_key
        ):
            raise HTTPException(
                status_code=HTTPStatus.EXPECTATION_FAILED, detail="Seed does not contain public key"
            )

        protocol_dict["bitvmx_prover_winternitz_public_keys_dto"] = (
            bitvmx_prover_winternitz_public_keys_dto
        )
        protocol_dict["bitvmx_protocol_setup_properties_dto"] = bitvmx_protocol_setup_properties_dto
        protocol_dict["bitvmx_protocol_properties_dto"] = bitvmx_protocol_properties_dto

        generate_verifier_public_keys_service = self.generate_verifier_public_keys_service_class(
            verifier_private_key
        )
        bitvmx_verifier_winternitz_public_keys_dto = generate_verifier_public_keys_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto
        )
        protocol_dict["bitvmx_verifier_winternitz_public_keys_dto"] = (
            bitvmx_verifier_winternitz_public_keys_dto
        )

        protocol_dict["public_keys"] = [
            bitvmx_protocol_setup_properties_dto.verifier_destroyed_public_key,
            bitvmx_protocol_setup_properties_dto.prover_destroyed_public_key,
        ]

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
            pickle.dump(protocol_dict, f)

        return (
            bitvmx_verifier_winternitz_public_keys_dto,
            verifier_private_key.get_public_key().to_hex(),
        )
