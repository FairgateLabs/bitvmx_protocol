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

from scripts.bitcoin_script import BitcoinScript
from winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


def _generate_script_from_key(
    key,
    signature_public_keys,
    public_keys,
    trace_words_lengths,
    bits_per_digit_checksum,
    instruction_dict,
    trace_to_script_mapping,
):
    script = BitcoinScript()
    trace_to_script_mapping = reversed(trace_to_script_mapping)
    max_value = 12
    complementary_trace_to_script_mapping = list(
        map(lambda index: max_value - index, trace_to_script_mapping)
    )

    verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()

    for i in complementary_trace_to_script_mapping:
        verify_input_nibble_message_from_public_keys(
            script,
            public_keys[i],
            trace_words_lengths[i],
            bits_per_digit_checksum,
            to_alt_stack=True,
        )

    total_length = 0
    current_micro = key[-2:]
    current_pc_address = key[:-2]
    for i in reversed(complementary_trace_to_script_mapping):
        current_length = trace_words_lengths[i]
        for j in range(current_length):
            script.append("OP_FROMALTSTACK")

            # MICRO CHECK
            if i == 5:
                script.extend(["OP_DUP", int(current_micro, 16), "OP_NUMEQUALVERIFY"])

            # PC ADDRESS CHECK
            if i == 6:
                script.extend(["OP_DUP", int(current_pc_address[j], 16), "OP_NUMEQUALVERIFY"])

        if current_length == 2:
            script.extend([1, "OP_ROLL", "OP_DROP"])
            total_length += 1
        else:
            total_length += current_length

    execution_script = BitcoinScript.from_raw(scriptrawhex=instruction_dict[key], has_segwit=True)

    script = script + execution_script

    script.extend(
        [PublicKey(hex_str=signature_public_keys[-1]).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
    )

    script.append(1)
    return script


def split_list(input_list):
    if len(input_list) == 1:
        return input_list[0]
    else:
        middle_point = int(2 ** math.ceil(math.log2(len(input_list))) / 2)
        return [
            split_list(input_list[:middle_point]),
            split_list(input_list[middle_point:]),
        ]


def get_tag_hashed_merkle_root(
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

    if not isinstance(splitted_key_list, list):
        current_script = _generate_script_from_key(
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
                    target=get_tag_hashed_merkle_root,
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
                result = get_tag_hashed_merkle_root(
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
                    target=get_tag_hashed_merkle_root,
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
                    target=get_tag_hashed_merkle_root,
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
                left = get_tag_hashed_merkle_root(
                    splitted_key_list[0],
                    signature_public_keys,
                    public_keys,
                    trace_words_lengths,
                    bits_per_digit_checksum,
                    instruction_dict,
                    trace_to_script_mapping,
                    depth + 1,
                )
                right = get_tag_hashed_merkle_root(
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


def get_tree_depth(splitted_key_list):
    depth = 1
    current_list = splitted_key_list
    while isinstance(current_list[0], list):
        depth += 1
        current_list = current_list[0]
    return depth


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
            split_key_list = split_list(self.key_list)
            print("Call parallel hashed merkle root")
            init_time = time()
            merkle_root = get_tag_hashed_merkle_root(
                split_key_list,
                self.signature_public_keys,
                self.public_keys,
                self.trace_words_lengths,
                self.bits_per_digit_checksum,
                self.instruction_dict,
                self.trace_to_script_mapping(),
                0,
            )
            print(
                "End of parallel hashed merkle root in "
                + str((time() - init_time) / 60)
                + " minutes."
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
        script_list = list(
            map(
                lambda key: _generate_script_from_key(
                    key,
                    self.signature_public_keys,
                    self.public_keys,
                    self.trace_words_lengths,
                    self.bits_per_digit_checksum,
                    self.instruction_dict,
                    self.trace_to_script_mapping(),
                ),
                self.key_list,
            )
        )

        leaf_version = bytes([(1 if is_odd else 0) + LEAF_VERSION_TAPSCRIPT])
        pub_key = bytes.fromhex(public_key.to_x_only_hex())

        def traverse_level(level, already_traversed, depth, shared_list=None):
            if isinstance(level, list):
                if len(level) == 1:
                    result = traverse_level(level[0], already_traversed, depth)
                    if shared_list is None:
                        return result
                    else:
                        shared_list[0] = result
                        return
                if len(level) == 2:
                    current_low_values_per_branch = int((2 ** get_tree_depth([level[0]])) / 2)
                    if depth < 4:
                        manager = Manager()
                        new_left_shared_list = manager.list([None])
                        new_right_shared_list = manager.list([None])
                        a_process = Process(
                            target=traverse_level,
                            args=(level[0], already_traversed, depth + 1, new_left_shared_list)
                        )
                        b_process = Process(
                            target=traverse_level,
                            args=(level[1], already_traversed + current_low_values_per_branch, depth + 1, new_right_shared_list)
                        )
                        a_process.start()
                        b_process.start()
                        a_process.join()
                        b_process.join()
                        a = new_left_shared_list[0]
                        b = new_right_shared_list[0]
                    else:
                        a = traverse_level(level[0], already_traversed, depth + 1)
                        b = traverse_level(level[1], already_traversed + current_low_values_per_branch, depth + 1)

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
                result = tapleaf_tagged_hash(level)
                if shared_list is None:
                    return result
                else:
                    shared_list[0] = result
                    return

        merkle_path = traverse_level(split_list(script_list), 0, 0)

        control_block_bytes = leaf_version + pub_key + merkle_path
        return control_block_bytes.hex()

    def __getitem__(self, index):
        return _generate_script_from_key(
            self.key_list[index],
            self.signature_public_keys,
            self.public_keys,
            self.trace_words_lengths,
            self.bits_per_digit_checksum,
            self.instruction_dict,
            self.trace_to_script_mapping(),
        )
