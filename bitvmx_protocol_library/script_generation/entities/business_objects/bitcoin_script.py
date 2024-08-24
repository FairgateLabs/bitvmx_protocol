from typing import Any, List, Optional, Union

from bitcoinutils.keys import PublicKey
from bitcoinutils.script import Script


class BitcoinScript(Script):

    def __init__(self, script: Optional[list[Any]] = None):
        if script is None:
            self.script = []
        else:
            super().__init__(script)

    def __add__(self, _other: Union["BitcoinScript", list[Any], int, str]):
        if isinstance(_other, list):
            return BitcoinScript(self.script + _other)
        elif isinstance(_other, BitcoinScript):
            return BitcoinScript(self.script + _other.script)
        elif isinstance(_other, int) or isinstance(_other, str):
            return BitcoinScript(self.script + [_other])

        raise Exception("Type not supported")

    def __len__(self):
        return len(self.to_bytes())

    def extend(self, instruction_list: list[Any]):
        self.script.extend(instruction_list)

    def append(self, instruction: Any):
        self.script.append(instruction)

    @staticmethod
    def from_raw(scriptrawhex: str, has_segwit: bool = False):
        return BitcoinScript(
            super(BitcoinScript, BitcoinScript)
            .from_raw(scriptrawhex=scriptrawhex, has_segwit=has_segwit)
            .script
        )

    @staticmethod
    def from_int_list(script_list: List[int], has_segwit: bool = False):
        script_hex = ""
        for elem in script_list:
            hex_string = hex(elem)[2:]
            if len(hex_string) == 1:
                hex_string = "0" + hex_string
            script_hex += hex_string
        return BitcoinScript.from_raw(scriptrawhex=script_hex, has_segwit=has_segwit)

    def to_p2sh_script_pub_key(self) -> "Script":
        return BitcoinScript(super().to_p2sh_script_pub_key().script)

    def to_p2wsh_script_pub_key(self) -> "Script":
        return BitcoinScript(super().to_p2wsh_script_pub_key().script)

    def to_scriptwiz(self) -> list[str]:
        return list(
            map(
                lambda val: (
                    val
                    if isinstance(val, str) and val.startswith("OP")
                    else "<0x{}>".format(val) if isinstance(val, str) else "<{}>".format(val)
                ),
                self.script,
            )
        )

    def get_taproot_address(self, public_key: PublicKey):
        return public_key.get_taproot_address([[self]])
