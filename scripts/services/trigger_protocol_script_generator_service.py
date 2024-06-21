from scripts.bitcoin_script import BitcoinScript


class TriggerProtocolScriptGeneratorService:

    def __call__(self):
        script = BitcoinScript()
        # trigger_protocol_script.extend(
        #     [prover_public_key.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        # )
        # trigger_protocol_script.extend(
        #     [verifier_public_key.to_x_only_hex(), "OP_CHECKSIGVERIFY"]
        # )
        script.append(1)
        return script
