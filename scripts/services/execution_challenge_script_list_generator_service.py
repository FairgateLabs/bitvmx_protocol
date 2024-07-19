from bitcoinutils.keys import PublicKey

from bitvmx_execution.execution_trace_commitment_generation_service import (
    ExecutionTraceCommitmentGenerationService,
)
from scripts.bitcoin_script import BitcoinScript
from scripts.bitcoin_script_list import BitcoinScriptList
from winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


class ExecutionChallengeScriptListGeneratorService:

    @staticmethod
    def trace_to_script_mapping():
        return [9, 10, 11, 12, 0, 1, 3, 4, 6, 7, 8]
        # return [9, 10, 11, 12, 3, 4, 0, 1, 6, 7, 8]

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.execution_trace_commitment_generation_service = (
            ExecutionTraceCommitmentGenerationService(
                "./execution_files/instruction_commitment.txt",
                "./execution_files/instruction_mapping.txt",
            )
        )

    def __call__(
        self, signature_public_keys, public_keys, trace_words_lengths, bits_per_digit_checksum
    ) -> BitcoinScriptList:
        key_list, instruction_dict = self.execution_trace_commitment_generation_service()
        script_list = []
        for key in key_list:
            script = BitcoinScript()
            trace_to_script_mapping = reversed(self.trace_to_script_mapping())
            max_value = 12
            complementary_trace_to_script_mapping = list(
                map(lambda index: max_value - index, trace_to_script_mapping)
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
            current_micro = key[-2:]
            current_pc_address = key[:-2]
            for i in reversed(complementary_trace_to_script_mapping):
                current_length = trace_words_lengths[i]
                for j in range(current_length):
                    script.append("OP_FROMALTSTACK")

                    # MICRO CHECK
                    if i == 5:
                        script.extend(["OP_DUP", int(current_micro, 16), "OP_NUMEQUALVERIFY"])

                    # PC ADDRESS CHECK
                    if i == 6:
                        script.extend(
                            ["OP_DUP", int(current_pc_address[j], 16), "OP_NUMEQUALVERIFY"]
                        )

                if current_length == 2:
                    script.extend([1, "OP_ROLL", "OP_DROP"])
                    total_length += 1
                else:
                    total_length += current_length

            execution_script = BitcoinScript.from_raw(
                scriptrawhex=instruction_dict[key], has_segwit=True
            )

            script = script + execution_script

            script.extend(
                [PublicKey(hex_str=signature_public_keys[-1]).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
            )

            script.append(1)
            script_list.append(script)
        return BitcoinScriptList(script_list)
