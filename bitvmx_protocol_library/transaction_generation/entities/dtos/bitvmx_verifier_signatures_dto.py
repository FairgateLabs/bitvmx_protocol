from typing import List

from pydantic import BaseModel


class BitVMXVerifierSignaturesDTO(BaseModel):
    hash_result_signature: str
    search_hash_signatures: List[str]
    trace_signature: str
    read_search_hash_signatures: List[str]
    read_trace_signature: str
