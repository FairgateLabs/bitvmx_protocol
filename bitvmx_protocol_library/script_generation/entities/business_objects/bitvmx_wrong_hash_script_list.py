from typing import List, Optional

from bitcoinutils.keys import PublicKey
from pydantic import BaseModel

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_hash_challenge_script_generator_service import (
    TriggerWrongHashChallengeScriptGeneratorService,
)


class BitVMXWrongHashScriptList(BaseModel):
    signature_public_keys: List[str]
    trace_words_lengths: List[int]
    amount_of_bits_wrong_step_search: int
    hash_search_public_keys_list: List[List[List[str]]]
    choice_search_prover_public_keys_list: List[List[List[str]]]
    trace_prover_public_keys: List[List[str]]
    amount_of_nibbles_hash: int
    amount_of_bits_per_digit_checksum: int
    _script_list: Optional[BitcoinScriptList] = None

    @property
    def amount_of_base_scripts(self) -> int:
        return (2**self.amount_of_bits_wrong_step_search) - 1

    def script_list(self) -> BitcoinScriptList:
        if self._script_list is not None:
            return self._script_list
        trigger_wrong_hash_challenge_script_generator_service = (
            TriggerWrongHashChallengeScriptGeneratorService()
        )
        script_list = []
        assert len(self.choice_search_prover_public_keys_list) == len(
            self.hash_search_public_keys_list
        )
        for i in range(0, len(self.choice_search_prover_public_keys_list)):
            suffix_bin = "1" * self.amount_of_bits_wrong_step_search * i
            for j in range(0, self.amount_of_base_scripts):
                prefix_bin = bin(j)[2:].zfill(self.amount_of_bits_wrong_step_search)
                print(int(prefix_bin + suffix_bin, 2))
                script_list.append(
                    trigger_wrong_hash_challenge_script_generator_service(
                        signature_public_keys=self.signature_public_keys,
                        trace_words_lengths=self.trace_words_lengths,
                        amount_of_bits_wrong_step_search=self.amount_of_bits_wrong_step_search,
                        hash_search_public_keys_list=self.hash_search_public_keys_list,
                        choice_search_prover_public_keys_list=self.choice_search_prover_public_keys_list,
                        trace_prover_public_keys=self.trace_prover_public_keys,
                        amount_of_nibbles_hash=self.amount_of_nibbles_hash,
                        amount_of_bits_per_digit_checksum=self.amount_of_bits_per_digit_checksum,
                        bin_wrong_choice=prefix_bin + suffix_bin,
                    )
                )
        self._script_list = BitcoinScriptList(script_list)
        return self._script_list

    def get_control_block_hex(self, public_key: PublicKey, index: int, is_odd: bool) -> str:
        raise NotImplementedError

    def list_index_from_choice(self, choice: int):
        if choice == 0:
            return 0
        bin_choice = bin(choice)[2:].zfill(
            len(self.hash_search_public_keys_list) * self.amount_of_bits_wrong_step_search
        )
        splitted_bin = [
            bin_choice[i : i + self.amount_of_bits_wrong_step_search]
            for i in range(0, len(bin_choice), self.amount_of_bits_wrong_step_search)
        ]
        last_char = splitted_bin[-1]
        if last_char == "1" * self.amount_of_bits_wrong_step_search:
            index = 0
            while splitted_bin[-1] == "1" * self.amount_of_bits_wrong_step_search:
                splitted_bin = splitted_bin[:-1]
                index += self.amount_of_base_scripts
            if len(splitted_bin) == 0:
                # This case corresponds to the one where all bits are 1
                raise NotImplementedError
            index += int(splitted_bin[-1], 2)
            return index
        elif last_char == "0" * self.amount_of_bits_wrong_step_search:
            raise NotImplementedError
        else:
            return int(last_char, 2)

    def __getitem__(self, choice: int) -> List[str]:
        raise NotImplementedError
