from abc import ABC
from typing import Dict, List

from pydantic import BaseModel


class MemoryRegionDTO(BaseModel, ABC):
    # We consider words of 32 bits, 4 bytes
    address: str

    @property
    def init(self):
        return self.address

    @property
    def end(self):
        return hex(int(self.init, 16) + (self.amount_of_words - 1) * 4)[2:]


class InputMemoryRegionDTO(MemoryRegionDTO):
    amount_of_words: int


class ConstantsMemoryRegionDTO(MemoryRegionDTO):
    values: List[str]

    @property
    def amount_of_words(self):
        return len(self.values)


class MemoryRegionsDTO(BaseModel):
    input: InputMemoryRegionDTO
    constants: Dict[str, str]

    def memory_regions(self) -> List[MemoryRegionDTO]:
        memory_regions_list = []
        memory_regions_list.append(self.input)
        constants_keys = list(sorted(self.constants.keys()))
        for i in range(len(constants_keys)):
            current_address = constants_keys[i]
            if (int(memory_regions_list[-1].end, 16) + 4) == int(current_address, 16):
                memory_regions_list[-1].values.append(self.constants[current_address])
            else:
                memory_regions_list.append(
                    ConstantsMemoryRegionDTO(
                        address=current_address, values=[self.constants[current_address]]
                    )
                )
        return memory_regions_list
