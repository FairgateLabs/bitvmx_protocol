import secrets

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import NETWORK

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_private_dto import (
    BitVMXProtocolVerifierPrivateDTO,
)
from bitvmx_protocol_library.enums import BitcoinNetwork
from verifier_app.domain.persistence.interfaces.bitvmx_protocol_verifier_private_dto_persistence_interface import (
    BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
)


class CreateSetupController:
    def __init__(
        self,
        bitvmx_protocol_verifier_private_dto_persistence: BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
    ):
        self.bitvmx_protocol_verifier_private_dto_persistence = (
            bitvmx_protocol_verifier_private_dto_persistence
        )

    async def __call__(self, setup_uuid: str, network: BitcoinNetwork) -> str:
        if network == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == network.value
        private_key = PrivateKey(b=secrets.token_bytes(32))
        winternitz_private_key = PrivateKey(b=secrets.token_bytes(32))
        print("Init setup for id " + str(setup_uuid))
        bitvmx_protocol_verifier_private_dto = BitVMXProtocolVerifierPrivateDTO(
            winternitz_private_key=winternitz_private_key.to_bytes().hex(),
            destroyed_private_key=private_key.to_bytes().hex(),
        )
        self.bitvmx_protocol_verifier_private_dto_persistence.create(
            setup_uuid=setup_uuid,
            bitvmx_protocol_verifier_private_dto=bitvmx_protocol_verifier_private_dto,
        )
        return private_key.get_public_key().to_hex()
