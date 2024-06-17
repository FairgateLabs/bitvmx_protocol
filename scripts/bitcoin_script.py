from typing import Any, Optional, Union

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
