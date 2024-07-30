from pydantic import BaseModel
from typing import List


class BitVMXProverWinternitzPublicKeysDTO(BaseModel):
    hash_result_public_keys: List[str]
    hash_search_public_keys_list: List[List[List[str]]]
    choice_search_prover_public_keys_list: List[List[List[str]]]
    trace_prover_public_keys: List[List[str]]
