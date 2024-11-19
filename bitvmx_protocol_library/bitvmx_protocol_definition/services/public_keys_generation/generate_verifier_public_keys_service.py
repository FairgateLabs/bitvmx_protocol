from bitcoinutils.keys import PrivateKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)
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

    def __call__(self, bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO):

        halt_step_keys = self.verifier_winternitz_keys_nibbles_service(
            step=2, case=0, n0=bitvmx_protocol_properties_dto.amount_of_nibbles_halt_step
        )
        halt_step_public_keys = list(map(lambda key_list: key_list[-1], halt_step_keys))

        choice_search_verifier_public_keys_list = []
        for iter_count in range(
            bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            current_iteration_keys = []
            current_iteration_keys.append(
                self.verifier_winternitz_keys_single_word_service(
                    step=(3 + iter_count * 2 + 1),
                    case=0,
                    amount_of_bits=bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
                )
            )
            current_iteration_public_keys = []
            for keys_list_of_lists in current_iteration_keys:
                current_iteration_public_keys.append(
                    list(map(lambda key_list: key_list[-1], keys_list_of_lists))
                )

            choice_search_verifier_public_keys_list.append(current_iteration_public_keys)

        trace_words_lengths = bitvmx_protocol_properties_dto.trace_words_lengths[::-1]

        current_step = 3 + 2 * bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
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

        current_step += 2

        choice_read_search_verifier_public_keys_list = []
        for iter_count in range(
            bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            current_iteration_keys = []
            current_iteration_keys.append(
                self.verifier_winternitz_keys_single_word_service(
                    step=current_step + 2 * iter_count + 1,
                    case=0,
                    amount_of_bits=bitvmx_protocol_properties_dto.amount_of_bits_wrong_step_search,
                )
            )
            current_iteration_public_keys = []
            for keys_list_of_lists in current_iteration_keys:
                current_iteration_public_keys.append(
                    list(map(lambda key_list: key_list[-1], keys_list_of_lists))
                )

            choice_read_search_verifier_public_keys_list.append(current_iteration_public_keys)

        current_step += 2 * bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations

        write_trace_words_lengths = bitvmx_protocol_properties_dto.write_trace_words_lengths
        write_trace_words_lengths.reverse()

        read_trace_verifier_keys = []
        for i in range(len(write_trace_words_lengths)):
            read_trace_verifier_keys.append(
                self.verifier_winternitz_keys_nibbles_service(
                    step=current_step, case=i, n0=write_trace_words_lengths[i]
                )
            )
        read_trace_verifier_public_keys = []
        for keys_list_of_lists in read_trace_verifier_keys:
            read_trace_verifier_public_keys.append(
                list(map(lambda key_list: key_list[-1], keys_list_of_lists))
            )

        return BitVMXVerifierWinternitzPublicKeysDTO(
            halt_step_public_keys=halt_step_public_keys,
            choice_search_verifier_public_keys_list=choice_search_verifier_public_keys_list,
            trace_verifier_public_keys=trace_verifier_public_keys,
            choice_read_search_verifier_public_keys_list=choice_read_search_verifier_public_keys_list,
            read_trace_verifier_public_keys=read_trace_verifier_public_keys,
        )
