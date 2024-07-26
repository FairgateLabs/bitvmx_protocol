import math
from typing import List, Optional, Union

from bitcoinutils.keys import PublicKey

from scripts.bitcoin_script import BitcoinScript


class BitcoinScriptList:

    def __init__(self, init_value: Optional[Union[BitcoinScript, List[BitcoinScript]]] = None):
        if init_value is None:
            self.script_list = []
        elif isinstance(init_value, BitcoinScript):
            self.script_list = [init_value]
        elif isinstance(init_value, list):
            for elem in init_value:
                assert isinstance(elem, BitcoinScript)
            self.script_list = init_value
        else:
            raise Exception("Type not supported")

    def append(self, script: BitcoinScript):
        self.script_list.append(script)

    def extend(self, scripts: List[BitcoinScript]):
        for elem in scripts:
            assert isinstance(elem, BitcoinScript)
        self.script_list.extend(scripts)

    def __getitem__(self, index):
        return self.script_list[index]

    def to_scripts_tree(self):
        if len(self.script_list) == 1:
            return [self.script_list]
        else:

            def split_list(input_list):
                if len(input_list) == 1:
                    return input_list[0]
                else:
                    middle_point = int(2 ** math.ceil(math.log2(len(input_list))) / 2)
                    return [
                        split_list(input_list[:middle_point]),
                        split_list(input_list[middle_point:]),
                    ]

            return split_list(self.script_list)

    def get_taproot_address(self, public_key: PublicKey):
        return public_key.get_taproot_address(self.to_scripts_tree())
