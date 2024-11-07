from typing import List

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class GenericTriggerWrongLatterStepChallengeScriptGeneratorService:

    def __call__(
        self,
        signature_public_keys: List[str],
    ) -> BitcoinScript:
        script = BitcoinScript()
        script.append("OP_DROP")
        script.append(1)
        return script


class TriggerWrongLatterStep1ChallengeScriptGeneratorService(
    GenericTriggerWrongLatterStepChallengeScriptGeneratorService
):
    pass


class TriggerWrongLatterStep2ChallengeScriptGeneratorService(
    GenericTriggerWrongLatterStepChallengeScriptGeneratorService
):
    pass
