from bitcoinutils.keys import PublicKey

from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


class ExecutionChallengeScriptGeneratorService:

    @staticmethod
    def trace_to_script_mapping():
        #return [0, 1, 3, 4, 6, 7, 8, 9, 10, 11, 12]
        return [9, 10, 11, 12, 0, 1, 3, 4, 6, 7, 8]

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()

    def __call__(
        self, signature_public_keys, public_keys, trace_words_lengths, bits_per_digit_checksum
    ):
        script = BitcoinScript()
        trace_to_script_mapping = reversed(self.trace_to_script_mapping())
        max_value = 12
        complementary_trace_to_script_mapping = list(
            map(
                lambda index: max_value - index, trace_to_script_mapping
            )
        )

        for i in complementary_trace_to_script_mapping:
            self.verify_input_nibble_message_from_public_keys(
                script,
                public_keys[i],
                trace_words_lengths[i],
                bits_per_digit_checksum,
                to_alt_stack=True,
            )

        total_length = 0
        for i in complementary_trace_to_script_mapping:
            current_length = trace_words_lengths[i]
            for _ in range(current_length):
                script.append("OP_FROMALTSTACK")
            if current_length == 2:
                script.extend([1, "OP_ROLL", "OP_DROP"])
                total_length += 1
            else:
                total_length += current_length

        for _ in range(total_length):
            script.append("OP_DROP")

        # current_hardcoded_instruction = "5f0000000000535c00000000000000515800000000005958005f0000000000535c00000000000000000000000000000000000000000000000058000000000059540000005157585759535f5e5d5c5b5a595857565554535251005f5e5d5c5b5a5958575655545352510051766e6f6f6f6f00766e6f6f6f6f575756565555545453535252515100005e5c5a58565452005e5c5a58565452005800580058005800580058005800580001777a01777a01777a01777a01777a01777a01777a01777a51537b8851797658a2635894688852797658a2635894680088567957a0635f670068547901289379557a589379557a57a0635467006893547901289379557a589379557a57a06354670068930290007a0290007a0290007a0290007a0290007a0290007a0290007a0290007a6d6d6d6d0288007a0288007a0288007a0288007a0288007a0288007a0288007a0288007a6d6d6d6d01787a75028f0079028f00795f00527a88517a88028d0079028d00790000527a88517a88028b0079028b00790000527a88517a88028900790289007955795579527a88517a88537a537a6d028d007a028d007a028d007a028d007a028d007a028d007a028d007a028d007a6d6d6d6d5f0000000000577a577a028b007a028b007a028b007a028b007a028b007a028b007a028b007a028b007a01117a9376016393796b0142937993607a9376016193796b01409379935f7a9376015f93796b013e9379935d799376015e93796b013d9379935c799376015d93796b013c9379935b799376015c93796b013b9379935a799376015b93796b013a937993597a93015893796c6c6c6c6c6c6c0287007a0287007a0287007a0287007a0287007a0287007a0287007a0287007a549376016893796b014793799376016793796b014693799376016693796b014593799376016593796b014493799376016493796b014393799376016393796b014293799376016293796b0141937993016093796c6c6c6c6c6c6c006b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6d6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c6c01197a8801187a8801177a8801167a8801157a8801147a8801137a8801127a8801117a88607a885f7a885e7a885d7a885c7a885b7a885a7a88597a88587a88577a88567a88557a88547a88537a88527a88517a8851"
        # current_hardcoded_instruction_without_input = current_hardcoded_instruction[(9*8+2)*2:]
        # current_hardcoded_values = current_hardcoded_instruction[:(9*8+2)*2]
        #
        # total_amount_of_values = int(len(current_hardcoded_values) / 2)
        #
        # execution_script = BitcoinScript.from_raw(scriptrawhex=current_hardcoded_instruction_without_input,
        #                                           has_segwit=True)
        #
        # script = script + execution_script
        #
        # script.append("OP_DROP")

        for signature_public_key in reversed(signature_public_keys):
            script.extend(
                [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

        script.append(1)
        return script
