
from bitvmx_execution.services.bitvmx_wrapper import BitVMXWrapper


class ExecutionTraceGenerationService:

    @staticmethod
    def elf_file():
        return "plainc.elf"

    @staticmethod
    def commitment_file():
        if ExecutionTraceGenerationService.elf_file() == "zkverifier.elf":
            return "./execution_files/instruction_commitment_zk.txt"
        elif ExecutionTraceGenerationService.elf_file() == "plainc.elf":
            return "./execution_files/instruction_commitment.txt"

    def __init__(self, base_path):
        self.base_path = base_path
        # self.execution_trace_parsing_service = ExecutionTraceParsingService(
        #     base_path + "execution_trace.txt"
        # )
        self.elf_file_name = self.elf_file()
        self.bitvmx_wrapper = BitVMXWrapper(base_path)

    def __call__(self, protocol_dict):
        self.bitvmx_wrapper.generate_execution_checkpoints(protocol_dict, self.elf_file_name)
        # return self.execution_trace_parsing_service(
        #     self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", protocol_dict
        # )
