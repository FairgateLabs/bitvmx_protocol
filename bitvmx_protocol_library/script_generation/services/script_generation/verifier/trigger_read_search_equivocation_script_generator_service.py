from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_single_word_service import (
    VerifyDigitSignatureSingleWordService,
)


class TriggerReadSearchEquivocationScriptGeneratorService:
    def __init__(self):
        self.verify_input_nibbles_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()

    def __call__(
        self,
        signature_public_keys: List[str],
        hash_search_prover_public_keys: List[List[str]],
        hash_read_search_prover_public_keys: List[List[str]],
        amount_of_nibbles_hash: int,
        choice_search_prover_public_keys: List[List[List[str]]],
        choice_read_search_prover_public_keys: List[List[List[str]]],
        amount_of_bits_wrong_step_search: int,
        bits_per_digit_checksum: int,
    ):
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )

        for hash_public_keys in hash_search_prover_public_keys:
            self.verify_input_nibbles_message_from_public_keys(
                script=script,
                public_keys=hash_public_keys,
                n0=amount_of_nibbles_hash,
                bits_per_digit_checksum=bits_per_digit_checksum,
                to_alt_stack=True,
            )

        for hash_public_keys in reversed(hash_read_search_prover_public_keys):
            self.verify_input_nibbles_message_from_public_keys(
                script=script,
                public_keys=hash_public_keys,
                n0=amount_of_nibbles_hash,
                bits_per_digit_checksum=bits_per_digit_checksum,
                to_alt_stack=False,
            )
            script.append(0)
            for i in range(amount_of_nibbles_hash, 0, -1):
                script.extend([i, "OP_ROLL", "OP_FROMALTSTACK", "OP_EQUAL", "OP_ADD"])
            script.append(amount_of_nibbles_hash)
            script.append("OP_LESSTHAN")
            script.append("OP_VERIFY")

        for choice_list in reversed(choice_search_prover_public_keys):
            self.verify_input_single_word_from_public_keys(
                script=script,
                public_keys=choice_list[0],
                amount_of_bits=amount_of_bits_wrong_step_search,
                to_alt_stack=True,
            )

        for choice_list in choice_read_search_prover_public_keys:
            self.verify_input_single_word_from_public_keys(
                script=script,
                public_keys=choice_list[0],
                amount_of_bits=amount_of_bits_wrong_step_search,
                to_alt_stack=False,
            )
            script.append("OP_FROMALTSTACK")
            script.append("OP_EQUALVERIFY")

        script.append(1)
        return script
