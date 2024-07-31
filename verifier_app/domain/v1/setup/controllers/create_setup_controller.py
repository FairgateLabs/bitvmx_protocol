import os
import pickle
import secrets

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import NETWORK

from bitvmx_protocol_library.enums import BitcoinNetwork


class CreateSetupController:
    def __init__(self):
        pass

    async def __call__(self, setup_uuid: str, network: BitcoinNetwork) -> str:
        if network == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == network.value
        private_key = PrivateKey(b=secrets.token_bytes(32))
        print("Init setup for id " + str(setup_uuid))
        protocol_dict = {
            "verifier_private_key": private_key.to_bytes().hex(),
            "last_confirmed_step": None,
            "last_confirmed_step_tx_id": None,
            "setup_uuid": setup_uuid,
            "search_choices": [],
            "search_hashes": {},
            "network": network,
        }
        os.makedirs(f"verifier_files/{setup_uuid}")
        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "xb") as f:
            pickle.dump(protocol_dict, f)
        return private_key.get_public_key().to_hex()