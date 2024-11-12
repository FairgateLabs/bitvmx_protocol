import re


class InitialProgramCounterGenerationService:
    def __init__(self, instruction_commitment: str):
        self.instruction_commitment = instruction_commitment

    def __call__(self):
        with open(self.instruction_commitment) as mapping_file:
            mapping_lines = mapping_file.readlines()

        entrypoint_line = list(filter(lambda x: "Entrypoint: " in x, mapping_lines))[0]
        match = re.search(r"Entrypoint:\s+(0x[0-9a-fA-F]+)", entrypoint_line)
        return match.group(1)[2:]
