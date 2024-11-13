import multiprocessing
from time import time

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_commitment_generation_service import (
    ExecutionTraceCommitmentGenerationService,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitvmx_execution_script_list import (
    BitVMXExecutionScriptList,
)
from bitvmx_protocol_library.script_generation.services.script_generation.prover.execution_challenge_script_from_key_generator_service import (
    ExecutionChallengeScriptFromKeyGeneratorService,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
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
                execution_challenge_script_from_key_generator_service = (
                    ExecutionChallengeScriptFromKeyGeneratorService()
                )
                output_queue.put(
                    execution_challenge_script_from_key_generator_service(
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
        self,
        signature_public_keys,
        public_keys,
        trace_words_lengths,
        bits_per_digit_checksum,
        prover_signature_public_key,
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
        key_list, instruction_dict, opcode_dict = (
            self.execution_trace_commitment_generation_service()
        )

        bitvmx_execution_script_list = BitVMXExecutionScriptList(
            key_list=key_list,
            instruction_dict=instruction_dict,
            opcode_dict=opcode_dict,
            signature_public_keys=[prover_signature_public_key],
            public_keys=public_keys,
            trace_words_lengths=trace_words_lengths,
            bits_per_digit_checksum=bits_per_digit_checksum,
        )

        # test_public_key = PublicKey(hex_str=signature_public_keys[0])
        # assert (
        #     bitcoin_script_list.get_taproot_address(test_public_key).to_string()
        #     == bitvmx_execution_script_list.get_taproot_address(test_public_key).to_string()
        # )
        return bitvmx_execution_script_list
