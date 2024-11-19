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


class TriggerWrongTraceStepScriptGeneratorService:
    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()

    def __call__(
        self,
        signature_public_keys: List[str],
        verifier_halt_step_public_keys: List[str],
        amount_of_nibbles_halt_step: int,
        amount_of_bits_wrong_step_search: int,
        choice_search_verifier_public_keys_list: List[List[List[str]]],
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

        for choice_list in reversed(choice_search_verifier_public_keys_list):
            self.verify_input_single_word_from_public_keys(
                script=script,
                public_keys=choice_list[0],
                amount_of_bits=amount_of_bits_wrong_step_search,
                to_alt_stack=True,
            )

        self.verify_input_nibble_message_from_public_keys(
            script=script,
            public_keys=verifier_halt_step_public_keys,
            n0=amount_of_nibbles_halt_step,
            bits_per_digit_checksum=bits_per_digit_checksum,
            to_alt_stack=True,
        )

        words_lengths = [2, 3, 3]
        for word_length in words_lengths:
            for i in range(word_length - 1, -1, -1):
                script.append("OP_FROMALTSTACK")
                for _ in range(i * 4):
                    script.extend(["OP_DUP", "OP_ADD"])
                if i < word_length - 1:
                    script.append("OP_ADD")

        amount_of_published_bits = amount_of_bits_wrong_step_search * len(
            choice_search_verifier_public_keys_list
        )

        amount_of_remaining_bits = amount_of_published_bits

        script.append(0)
        while amount_of_remaining_bits > 24:
            script.append("OP_FROMALTSTACK")
            amount_of_remaining_bits -= amount_of_bits_wrong_step_search
            for _ in range(amount_of_remaining_bits - 24):
                script.extend(["OP_DUP", "OP_ADD"])
            script.append("OP_ADD")

        script.append(0)
        while amount_of_remaining_bits > 12:
            script.append("OP_FROMALTSTACK")
            amount_of_remaining_bits -= amount_of_bits_wrong_step_search
            for _ in range(amount_of_remaining_bits - 12):
                script.extend(["OP_DUP", "OP_ADD"])
            script.append("OP_ADD")

        script.append(0)
        while amount_of_remaining_bits > 0:
            script.append("OP_FROMALTSTACK")
            amount_of_remaining_bits -= amount_of_bits_wrong_step_search
            for _ in range(amount_of_remaining_bits):
                script.extend(["OP_DUP", "OP_ADD"])
            script.append("OP_ADD")

        script.extend([5, "OP_PICK", 3, "OP_PICK", "OP_LESSTHAN"])

        script.append("OP_IF")

        script.extend(["OP_2DROP", "OP_2DROP", "OP_2DROP"])
        script.append("OP_ELSE")

        script.extend([5, "OP_ROLL", 3, "OP_ROLL", "OP_EQUALVERIFY"])
        script.extend([3, "OP_PICK", 2, "OP_PICK", "OP_LESSTHAN"])

        script.append("OP_IF")

        script.extend(["OP_2DROP", "OP_2DROP"])

        script.append("OP_ELSE")

        script.extend([3, "OP_ROLL", 2, "OP_ROLL", "OP_EQUALVERIFY"])
        script.append("OP_LESSTHAN")
        script.append("OP_VERIFY")

        script.append("OP_ENDIF")

        script.append("OP_ENDIF")

        script.append(1)
        return script
