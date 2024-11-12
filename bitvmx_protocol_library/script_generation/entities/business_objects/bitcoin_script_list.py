from multiprocessing import Manager, Process
from multiprocessing.managers import ListProxy
from typing import List, Optional, Union

from bitcoinutils.keys import P2trAddress, PublicKey
from bitcoinutils.utils import (
    b_to_i,
    tagged_hash,
    tapbranch_tagged_hash,
    tapleaf_tagged_hash,
    tweak_taproot_pubkey,
)

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.script_generation.services.split_list_for_merkle_tree_service import (
    SplitListForMerkleTreeService,
)


def _get_tag_hashed_merkle_root(
    splitted_key_list: Union[List, BitcoinScript],
    depth: int,
    shared_list: Optional[ListProxy] = None,
):

    if not splitted_key_list:
        return b""
    if isinstance(splitted_key_list, BitcoinScript):
        result = tapleaf_tagged_hash(splitted_key_list)
        if shared_list:
            shared_list[0] = result
        else:
            return result
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
                        depth + 1,
                        new_left_shared_list,
                    ),
                )
                right_process = Process(
                    target=_get_tag_hashed_merkle_root,
                    args=(
                        splitted_key_list[1],
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
                    depth + 1,
                )
                right = _get_tag_hashed_merkle_root(
                    splitted_key_list[1],
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


class BitcoinScriptList:

    def __init__(self, script_list: Optional[Union[BitcoinScript, List[BitcoinScript]]] = None):
        if script_list is None:
            self.script_list = []
        elif isinstance(script_list, BitcoinScript):
            self.script_list = [script_list]
        elif isinstance(script_list, list):
            for elem in script_list:
                assert isinstance(elem, BitcoinScript)
            self.script_list = script_list
        else:
            raise Exception("Type not supported")

    def append(self, script: BitcoinScript):
        self.script_list.append(script)

    def extend(self, scripts: List[BitcoinScript]):
        for elem in scripts:
            assert isinstance(elem, BitcoinScript)
        self.script_list.extend(scripts)

    def __getitem__(self, index: int):
        return self.script_list[index]

    def __add__(self, other: Union["BitcoinScriptList", BitcoinScript]) -> "BitcoinScriptList":
        assert isinstance(other, BitcoinScriptList) or isinstance(other, BitcoinScript)
        if isinstance(other, BitcoinScript):
            script_list_copy = self.script_list.copy()
            script_list_copy.append(other)
            return BitcoinScriptList(script_list_copy)
        elif isinstance(other, BitcoinScriptList):
            return BitcoinScriptList(self.script_list + other.script_list)
        raise Exception("Type not supported")

    def __len__(self):
        return len(self.script_list)

    def to_scripts_tree(self):
        if len(self.script_list) == 1:
            return [self.script_list]
        else:
            split_list_for_merkle_tree_service = SplitListForMerkleTreeService()
            return split_list_for_merkle_tree_service(self.script_list)

    def get_taproot_address(self, public_key: PublicKey) -> P2trAddress:
        key_x = public_key.to_bytes()[:32]
        if len(self.script_list) == 0:
            tweak = tagged_hash(key_x, "TapTweak")
        else:
            merkle_root = _get_tag_hashed_merkle_root(
                self.to_scripts_tree(),
                0,
            )
            tweak = tagged_hash(key_x + merkle_root, "TapTweak")

        tweak_int = b_to_i(tweak)

        # keep x-only coordinate
        tweak_and_odd = tweak_taproot_pubkey(public_key.key.to_string(), tweak_int)
        pubkey = tweak_and_odd[0][:32]
        is_odd = tweak_and_odd[1]
        return P2trAddress(witness_program=pubkey.hex(), is_odd=is_odd)
