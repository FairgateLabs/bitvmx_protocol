from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.bitcoin_script import BitcoinScript


class TriggerProtocolScriptGeneratorService:

    def __call__(self, signature_public_keys):
        script = BitcoinScript()

        # script.append("OP_CODESEPARATOR")

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return script
