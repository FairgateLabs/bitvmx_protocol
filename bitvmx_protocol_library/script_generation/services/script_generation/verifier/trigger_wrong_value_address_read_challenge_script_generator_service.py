from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class GenericTriggerWrongValueAddressReadChallengeScriptGeneratorService:

    def __call__(
        self,
        signature_public_keys: List[str],
    ) -> BitcoinScript:
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


class TriggerWrongValueAddressRead1ChallengeScriptGeneratorService(
    GenericTriggerWrongValueAddressReadChallengeScriptGeneratorService
):
    pass


class TriggerWrongValueAddressRead2ChallengeScriptGeneratorService(
    GenericTriggerWrongValueAddressReadChallengeScriptGeneratorService
):
    pass
