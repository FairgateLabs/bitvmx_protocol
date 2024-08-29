from typing import List

from pydantic import BaseModel


class BitVMXProverSignaturesDTO(BaseModel):
    trigger_protocol_signature: str
    search_choice_signatures: List[str]
    trigger_execution_challenge_signature: str
    read_search_choice_signatures: List[str]
