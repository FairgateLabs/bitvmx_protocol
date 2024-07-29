from typing import List

from pydantic import BaseModel


class PublicKeysPostV1Input(BaseModel):
    setup_uuid: str
    seed_destroyed_public_key_hex: str
    prover_public_key: str
    hash_result_public_keys: List[str]
    hash_search_public_keys_list: List[List[List[str]]]
    choice_search_prover_public_keys_list: List[List[List[str]]]
    trace_words_lengths: List[int]
    trace_prover_public_keys: List[List[str]]
    amount_of_wrong_step_search_iterations: int
    amount_of_bits_wrong_step_search: int
    amount_of_bits_per_digit_checksum: int
    funding_amount_satoshis: int
    step_fees_satoshis: int
    funds_tx_id: str
    funds_index: int
    amount_of_nibbles_hash: int
    controlled_prover_address: str


class PublicKeysPostV1Output(BaseModel):
    choice_search_verifier_public_keys_list: List[List[List[str]]]
    verifier_public_key: str
    trace_verifier_public_keys: List[List[str]]
