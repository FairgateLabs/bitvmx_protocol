from abc import ABC
from typing import Dict, List

from pydantic import BaseModel


class MemoryRegionDTO(BaseModel, ABC):
    # We consider words of 32 bits, 4 bytes
    address: str
    amount_of_words: int

    @property
    def init(self):
        return self.address

    @property
    def end(self):
        raise NotImplementedError


class InputMemoryRegionDTO(MemoryRegionDTO):
    pass


class ConstantsMemoryRegionDTO(MemoryRegionDTO):
    values: List[str]


class MemoryRegionsDTO(BaseModel):
    input: InputMemoryRegionDTO
    constants: Dict[str, str]

    def memory_regions(self) -> List[MemoryRegionDTO]:
        memory_regions_list = []
        memory_regions_list.append(self.input)
        raise NotImplementedError
