from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class TriggerNoHaltInHaltStepChallengeScriptGeneratorService:
    def __call__(self, signature_public_keys: List[str]):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )
        # script.append("OP_DROP")
        script.append(1)
        return script
