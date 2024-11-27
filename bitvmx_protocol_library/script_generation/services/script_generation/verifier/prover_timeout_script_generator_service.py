from datetime import timedelta
from math import ceil
from typing import List

from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
from bitcoinutils.keys import PublicKey
from bitcoinutils.transactions import Sequence

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)


class ProverTimeoutScriptGeneratorService:
    def __init__(self):
        pass

    def __call__(
        self,
        signature_public_keys: List[str],
        timeout_wait_time: timedelta,
    ):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )
        total_amount_of_seconds = timeout_wait_time.total_seconds()
        total_amount_of_blocks = ceil(total_amount_of_seconds / 600)
        interval = Sequence(
            seq_type=TYPE_RELATIVE_TIMELOCK, value=total_amount_of_blocks, is_type_block=True
        )
        script.extend([interval.for_script(), "OP_CHECKSEQUENCEVERIFY"])
        return script
