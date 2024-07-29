import os
import pickle
import secrets

from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import setup

from bitvmx_protocol_library.enums import BitcoinNetwork
from verifier_app.api.v1.setup.crud.view_models import SetupPostV1Input, SetupPostV1Output


async def setup_post_view(setup_post_view_input: SetupPostV1Input) -> SetupPostV1Output:
    private_key = PrivateKey(b=secrets.token_bytes(32))
    setup_uuid = setup_post_view_input.setup_uuid
    print("Init setup for id " + str(setup_uuid))
    protocol_dict = {
        "verifier_private_key": private_key.to_bytes().hex(),
        "last_confirmed_step": None,
        "last_confirmed_step_tx_id": None,
        "setup_uuid": setup_uuid,
        "search_choices": [],
        "search_hashes": {},
        "network": setup_post_view_input.network,
    }
    if protocol_dict["network"] == BitcoinNetwork.MUTINYNET:
        setup("testnet")
    else:
        setup(protocol_dict["network"].value)
    os.makedirs(f"verifier_files/{setup_uuid}")
    with open(f"verifier_files/{setup_uuid}/file_database.pkl", "xb") as f:
        pickle.dump(protocol_dict, f)
    return SetupPostV1Output(
        public_key=private_key.get_public_key().to_hex(),
    )
