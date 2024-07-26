import multiprocessing
from time import time

from bitcoinutils.keys import PublicKey

from bitvmx_execution.services.execution_trace_commitment_generation_service import (
    ExecutionTraceCommitmentGenerationService,
)
from bitvmx_protocol_library.script_generation.entities.bitcoin_script import BitcoinScript
from bitvmx_protocol_library.script_generation.entities.bitvmx_execution_script_list import BitVMXExecutionScriptList
from winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


def _generate_script_from_key(
    key,
    signature_public_keys,
    public_keys,
    trace_words_lengths,
    bits_per_digit_checksum,
    instruction_dict,
    trace_to_script_mapping,
):
    script = BitcoinScript()
    trace_to_script_mapping = reversed(trace_to_script_mapping)
    max_value = 12
    complementary_trace_to_script_mapping = list(
        map(lambda index: max_value - index, trace_to_script_mapping)
    )

    verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()

    for i in complementary_trace_to_script_mapping:
        verify_input_nibble_message_from_public_keys(
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
                script.extend(["OP_DUP", int(current_pc_address[j], 16), "OP_NUMEQUALVERIFY"])

        if current_length == 2:
            script.extend([1, "OP_ROLL", "OP_DROP"])
            total_length += 1
        else:
            total_length += current_length

    execution_script = BitcoinScript.from_raw(scriptrawhex=instruction_dict[key], has_segwit=True)

    script = script + execution_script

    script.extend(
        [PublicKey(hex_str=signature_public_keys[-1]).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
    )

    script.append(1)
    return script


class ExecutionChallengeScriptListGeneratorService:

    @staticmethod
    def trace_to_script_mapping():
        return [9, 10, 11, 12, 0, 1, 3, 4, 6, 7, 8]
        # return [9, 10, 11, 12, 3, 4, 0, 1, 6, 7, 8]

    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.execution_trace_commitment_generation_service = (
            ExecutionTraceCommitmentGenerationService(
                "./execution_files/instruction_mapping.txt",
            )
        )

    def _generate_script_for_file(
        self,
        signature_public_keys,
        public_keys,
        trace_words_lengths,
        bits_per_digit_checksum,
    ):
        key_list, instruction_dict = self.execution_trace_commitment_generation_service()
        script_list = []

        total_amount_of_processes = multiprocessing.cpu_count()

        def process_tasks(
            signature_public_keys,
            public_keys,
            trace_words_lengths,
            bits_per_digit_checksum,
            instruction_dict,
            trace_to_script_mapping,
            input_queue,
            output_queue,
        ):
            while not input_queue.empty():
                current_key = input_queue.get()
                output_queue.put(
                    _generate_script_from_key(
                        current_key,
                        signature_public_keys,
                        public_keys,
                        trace_words_lengths,
                        bits_per_digit_checksum,
                        instruction_dict,
                        trace_to_script_mapping,
                    )
                )

        input_queues = []
        output_queues = []
        processes = []
        for _ in range(total_amount_of_processes - 1):
            input_queue = multiprocessing.Queue()
            output_queue = multiprocessing.Queue()
            input_queues.append(input_queue)
            output_queues.append(output_queue)
            current_process = multiprocessing.Process(
                target=process_tasks,
                args=(
                    signature_public_keys,
                    public_keys,
                    trace_words_lengths,
                    bits_per_digit_checksum,
                    instruction_dict,
                    self.trace_to_script_mapping(),
                    input_queue,
                    output_queue,
                ),
            )
            processes.append(current_process)

        amount_of_queues = len(input_queues)
        for i in range(len(key_list)):
            current_key = key_list[i]
            input_queues[i % amount_of_queues].put(current_key)

        i = 1
        for process in processes:
            print("Starting new process: " + str(i))
            i += 1
            process.start()

        init_time = time()
        for j in range(len(key_list)):
            if j % 100 == 0:
                print("Queue item get " + str(j) + " " + str(time() - init_time))
            script_list.append(output_queues[j % amount_of_queues].get())

        for process in processes:
            i -= 1
            print("Waiting for end of process" + str(i))
            process.join()

        return script_list

    def __call__(
        self, signature_public_keys, public_keys, trace_words_lengths, bits_per_digit_checksum
    ) -> BitVMXExecutionScriptList:
        # Original method
        # script_list = self._generate_script_for_file(
        #     signature_public_keys,
        #     public_keys,
        #     trace_words_lengths,
        #     bits_per_digit_checksum,
        # )
        # bitcoin_script_list = BitcoinScriptList(script_list)

        # New method
        key_list, instruction_dict = self.execution_trace_commitment_generation_service()

        bitvmx_execution_script_list = BitVMXExecutionScriptList(
            key_list,
            instruction_dict,
            signature_public_keys,
            public_keys,
            trace_words_lengths,
            bits_per_digit_checksum,
        )

        # test_public_key = PublicKey(hex_str=signature_public_keys[0])
        # assert (
        #     bitcoin_script_list.get_taproot_address(test_public_key).to_string()
        #     == bitvmx_execution_script_list.get_taproot_address(test_public_key).to_string()
        # )
        return bitvmx_execution_script_list
