from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class TriggerReadSearchEquivocationScriptGeneratorService:
    def __init__(self):
        pass

    def __call__(
        self,
        signature_public_keys: List[str],
        choice_search_prover_public_keys_list: List[List[List[str]]],
    ):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )
        script.append(1)
        return script
