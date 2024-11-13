import re

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)


class ExecutionTraceCommitmentGenerationService:

    def __init__(self, instruction_mapping_path: str):
        self.instruction_mapping_path = instruction_mapping_path

    def __call__(self):
        instruction_commitment_path = ExecutionTraceGenerationService.commitment_file()
        with open(self.instruction_mapping_path) as mapping_file:
            mapping_lines = mapping_file.readlines()

        mapping_dict = {}
        pattern = r'Key:\s*(\w+),\s*Script:\s*"([^"]+)"'
        for line in mapping_lines:
            match = re.search(pattern, line)
            mapping_dict[match.group(1)] = match.group(2)

        with open(instruction_commitment_path) as commitment_file:
            commitment_lines = commitment_file.readlines()

        key_list = []
        instruction_dict = {}
        opcode_dict = {}
        pattern = (
            r"PC:\s*(0x[0-9A-Fa-f]+)\s*Micro:\s*(\d+)\s*Opcode:\s*(0x[0-9A-Fa-f]+)\s*Key:\s*(\w+)"
        )
        commitment_lines = list(
            filter(lambda current_line: current_line[0:3] == "PC:", commitment_lines)
        )
        for line in commitment_lines:
            match = re.search(pattern, line)
            pc = match.group(1)[2:]
            micro = match.group(2).zfill(2)
            # This is not really necessary (we can add the verification)
            # opcode = match.group(3)
            key = match.group(4)
            composed_key = pc + micro
            key_list.append(composed_key)
            instruction_dict[composed_key] = mapping_dict[key]
            opcode_dict[composed_key] = match.group(3)[2:]
        # Just in case, but this should not be necessary since it's ordered in origin
        return key_list, instruction_dict, opcode_dict
