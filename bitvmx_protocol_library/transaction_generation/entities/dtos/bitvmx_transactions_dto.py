from typing import Any, List

from pydantic import BaseModel


class BitVMXTransactionsDTO(BaseModel):
    funding_tx: Any
    hash_result_tx: Any
    trigger_protocol_tx: Any
    search_hash_tx_list: List[Any]
    search_choice_tx_list: List[Any]
    trace_tx: Any
    trigger_execution_challenge_tx: Any
    execution_challenge_tx: Any
