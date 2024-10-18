from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)


class TriggerInputEquivocationChallengeScriptsGeneratorService:
    def __init__(self):
        pass

    def __call__(
        self,
        signature_public_keys: List[str],
        base_input_address: str,
        amount_of_input_words: int,
        address_public_keys: List[str],
        value_public_keys: List[str],
    ) -> BitcoinScriptList:

        script = BitcoinScript()

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return BitcoinScriptList(script)
