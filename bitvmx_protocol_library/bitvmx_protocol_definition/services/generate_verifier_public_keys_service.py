from bitcoinutils.keys import PrivateKey

from bitvmx_protocol_library.winternitz_keys_handling.services.generate_winternitz_keys_nibbles_service import (
    GenerateWinternitzKeysNibblesService,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_winternitz_keys_single_word_service import (
    GenerateWinternitzKeysSingleWordService,
)


class GenerateVerifierPublicKeysService:

    def __init__(self, private_key: PrivateKey):
        self.verifier_winternitz_keys_single_word_service = GenerateWinternitzKeysSingleWordService(
            private_key=private_key
        )
        self.verifier_winternitz_keys_nibbles_service = GenerateWinternitzKeysNibblesService(
            private_key=private_key
        )

    def __call__(self, protocol_dict):

        amount_of_wrong_step_search_iterations = protocol_dict[
            "amount_of_wrong_step_search_iterations"
        ]
        amount_of_bits_wrong_step_search = protocol_dict["amount_of_bits_wrong_step_search"]

        choice_search_verifier_public_keys_list = []
        for iter_count in range(amount_of_wrong_step_search_iterations):
            current_iteration_keys = []
            current_iteration_keys.append(
                self.verifier_winternitz_keys_single_word_service(
                    step=(3 + iter_count * 2 + 1),
                    case=0,
                    amount_of_bits=amount_of_bits_wrong_step_search,
                )
            )
            current_iteration_public_keys = []
            for keys_list_of_lists in current_iteration_keys:
                current_iteration_public_keys.append(
                    list(map(lambda key_list: key_list[-1], keys_list_of_lists))
                )

            choice_search_verifier_public_keys_list.append(current_iteration_public_keys)

        protocol_dict["choice_search_verifier_public_keys_list"] = (
            choice_search_verifier_public_keys_list
        )

        trace_words_lengths = [8, 8, 8] + [8, 8, 8] + [8, 2, 8] + [8, 8, 8, 2]
        trace_words_lengths.reverse()

        protocol_dict["trace_words_lengths"] = trace_words_lengths

        current_step = 3 + 2 * amount_of_wrong_step_search_iterations
        trace_verifier_keys = []
        for i in range(len(trace_words_lengths)):
            trace_verifier_keys.append(
                self.verifier_winternitz_keys_nibbles_service(
                    step=current_step, case=i, n0=trace_words_lengths[i]
                )
            )
        trace_verifier_public_keys = []
        for keys_list_of_lists in trace_verifier_keys:
            trace_verifier_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )

        protocol_dict["trace_verifier_public_keys"] = trace_verifier_public_keys
