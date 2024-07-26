import math
from multiprocessing import Manager, Process
from time import time

from bitcoinutils.constants import LEAF_VERSION_TAPSCRIPT
from bitcoinutils.keys import P2trAddress, PublicKey
from bitcoinutils.utils import (
    b_to_i,
    tagged_hash,
    tapbranch_tagged_hash,
    tapleaf_tagged_hash,
    tweak_taproot_pubkey,
)

from bitvmx_protocol_library.script_generation.services.script_generation.execution_challenge_script_from_key_generator_service import (
    ExecutionChallengeScriptFromKeyGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.split_list_for_merkle_tree_service import \
    SplitListForMerkleTreeService


def _get_tag_hashed_merkle_root(
    splitted_key_list,
    signature_public_keys,
    public_keys,
    trace_words_lengths,
    bits_per_digit_checksum,
    instruction_dict,
    trace_to_script_mapping,
    depth,
    shared_list=None,
):

    if not splitted_key_list:
        return b""
    execution_challenge_script_from_key_generator_service = (
        ExecutionChallengeScriptFromKeyGeneratorService()
    )
    if not isinstance(splitted_key_list, list):
        current_script = execution_challenge_script_from_key_generator_service(
            splitted_key_list,
            signature_public_keys,
            public_keys,
            trace_words_lengths,
            bits_per_digit_checksum,
            instruction_dict,
            trace_to_script_mapping,
        )
        return tapleaf_tagged_hash(current_script)
    # list
    else:
        if len(splitted_key_list) == 0:
            return b""
        elif len(splitted_key_list) == 1:
            if depth < 4:
                manager = Manager()
                new_shared_list = manager.list([None])
                process = Process(
                    target=_get_tag_hashed_merkle_root,
                    args=(
                        splitted_key_list[0],
                        signature_public_keys,
                        public_keys,
                        trace_words_lengths,
                        bits_per_digit_checksum,
                        instruction_dict,
                        trace_to_script_mapping,
                        depth + 1,
                        new_shared_list,
                    ),
                )
                process.start()
                process.join()
                result = new_shared_list[0]
            else:
                result = _get_tag_hashed_merkle_root(
                    splitted_key_list[0],
                    signature_public_keys,
                    public_keys,
                    trace_words_lengths,
                    bits_per_digit_checksum,
                    instruction_dict,
                    trace_to_script_mapping,
                    depth + 1,
                )
            if shared_list:
                shared_list[0] = result
            else:
                return result
        elif len(splitted_key_list) == 2:
            if depth < 4:
                manager = Manager()
                new_left_shared_list = manager.list([None])
                new_right_shared_list = manager.list([None])
                left_process = Process(
                    target=_get_tag_hashed_merkle_root,
                    args=(
                        splitted_key_list[0],
                        signature_public_keys,
                        public_keys,
                        trace_words_lengths,
                        bits_per_digit_checksum,
                        instruction_dict,
                        trace_to_script_mapping,
                        depth + 1,
                        new_left_shared_list,
                    ),
                )
                right_process = Process(
                    target=_get_tag_hashed_merkle_root,
                    args=(
                        splitted_key_list[1],
                        signature_public_keys,
                        public_keys,
                        trace_words_lengths,
                        bits_per_digit_checksum,
                        instruction_dict,
                        trace_to_script_mapping,
                        depth + 1,
                        new_right_shared_list,
                    ),
                )
                left_process.start()
                right_process.start()
                left_process.join()
                right_process.join()
                left_result = new_left_shared_list[0]
                right_result = new_right_shared_list[0]
                result = tapbranch_tagged_hash(left_result, right_result)
            else:
                left = _get_tag_hashed_merkle_root(
                    splitted_key_list[0],
                    signature_public_keys,
                    public_keys,
                    trace_words_lengths,
                    bits_per_digit_checksum,
                    instruction_dict,
                    trace_to_script_mapping,
                    depth + 1,
                )
                right = _get_tag_hashed_merkle_root(
                    splitted_key_list[1],
                    signature_public_keys,
                    public_keys,
                    trace_words_lengths,
                    bits_per_digit_checksum,
                    instruction_dict,
                    trace_to_script_mapping,
                    depth + 1,
                )
                result = tapbranch_tagged_hash(left, right)
            if shared_list:
                shared_list[0] = result
            else:
                return result
        else:
            # Raise an error if a branch node contains more than two elements
            raise ValueError("Invalid Merkle branch: List cannot have more than 2 branches.")


def _traverse_level(
    index,
    level,
    already_traversed,
    depth,
    signature_public_keys,
    public_keys,
    trace_words_lengths,
    bits_per_digit_checksum,
    instruction_dict,
    trace_to_script_mapping,
    shared_list=None,
):
    if isinstance(level, list):
        if len(level) == 1:
            result = _traverse_level(
                index,
                level[0],
                already_traversed,
                depth,
                signature_public_keys,
                public_keys,
                trace_words_lengths,
                bits_per_digit_checksum,
                instruction_dict,
                trace_to_script_mapping,
            )
            if shared_list is None:
                return result
            else:
                shared_list[0] = result
                return
        if len(level) == 2:
            current_low_values_per_branch = int(
                (2 ** BitVMXExecutionScriptList.get_tree_depth([level[0]])) / 2
            )
            if depth < 4:
                manager = Manager()
                new_left_shared_list = manager.list([None])
                new_right_shared_list = manager.list([None])
                a_process = Process(
                    target=_traverse_level,
                    args=(
                        index,
                        level[0],
                        already_traversed,
                        depth + 1,
                        signature_public_keys,
                        public_keys,
                        trace_words_lengths,
                        bits_per_digit_checksum,
                        instruction_dict,
                        trace_to_script_mapping,
                        new_left_shared_list,
                    ),
                )
                b_process = Process(
                    target=_traverse_level,
                    args=(
                        index,
                        level[1],
                        already_traversed + current_low_values_per_branch,
                        depth + 1,
                        signature_public_keys,
                        public_keys,
                        trace_words_lengths,
                        bits_per_digit_checksum,
                        instruction_dict,
                        trace_to_script_mapping,
                        new_right_shared_list,
                    ),
                )
                a_process.start()
                b_process.start()
                a_process.join()
                b_process.join()
                a = new_left_shared_list[0]
                b = new_right_shared_list[0]
            else:
                a = _traverse_level(
                    index,
                    level[0],
                    already_traversed,
                    depth + 1,
                    signature_public_keys,
                    public_keys,
                    trace_words_lengths,
                    bits_per_digit_checksum,
                    instruction_dict,
                    trace_to_script_mapping,
                )
                b = _traverse_level(
                    index,
                    level[1],
                    already_traversed + current_low_values_per_branch,
                    depth + 1,
                    signature_public_keys,
                    public_keys,
                    trace_words_lengths,
                    bits_per_digit_checksum,
                    instruction_dict,
                    trace_to_script_mapping,
                )

            if (already_traversed <= index) and (
                index < already_traversed + current_low_values_per_branch
            ):
                result = a + b
                if shared_list is None:
                    return result
                else:
                    shared_list[0] = result
                    return
            if (already_traversed + current_low_values_per_branch <= index) and (
                index < (already_traversed + 2 * current_low_values_per_branch)
            ):
                result = b + a
                if shared_list is None:
                    return result
                else:
                    shared_list[0] = result
                    return
            result = tapbranch_tagged_hash(a, b)
            if shared_list is None:
                return result
            else:
                shared_list[0] = result
                return
        raise ValueError("Invalid Merkle branch: List cannot have more than 2 branches.")
    else:
        if already_traversed == index:
            result = b""
            if shared_list is None:
                return result
            else:
                shared_list[0] = result
                return
        execution_challenge_script_from_key_generator_service = (
            ExecutionChallengeScriptFromKeyGeneratorService()
        )
        result = tapleaf_tagged_hash(
            execution_challenge_script_from_key_generator_service(
                level,
                signature_public_keys,
                public_keys,
                trace_words_lengths,
                bits_per_digit_checksum,
                instruction_dict,
                trace_to_script_mapping,
            )
        )
        if shared_list is None:
            return result
        else:
            shared_list[0] = result
            return


class BitVMXExecutionScriptList:
    def __init__(
        self,
        key_list,
        instruction_dict,
        signature_public_keys,
        public_keys,
        trace_words_lengths,
        bits_per_digit_checksum,
    ):
        self.key_list = key_list
        self.instruction_dict = instruction_dict
        self.signature_public_keys = signature_public_keys
        self.public_keys = public_keys
        self.trace_words_lengths = trace_words_lengths
        self.bits_per_digit_checksum = bits_per_digit_checksum
        self.taproot_address = None

    @staticmethod
    def get_tree_depth(splitted_key_list):
        depth = 1
        current_list = splitted_key_list
        while isinstance(current_list[0], list):
            depth += 1
            current_list = current_list[0]
        return depth

    @staticmethod
    def trace_to_script_mapping():
        return [9, 10, 11, 12, 0, 1, 3, 4, 6, 7, 8]
        # return [9, 10, 11, 12, 3, 4, 0, 1, 6, 7, 8]

    def get_taproot_address(self, public_key: PublicKey):
        if self.taproot_address:
            return self.taproot_address
        key_x = public_key.to_bytes()[:32]
        if len(self.key_list) == 0:
            tweak = tagged_hash(key_x, "TapTweak")
        else:
            split_list_for_merkle_tree_service = SplitListForMerkleTreeService()
            split_key_list = split_list_for_merkle_tree_service(self.key_list)
            print("Call parallel hashed merkle root")
            init_time = time()
            merkle_root = _get_tag_hashed_merkle_root(
                split_key_list,
                self.signature_public_keys,
                self.public_keys,
                self.trace_words_lengths,
                self.bits_per_digit_checksum,
                self.instruction_dict,
                self.trace_to_script_mapping(),
                0,
            )
            end_time = time()
            if end_time - init_time > 60:
                print(
                    "End of parallel hashed merkle root in "
                    + str((time() - init_time) / 60)
                    + " minutes."
                )
            else:
                print(
                    "End of parallel hashed merkle root in " + str(time() - init_time) + " seconds."
                )
            tweak = tagged_hash(key_x + merkle_root, "TapTweak")

        tweak_int = b_to_i(tweak)

        # keep x-only coordinate
        tweak_and_odd = tweak_taproot_pubkey(public_key.key.to_string(), tweak_int)
        pubkey = tweak_and_odd[0][:32]
        is_odd = tweak_and_odd[1]
        self.taproot_address = P2trAddress(witness_program=pubkey.hex(), is_odd=is_odd)
        return self.taproot_address

    def get_control_block_hex(self, public_key: PublicKey, index: int, is_odd: bool):

        leaf_version = bytes([(1 if is_odd else 0) + LEAF_VERSION_TAPSCRIPT])
        pub_key = bytes.fromhex(public_key.to_x_only_hex())

        init_time = time()
        split_list_for_merkle_tree_service = SplitListForMerkleTreeService()
        print("Start control block computation")
        merkle_path = _traverse_level(
            index,
            split_list_for_merkle_tree_service(self.key_list),
            0,
            0,
            self.signature_public_keys,
            self.public_keys,
            self.trace_words_lengths,
            self.bits_per_digit_checksum,
            self.instruction_dict,
            self.trace_to_script_mapping(),
        )
        print("End of control block computation in " + str(time() - init_time) + " seconds.")

        control_block_bytes = leaf_version + pub_key + merkle_path
        return control_block_bytes.hex()

    def __getitem__(self, index):
        execution_challenge_script_from_key_generator_service = (
            ExecutionChallengeScriptFromKeyGeneratorService()
        )
        return execution_challenge_script_from_key_generator_service(
            self.key_list[index],
            self.signature_public_keys,
            self.public_keys,
            self.trace_words_lengths,
            self.bits_per_digit_checksum,
            self.instruction_dict,
            self.trace_to_script_mapping(),
        )
