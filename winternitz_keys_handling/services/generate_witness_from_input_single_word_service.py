from winternitz_keys_handling.services.compute_max_checksum_service import ComputeMaxChecksumService
from winternitz_keys_handling.services.generate_winternitz_keys_single_word_service import (
    GenerateWinternitzKeysSingleWordService,
)


class GenerateWitnessFromInputSingleWordService:

    def __init__(self, secret_key):
        self.compute_max_checksum_service = ComputeMaxChecksumService()
        self.generate_winternitz_keys_single_word_service = GenerateWinternitzKeysSingleWordService(
            secret_key
        )

    def __call__(
        self,
        step: int,
        case: int,
        input_number: int,
        amount_of_bits,
    ):

        d0 = 2**4
        n0 = 1
        max_checksum_value = 2**amount_of_bits - 1
        checksum_digit = max_checksum_value - input_number
        current_keys = self.generate_winternitz_keys_single_word_service(step, case, amount_of_bits)
        input_keys = current_keys[1]
        checksum_keys = current_keys[0]
        # checksum_keys.reverse()
        witness = []
        current_digit = input_number
        current_private_key = input_keys[current_digit]
        witness.append(current_private_key)
        witness.append(hex(current_digit)[2:].zfill(2) if current_digit > 0 else "")

        current_digit = checksum_digit
        current_private_key = checksum_keys[current_digit]
        witness.append(current_private_key)
        witness.append(hex(current_digit)[2:].zfill(2) if current_digit > 0 else "")

        return witness
