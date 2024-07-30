from typing import List, Optional

from pydantic import BaseModel, conint, field_validator


class SetupPostV1Input(BaseModel):
    max_amount_of_steps: int
    amount_of_bits_wrong_step_search: conint(ge=1, le=3)
    verifier_list: Optional[List[str]] = None
    # Debug this field (not that important since the optimal is 4)
    amount_of_bits_per_digit_checksum: Optional[conint(ge=4, le=4)] = 4

    @field_validator("max_amount_of_steps")
    def check_positive_amount_of_steps(cls, max_amount_of_steps):
        if max_amount_of_steps <= 0:
            raise ValueError("amount_of_steps must be a positive integer")
        return max_amount_of_steps


class SetupPostV1Output(BaseModel):
    setup_uuid: str
