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


class TriggerWrongProgramCounterChallengeScriptGeneratorService:
    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.verify_input_single_word_from_public_keys = VerifyDigitSignatureSingleWordService()
        self.cached_sha_scripts = {}

    def __call__(
        self,
        signature_public_keys: List[str],
        trace_words_lengths: List[int],
        amount_of_bits_wrong_step_search: int,
        hash_search_public_keys_list: List[List[List[str]]],
        choice_search_prover_public_keys_list: List[List[List[str]]],
        trace_prover_public_keys: List[List[str]],
        hash_result_public_keys: List[str],
        amount_of_nibbles_hash: int,
        amount_of_bits_per_digit_checksum: int,
        bin_wrong_choice: str,
    ):
        choice = int(bin_wrong_choice, 2)
        script = BitcoinScript()
        for signature_public_key in signature_public_keys:
            script.extend(
                [
                    PublicKey(hex_str=signature_public_key).to_x_only_hex(),
                    "OP_CHECKSIGVERIFY",
                ]
            )

        # wrong_hash_choice_array = [
        #     bin_wrong_choice[i : i + amount_of_bits_wrong_step_search].zfill(
        #         amount_of_bits_wrong_step_search
        #     )
        #     for i in range(0, len(bin_wrong_choice), amount_of_bits_wrong_step_search)
        # ]
        # counter = -1
        # # Character we need to discard at the end of the array
        # if wrong_hash_choice_array[counter] == ("0" * amount_of_bits_wrong_step_search):
        #     suffix_character = "0"
        # else:
        #     suffix_character = "1"
        #
        # if choice == 0:
        #     for choice_list in reversed(choice_search_prover_public_keys_list):
        #         self.verify_input_single_word_from_public_keys(
        #             script=script,
        #             public_keys=choice_list[0],
        #             amount_of_bits=amount_of_bits_wrong_step_search,
        #             to_alt_stack=False,
        #         )
        #         script.append(0)
        #         script.append("OP_EQUALVERIFY")
        # else:
        #     while -counter <= len(wrong_hash_choice_array):
        #         self.verify_input_single_word_from_public_keys(
        #             script=script,
        #             public_keys=choice_search_prover_public_keys_list[counter][0],
        #             amount_of_bits=amount_of_bits_wrong_step_search,
        #             to_alt_stack=False,
        #         )
        #         script.append(int(wrong_hash_choice_array[counter], 2))
        #         script.append("OP_EQUALVERIFY")
        #         if wrong_hash_choice_array[counter] != (
        #             suffix_character * amount_of_bits_wrong_step_search
        #         ):
        #             break
        #         counter -= 1
        script.append(1)
        return script
