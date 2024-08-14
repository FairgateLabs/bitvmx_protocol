from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class TriggerWrongHashChallengeScriptGeneratorService:
    def __init__(self):
        pass

    def __call__(self, verifier_public_key: str):
        script = BitcoinScript()
        script.extend([PublicKey(hex_str=verifier_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"])
        script.append(1)
        return script
