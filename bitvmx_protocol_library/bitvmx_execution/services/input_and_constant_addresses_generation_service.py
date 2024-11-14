import re

from bitvmx_protocol_library.bitvmx_execution.entities.memory_region_dto import (
    InputMemoryRegionDTO,
    MemoryRegionsDTO,
)


class InputAndConstantAddressesGenerationService:
    def __init__(self, instruction_commitment: str):
        self.instruction_commitment = instruction_commitment

    def __call__(self, input_length: int):
        with open(self.instruction_commitment) as mapping_file:
            mapping_lines = mapping_file.readlines()
        input_line = list(filter(lambda x: ".input Start" in x, mapping_lines))[0]
        match = re.search(r"Start:\s+(0x[0-9a-fA-F]+)", input_line)
        init_input_address = match.group(1)[2:]
        constant_lines = list(filter(lambda x: x.startswith("Address:"), mapping_lines))
        constant_memory_regions = {}
        while len(constant_lines) > 0:
            current_line = constant_lines.pop(0)
            match = re.search(
                r"Address:\s+(0x[0-9a-fA-F]+)\s+value:\s+(0x[0-9a-fA-F]+)\n", current_line
            )
            address = match.group(1)[2:]
            value = match.group(2)[2:]
            constant_memory_regions[address] = value
        return MemoryRegionsDTO(
            input=InputMemoryRegionDTO(
                address=init_input_address,
                amount_of_words=input_length,
            ),
            constants=constant_memory_regions,
        )
