from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.confirm_nibbles_script_generator_service import (
    ConfirmNibblesScriptGeneratorService,
)


class TriggerProtocolScriptGeneratorService:

    def __init__(self):
        self.confirm_nibbles_script_generator_service = ConfirmNibblesScriptGeneratorService()

    def __call__(
        self,
        signature_public_keys: List[str],
        prover_halt_step_public_keys: List[str],
        verifier_halt_step_public_keys: List[str],
        amount_of_nibbles_halt_step: int,
        bits_per_digit_checksum: int,
    ):
        script = BitcoinScript()

        # script.append("OP_CODESEPARATOR")

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        self.confirm_nibbles_script_generator_service(
            script,
            prover_halt_step_public_keys,
            verifier_halt_step_public_keys,
            amount_of_nibbles_halt_step,
            bits_per_digit_checksum,
        )

        script.append(1)
        return script
