import math
from datetime import timedelta
from typing import ClassVar, List

from pydantic import BaseModel

from bitvmx_protocol_library.classproperty import classproperty
from bitvmx_protocol_library.winternitz_keys_handling.services.compute_max_checksum_service import (
    ComputeMaxChecksumService,
)


class BitVMXProtocolPropertiesDTO(BaseModel):
    max_amount_of_steps: int
    amount_of_input_words: int
    amount_of_bits_wrong_step_search: int
    amount_of_bits_per_digit_checksum: int
    amount_of_nibbles_hash_with_checksum: int = None

    trace_words_lengths: ClassVar[List[int]]
    write_trace_words_lengths: ClassVar[List[int]]
    read_1_address_position: ClassVar[int]
    read_1_value_position: ClassVar[int]
    read_1_last_step_position: ClassVar[int]
    read_2_address_position: ClassVar[int]
    read_2_value_position: ClassVar[int]
    read_2_last_step_position: ClassVar[int]
    read_pc_address_position: ClassVar[int]
    read_pc_micro_position: ClassVar[int]
    read_pc_opcode_position: ClassVar[int]
    write_address_position: ClassVar[int]
    write_value_position: ClassVar[int]
    write_pc_address_position: ClassVar[int]
    write_pc_micro_position: ClassVar[int]
    read_write_address_position: ClassVar[int]
    read_write_value_position: ClassVar[int]
    read_write_pc_address_position: ClassVar[int]
    read_write_pc_micro_position: ClassVar[int]
    amount_of_nibbles_input_word: ClassVar[int]
    amount_of_nibbles_hash: ClassVar[int]
    amount_of_bytes_halt_step: ClassVar[int]

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
    @classproperty
    def amount_of_nibbles_hash(self) -> int:
        return 64

    @property
    def timeout_wait_time(self) -> timedelta:
        months = 0
        weeks = 2
        days = 0
        hours = 0
        minutes = 0
        return timedelta(days=(months * 30) + (weeks * 7) + days, hours=hours, minutes=minutes)

    @classproperty
    def amount_of_bytes_halt_step(self) -> int:
        return 4

    @property
    def amount_of_nibbles_halt_step(self) -> int:
        return self.amount_of_bytes_halt_step * 2

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

    @classproperty
    def trace_words_lengths(self):
        # Read 1, Read 2, Read PC, Write 1, Write PC
        return [8, 8, 8] + [8, 8, 8] + [8, 2, 8] + [8, 8] + [8, 2]

    @classproperty
    def write_trace_words_lengths(self):
        # Write 1, Write PC
        return [8, 8] + [8, 2]

    @classproperty
    def read_1_address_position(self):
        return 0

    @classproperty
    def read_1_value_position(self):
        return 1

    @classproperty
    def read_1_last_step_position(self):
        return 2

    @classproperty
    def read_2_address_position(self):
        return 3

    @classproperty
    def read_2_value_position(self):
        return 4

    @classproperty
    def read_2_last_step_position(self):
        return 5

    @classproperty
    def read_pc_address_position(self):
        return 6

    @classproperty
    def read_pc_micro_position(self):
        return 7

    @classproperty
    def read_pc_opcode_position(self):
        return 8

    @classproperty
    def write_address_position(self):
        return 9

    @classproperty
    def write_value_position(self):
        return 10

    @classproperty
    def write_pc_address_position(self):
        return 11

    @classproperty
    def write_pc_micro_position(self):
        return 12

    @classproperty
    def read_write_address_position(self):
        return 0

    @classproperty
    def read_write_value_position(self):
        return 1

    @classproperty
    def read_write_pc_address_position(self):
        return 2

    @classproperty
    def read_write_pc_micro_position(self):
        return 3

    @classproperty
    def amount_of_nibbles_input_word(self):
        return 8

    @property
    def amount_of_trace_steps(self):
        return (
            2**self.amount_of_bits_wrong_step_search
        ) ** self.amount_of_wrong_step_search_iterations
