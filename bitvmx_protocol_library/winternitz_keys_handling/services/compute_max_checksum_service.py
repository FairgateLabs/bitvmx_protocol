import math


class ComputeMaxChecksumService:
    def __call__(self, d0: int, n0: int, bits_per_digit_checksum: int):
        max_checksum_value = n0 * (d0 - 1)
        max_checksum_binary_representation = bin(max_checksum_value)[2:]
        n1 = math.ceil(len(max_checksum_binary_representation) / bits_per_digit_checksum)
        if n1 > 1:
            d1 = 2**bits_per_digit_checksum
        else:
            d1 = max_checksum_value + 1
        return d1, n1, max_checksum_value
