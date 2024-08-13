from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class TriggerWrongHashChallengeScriptGeneratorService:
    def __init__(self):
        pass

    def __call__(self):
        script = BitcoinScript()
        script.append("OP_DROP")
        script.append(1)
        return script
