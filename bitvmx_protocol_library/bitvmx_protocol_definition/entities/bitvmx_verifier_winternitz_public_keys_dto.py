from typing import List

from pydantic import BaseModel


class BitVMXVerifierWinternitzPublicKeysDTO(BaseModel):
    halt_step_public_keys: List[str]
    choice_search_verifier_public_keys_list: List[List[List[str]]]
    trace_verifier_public_keys: List[List[str]]
    choice_read_search_verifier_public_keys_list: List[List[List[str]]]
    read_trace_verifier_public_keys: List[List[str]]
