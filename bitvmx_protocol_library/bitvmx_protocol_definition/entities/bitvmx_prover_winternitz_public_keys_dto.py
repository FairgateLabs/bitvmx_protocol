from typing import List

from pydantic import BaseModel


class BitVMXProverWinternitzPublicKeysDTO(BaseModel):
    hash_result_public_keys: List[str]
    hash_search_public_keys_list: List[List[List[str]]]
    choice_search_prover_public_keys_list: List[List[List[str]]]
    trace_prover_public_keys: List[List[str]]
    hash_read_search_public_keys_list: List[List[List[str]]]
    choice_read_search_prover_public_keys_list: List[List[List[str]]]
