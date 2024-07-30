import math

from pydantic import BaseModel

from bitvmx_protocol_library.winternitz_keys_handling.services.compute_max_checksum_service import (
    ComputeMaxChecksumService,
)


class BitVMXProtocolPropertiesDTO(BaseModel):
    max_amount_of_steps: int
    amount_of_bits_wrong_step_search: int
    amount_of_bits_per_digit_checksum: int
    amount_of_nibbles_hash_with_checksum: int = None

    def __init__(self, **data):
        super().__init__(**data)
        compute_max_checksum_service = ComputeMaxChecksumService()
        n0 = self.amount_of_nibbles_hash
        d1, n1, max_checksum_value = compute_max_checksum_service(
            d0=self.d0,
            n0=n0,
            bits_per_digit_checksum=self.amount_of_bits_per_digit_checksum,
        )
        self.amount_of_nibbles_hash_with_checksum = n0 + n1

    # Compute this depending on the hash algorithm, now only SHA 256 is available
    @property
    def amount_of_nibbles_hash(self) -> int:
        return 64

    @property
    def d0(self) -> int:
        return 2**self.amount_of_bits_per_digit

    @property
    def amount_of_bits_per_digit(self):
        return 4

    @property
    def amount_of_wrong_step_search_hashes_per_iteration(self) -> int:
        return 2**self.amount_of_bits_wrong_step_search - 1

    @property
    def amount_of_wrong_step_search_iterations(self):
        return math.ceil(
            math.ceil(math.log2(self.max_amount_of_steps)) / self.amount_of_bits_wrong_step_search
        )

    @property
    def trace_words_lengths(self):
        # Read 1, Read 2, Read PC, Write 1, Write PC
        return [8, 8, 8] + [8, 8, 8] + [8, 2, 8] + [8, 8] + [8, 2]

    @property
    def amount_of_trace_steps(self):
        return 2**self.amount_of_bits_wrong_step_search**self.amount_of_wrong_step_search_iterations
