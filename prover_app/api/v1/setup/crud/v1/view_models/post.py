from typing import List, Optional

from pydantic import BaseModel, conint, field_validator


class SetupPostV1Input(BaseModel):
    max_amount_of_steps: conint(ge=0, le=2**32)
    amount_of_bits_wrong_step_search: conint(ge=1, le=3)
    funding_tx_id: str
    funding_index: int
    secret_origin_of_funds: str
    verifier_list: Optional[List[str]] = None
    # Debug this field (not that important since the optimal is 4)
    amount_of_bits_per_digit_checksum: Optional[conint(ge=4, le=4)] = 4
    prover_destination_address: str
    prover_signature_private_key: str
    prover_signature_public_key: str
    amount_of_input_words: conint(ge=0)

    @field_validator("max_amount_of_steps")
    def check_positive_amount_of_steps(cls, max_amount_of_steps):
        if max_amount_of_steps <= 0:
            raise ValueError("amount_of_steps must be a positive integer")
        return max_amount_of_steps


class SetupPostV1Output(BaseModel):
    setup_uuid: str
