from bitvmx_protocol_library.bitvmx_execution.services.bitvmx_wrapper import BitVMXWrapper


class ExecutionTraceGenerationService:

    @staticmethod
    def elf_file():
        return "plainc.elf"
        # return "zkverifier.elf"

    @staticmethod
    def commitment_file():
        if ExecutionTraceGenerationService.elf_file() == "zkverifier.elf":
            return "./execution_files/instruction_commitment_zk.txt"
        elif ExecutionTraceGenerationService.elf_file() == "plainc.elf":
            return "./execution_files/instruction_commitment.txt"

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.elf_file_name = self.elf_file()
        self.bitvmx_wrapper = BitVMXWrapper(base_path)

    def __call__(self, setup_uuid: str):
        self.bitvmx_wrapper.generate_execution_checkpoints(setup_uuid, self.elf_file_name)
        # return self.execution_trace_parsing_service(
        #     self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", protocol_dict
        # )
