from typing import List

from pydantic import BaseModel


class SignaturesPostV1Input(BaseModel):
    setup_uuid: str
    trigger_protocol_signature: str
    search_choice_signatures: List[str]
    trigger_execution_signature: str


class SignaturesPostV1Output(BaseModel):
    verifier_hash_result_signature: str
    verifier_search_hash_signatures: List[str]
    verifier_trace_signature: str
    # verifier_execution_challenge_signature: str
