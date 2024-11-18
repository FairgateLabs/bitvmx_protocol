from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_last_hash_equivocation_challenge_script_generator_service import (
    TriggerLastHashEquivocationChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_hash_challenge_script_generator_service import (
    TriggerWrongHashChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_program_counter_challenge_script_generator_service import (
    TriggerWrongProgramCounterChallengeScriptGeneratorService,
)


class BitVMXAbstractHashScriptList(BaseModel, ABC):
    signature_public_keys: List[str]
    trace_words_lengths: List[int]
    amount_of_bits_wrong_step_search: int
    hash_search_public_keys_list: List[List[List[str]]]
    choice_search_prover_public_keys_list: List[List[List[str]]]
    trace_prover_public_keys: List[List[str]]
    hash_result_public_keys: List[str]
    amount_of_nibbles_hash: int
    amount_of_bits_per_digit_checksum: int
    _script_list: Optional[BitcoinScriptList] = None

    @property
    @abstractmethod
    def script_generator_service(self):
        pass

    @property
    def amount_of_base_scripts(self) -> int:
        return (2**self.amount_of_bits_wrong_step_search) - 1

    def script_list(self) -> BitcoinScriptList:
        if self._script_list is not None:
            return self._script_list
        trigger_wrong_hash_challenge_script_generator_service = self.script_generator_service()
        script_list = []
        assert len(self.choice_search_prover_public_keys_list) == len(
            self.hash_search_public_keys_list
        )
        for i in range(0, len(self.choice_search_prover_public_keys_list)):
            suffix_bin = "1" * self.amount_of_bits_wrong_step_search * i
            for j in range(0, self.amount_of_base_scripts):
                prefix_bin = bin(j)[2:].zfill(self.amount_of_bits_wrong_step_search)
                # print("Ended in *1: " + str(int(prefix_bin + suffix_bin, 2)))
                script_list.append(
                    trigger_wrong_hash_challenge_script_generator_service(
                        signature_public_keys=self.signature_public_keys,
                        trace_words_lengths=self.trace_words_lengths,
                        amount_of_bits_wrong_step_search=self.amount_of_bits_wrong_step_search,
                        hash_search_public_keys_list=self.hash_search_public_keys_list,
                        choice_search_prover_public_keys_list=self.choice_search_prover_public_keys_list,
                        trace_prover_public_keys=self.trace_prover_public_keys,
                        hash_result_public_keys=self.hash_result_public_keys,
                        amount_of_nibbles_hash=self.amount_of_nibbles_hash,
                        amount_of_bits_per_digit_checksum=self.amount_of_bits_per_digit_checksum,
                        bin_wrong_choice=prefix_bin + suffix_bin,
                    )
                )
        for i in range(1, len(self.choice_search_prover_public_keys_list)):
            suffix_bin = "0" * self.amount_of_bits_wrong_step_search * i
            for j in range(1, self.amount_of_base_scripts + 1):
                prefix_bin = bin(j)[2:].zfill(self.amount_of_bits_wrong_step_search)
                # print("Ended in *0: " + str(int(prefix_bin + suffix_bin, 2)))
                script_list.append(
                    trigger_wrong_hash_challenge_script_generator_service(
                        signature_public_keys=self.signature_public_keys,
                        trace_words_lengths=self.trace_words_lengths,
                        amount_of_bits_wrong_step_search=self.amount_of_bits_wrong_step_search,
                        hash_search_public_keys_list=self.hash_search_public_keys_list,
                        choice_search_prover_public_keys_list=self.choice_search_prover_public_keys_list,
                        trace_prover_public_keys=self.trace_prover_public_keys,
                        hash_result_public_keys=self.hash_result_public_keys,
                        amount_of_nibbles_hash=self.amount_of_nibbles_hash,
                        amount_of_bits_per_digit_checksum=self.amount_of_bits_per_digit_checksum,
                        bin_wrong_choice=prefix_bin + suffix_bin,
                    )
                )
        # print(
        #     "Value equal to "
        #     + "1" * self.amount_of_bits_wrong_step_search * len(self.hash_search_public_keys_list)
        #     + ": "
        #     + str(
        #         int(
        #             "1"
        #             * self.amount_of_bits_wrong_step_search
        #             * len(self.hash_search_public_keys_list),
        #             2,
        #         )
        #     )
        # )
        script_list.append(
            trigger_wrong_hash_challenge_script_generator_service(
                signature_public_keys=self.signature_public_keys,
                trace_words_lengths=self.trace_words_lengths,
                amount_of_bits_wrong_step_search=self.amount_of_bits_wrong_step_search,
                hash_search_public_keys_list=self.hash_search_public_keys_list,
                choice_search_prover_public_keys_list=self.choice_search_prover_public_keys_list,
                trace_prover_public_keys=self.trace_prover_public_keys,
                hash_result_public_keys=self.hash_result_public_keys,
                amount_of_nibbles_hash=self.amount_of_nibbles_hash,
                amount_of_bits_per_digit_checksum=self.amount_of_bits_per_digit_checksum,
                bin_wrong_choice="1"
                * self.amount_of_bits_wrong_step_search
                * len(self.hash_search_public_keys_list),
            )
        )
        self._script_list = BitcoinScriptList(script_list)
        return self._script_list

    def list_index_from_choice(self, choice: int):
        if choice == 0:
            return 0
        if choice == (
            (2**self.amount_of_bits_wrong_step_search) ** (len(self.hash_search_public_keys_list))
            - 1
        ):
            return self.amount_of_base_scripts * (
                2 * len(self.choice_search_prover_public_keys_list) - 1
            )
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
            index += int(splitted_bin[-1], 2)
            return index
        elif last_char == "0" * self.amount_of_bits_wrong_step_search:
            index = self.amount_of_base_scripts * len(self.hash_search_public_keys_list)
            splitted_bin = splitted_bin[:-1]
            while splitted_bin[-1] == "0" * self.amount_of_bits_wrong_step_search:
                splitted_bin = splitted_bin[:-1]
                index += self.amount_of_base_scripts
            if len(splitted_bin) == 0:
                raise Exception(
                    "We should never get to this point since the 0 is considered at the beginning"
                )
            index += int(splitted_bin[-1], 2)
            return index - 1
        else:
            return int(last_char, 2)

    def __len__(self):
        return (
            self.amount_of_base_scripts * (2 * len(self.choice_search_prover_public_keys_list) - 1)
            + 1
        )

    def __getitem__(self, choice: int) -> List[str]:
        raise NotImplementedError


class BitVMXWrongHashScriptList(BitVMXAbstractHashScriptList):
    @property
    def script_generator_service(self):
        return TriggerWrongHashChallengeScriptGeneratorService


class BitVMXWrongProgramCounterScriptList(BitVMXAbstractHashScriptList):
    @property
    def script_generator_service(self):
        return TriggerWrongProgramCounterChallengeScriptGeneratorService


class BitVMXLastHashEquivocationScriptList(BitVMXAbstractHashScriptList):
    @property
    def script_generator_service(self):
        return TriggerLastHashEquivocationChallengeScriptGeneratorService
