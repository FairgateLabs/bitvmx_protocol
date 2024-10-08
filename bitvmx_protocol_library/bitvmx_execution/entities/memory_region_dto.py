from abc import ABC
from typing import List

from pydantic import BaseModel


class MemoryRegionDTO(BaseModel, ABC):
    # We consider words of 32 bits, 4 bytes
    address: str
    amount_of_words: int


class InputMemoryRegionDTO(MemoryRegionDTO):
    pass


class ConstantsMemoryRegionDTO(MemoryRegionDTO):
    values: List[str]


class MemoryRegionsDTO(BaseModel):
    input: InputMemoryRegionDTO
    constants: List[ConstantsMemoryRegionDTO]
