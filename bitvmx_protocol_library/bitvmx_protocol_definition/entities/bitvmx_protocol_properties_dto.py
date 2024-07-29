from pydantic import BaseModel


class BitVMXProtocolPropertiesDTO(BaseModel):
    amount_of_nibbles_hash: int
    amount_of_wrong_step_search_iterations: int
    amount_of_wrong_step_search_hashes_per_iteration: int
    amount_of_bits_wrong_step_search: int
