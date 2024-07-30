from bitcoinutils.keys import PrivateKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import (
    BitVMXProverWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_winternitz_keys_nibbles_service import (
    GenerateWinternitzKeysNibblesService,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_winternitz_keys_single_word_service import (
    GenerateWinternitzKeysSingleWordService,
)


class GenerateProverPublicKeysService:

    def __init__(self, private_key: PrivateKey):
        self.prover_winternitz_keys_nibbles_service = GenerateWinternitzKeysNibblesService(
            private_key=private_key
        )
        self.prover_winternitz_keys_single_word_service = GenerateWinternitzKeysSingleWordService(
            private_key=private_key
        )

    def __call__(self, protocol_dict, bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO):

        hash_result_keys = self.prover_winternitz_keys_nibbles_service(
            step=1, case=0, n0=bitvmx_protocol_properties_dto.amount_of_nibbles_hash
        )
        hash_result_public_keys = list(map(lambda key_list: key_list[-1], hash_result_keys))
        # protocol_dict["hash_result_public_keys"] = hash_result_public_keys

        hash_search_public_keys_list = []
        choice_search_prover_public_keys_list = []
        for iter_count in range(
            bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            current_iteration_hash_keys = []

            for word_count in range(
                bitvmx_protocol_properties_dto.amount_of_wrong_step_search_hashes_per_iteration
            ):
                current_iteration_hash_keys.append(
                    self.prover_winternitz_keys_nibbles_service(
                        step=(3 + iter_count * 2),
                        case=word_count,
                        n0=bitvmx_protocol_properties_dto.amount_of_nibbles_hash,
                    )
                )
            current_iteration_hash_public_keys = []
            for keys_list_of_lists in current_iteration_hash_keys:
                current_iteration_hash_public_keys.append(
                    list(map(lambda key_list: key_list[-1], keys_list_of_lists))
                )
            hash_search_public_keys_list.append(current_iteration_hash_public_keys)

            current_iteration_prover_choice_keys = []
            current_iteration_prover_choice_keys.append(
                self.prover_winternitz_keys_single_word_service(
                    step=(3 + iter_count * 2 + 1),
                    case=0,
                    amount_of_bits=bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
                )
            )
            current_iteration_prover_choice_public_keys = []
            for keys_list_of_lists in current_iteration_prover_choice_keys:
                current_iteration_prover_choice_public_keys.append(
                    list(map(lambda key_list: key_list[-1], keys_list_of_lists))
                )
            choice_search_prover_public_keys_list.append(
                current_iteration_prover_choice_public_keys
            )

        # protocol_dict["hash_search_public_keys_list"] = hash_search_public_keys_list
        # protocol_dict["choice_search_prover_public_keys_list"] = (
        #     choice_search_prover_public_keys_list
        # )

        trace_words_lengths = bitvmx_protocol_properties_dto.trace_words_lengths
        trace_words_lengths.reverse()

        # protocol_dict["trace_words_lengths"] = trace_words_lengths

        current_step = 3 + 2 * bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        trace_prover_keys = []
        for i in range(len(trace_words_lengths)):
            trace_prover_keys.append(
                self.prover_winternitz_keys_nibbles_service(
                    step=current_step, case=i, n0=trace_words_lengths[i]
                )
            )
        trace_prover_public_keys = []
        for keys_list_of_lists in trace_prover_keys:
            trace_prover_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )

        # protocol_dict["trace_prover_public_keys"] = trace_prover_public_keys
        return BitVMXProverWinternitzPublicKeysDTO(
            hash_result_public_keys=hash_result_public_keys,
            hash_search_public_keys_list=hash_search_public_keys_list,
            choice_search_prover_public_keys_list=choice_search_prover_public_keys_list,
            trace_prover_public_keys=trace_prover_public_keys,
        )
