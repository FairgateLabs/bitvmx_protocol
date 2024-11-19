from typing import List

from bitvmx_protocol_library.winternitz_keys_handling.services.compute_max_checksum_service import (
    ComputeMaxChecksumService,
)


def decrypt_first_item(
    witness: List[str],
    amount_of_nibbles: int,
    amount_of_bits_per_digit: int,
    bits_per_digit_checksum: int,
) -> (str, List[str]):
    compute_max_checksum_service = ComputeMaxChecksumService()
    d0 = 2**amount_of_bits_per_digit
    n0 = amount_of_nibbles
    _, n1, _ = compute_max_checksum_service(
        d0=d0, n0=n0, bits_per_digit_checksum=bits_per_digit_checksum
    )
    value = "".join(map(lambda x: "0" if x == "" else x[1], witness[: n0 * 2][1::2]))[::-1]
    remaining_witness = witness[n0 * 2 + n1 * 2 :]
    value_witness = witness[: n0 * 2 + n1 * 2]
    return value, value_witness, remaining_witness
