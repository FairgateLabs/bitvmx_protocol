from typing import List

from pydantic import BaseModel


class HashPublicationWitnessDTO(BaseModel):
    final_hash: List[str]
    halt_step: List[str]
    input: List[List[str]]
