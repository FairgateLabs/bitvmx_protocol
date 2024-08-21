from typing import List

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
    trace_prover_public_keys: List[List[str]]
    amount_of_nibbles_hash: int
    amount_of_bits_per_digit_checksum: int

    @property
    def amount_of_base_scripts(self) -> int:
        return (2**self.amount_of_bits_wrong_step_search) - 2

    def script_list(self) -> BitcoinScriptList:
        trigger_wrong_hash_challenge_script_generator_service = (
            TriggerWrongHashChallengeScriptGeneratorService()
        )
        script_list = []
        for i in range(1, self.amount_of_base_scripts + 1):
            script_list.append(
                trigger_wrong_hash_challenge_script_generator_service(
                    signature_public_keys=self.signature_public_keys,
                    trace_words_lengths=self.trace_words_lengths,
                    amount_of_bits_wrong_step_search=self.amount_of_bits_wrong_step_search,
                    hash_search_public_keys_list=self.hash_search_public_keys_list,
                    trace_prover_public_keys=self.trace_prover_public_keys,
                    amount_of_nibbles_hash=self.amount_of_nibbles_hash,
                    amount_of_bits_per_digit_checksum=self.amount_of_bits_per_digit_checksum,
                    choice=i,
                )
            )
        return BitcoinScriptList(script_list)

    def get_control_block_hex(self, public_key: PublicKey, index: int, is_odd: bool) -> str:
        raise NotImplementedError

    def list_index_from_choice(self, choice: int):
        bin_choice = bin(choice)[2:].zfill(
            len(self.hash_search_public_keys_list) * self.amount_of_bits_wrong_step_search
        )
        splitted_bin = [
            bin_choice[i : i + self.amount_of_bits_wrong_step_search]
            for i in range(0, len(bin_choice), self.amount_of_bits_wrong_step_search)
        ]
        last_char = splitted_bin[-1]
        if last_char == "1" * self.amount_of_bits_wrong_step_search:
            raise NotImplementedError
        elif last_char == "0" * self.amount_of_bits_wrong_step_search:
            raise NotImplementedError
        else:
            return int(last_char, 2) - 1

    def __getitem__(self, choice: int) -> List[str]:
        raise NotImplementedError
