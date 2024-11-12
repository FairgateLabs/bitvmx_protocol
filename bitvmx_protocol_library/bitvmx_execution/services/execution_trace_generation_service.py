from typing import Optional

from bitvmx_protocol_library.bitvmx_execution.services.bitvmx_wrapper import BitVMXWrapper


class ExecutionTraceGenerationService:

    @staticmethod
    def elf_file():
        # return "plainc.elf"
        # return "zkverifier.elf"
        return "test_input.elf"

    # This can be computed on the fly to avoid storing it (it does not take that much time to generate it)
    @staticmethod
    def commitment_file():
        if ExecutionTraceGenerationService.elf_file() == "zkverifier.elf":
            return "./execution_files/instruction_commitment_zk.txt"
        elif ExecutionTraceGenerationService.elf_file() == "plainc.elf":
            return "./execution_files/instruction_commitment.txt"
        elif ExecutionTraceGenerationService.elf_file() == "test_input.elf":
            return "./execution_files/instruction_commitment_input.txt"

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.elf_file_name = self.elf_file()
        self.bitvmx_wrapper = BitVMXWrapper(base_path)

    def __call__(self, setup_uuid: str, input_hex: Optional[str] = None):
        self.bitvmx_wrapper.generate_execution_checkpoints(
            setup_uuid=setup_uuid, elf_file=self.elf_file_name, input_hex=input_hex
        )
        # return self.execution_trace_parsing_service(
        #     self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", protocol_dict
        # )
