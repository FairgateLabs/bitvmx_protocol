import math
import os
import re
import subprocess
from enum import Enum
from typing import Optional

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)


def _tweak_input(input_hex: str):
    return input_hex[:-1] + hex(15 - int(input_hex[-1], 16))[2:]


class ReadErrorType(Enum):
    BEFORE = "before"
    SAME = "same"
    AFTERWARDS = "afterwards"


class ReadErrorPosition(Enum):
    ONE = "one"
    TWO = "two"


class BitVMXWrapper:

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.execution_checkpoint_interval = 50000000
        # self.fail_actor = "verifier"
        self.fail_actor = "prover"
        # self.fail_step = "1234567890"
        # self.fail_step = "1"
        # self.fail_step = "29"
        self.fail_step = None
        # self.fail_type = "--fail-execute"
        self.fail_type = "--fail-hash"
        # self.fail_type = "--fail-pc"
        self.fail_input = False
        self.fail_actor_input = "prover"
        self.contains_fail = (
            self.fail_actor is not None
            and self.fail_actor in self.base_path
            and self.fail_step is not None
            and self.fail_type is not None
        )
        self.contains_input_fail = (
            self.fail_actor_input is not None
            and self.fail_actor_input in self.base_path
            and self.fail_input
        )

        self.fail_read = False
        self.fail_actor_read = "prover"
        # This is the latter one
        # self.fail_read_type = ReadErrorType.BEFORE
        self.fail_read_type = ReadErrorType.SAME
        self.fail_read_position = ReadErrorPosition.ONE
        # DO NOT CHANGE THIS AS OF NOW (WE HARDCODE THE EXAMPLE)
        self.fail_read_step = 16
        # read1_add       4026531872
        # read1_val       3766484992
        # read1_last_step 4
        # read2_add       4026531900
        # read2_val       2852126724
        # read2_last_step 14
        self.contains_read_fail = (
            self.fail_read_type is not None
            and self.fail_read_position is not None
            and self.fail_actor_read in self.base_path
            and self.fail_read
            and self.fail_read_step is not None
        )

    def get_execution_trace(
        self, setup_uuid: str, index: int, input_hex: Optional[str] = None, fail_read=True
    ):
        base_point = (
            math.floor((index - 1) / self.execution_checkpoint_interval)
            * self.execution_checkpoint_interval
        )
        print(
            "Executing command for list "
            + str(index)
            + " with step "
            + str(base_point)
            + " and limit "
            + str(index)
            + " with base 0 index "
            + str(index - 1)
        )
        command = [
            "cargo",
            "run",
            "--manifest-path",
            "../../BitVMX-CPU/Cargo.toml",
            "--release",
            "--bin",
            "emulator",
            "--",
            "execute",
            "--step",
            str(base_point),
            "--list",
            str(index),
            "--trace",
            "--limit",
            str(index),
        ]
        if input_hex is not None:
            command.extend(
                [
                    "--input",
                    _tweak_input(input_hex=input_hex) if self.contains_input_fail else input_hex,
                    "--input-as-little",
                ]
            )
        if self.contains_fail and int(self.fail_step) <= index:
            command.extend([self.fail_type, self.fail_step])

        if self.contains_read_fail and int(self.fail_read_step) <= index and fail_read:
            if self.fail_read_position == ReadErrorPosition.ONE:
                command.append("--fail-read-1")
                command.append(str(self.fail_read_step))
                command.append(str(4026531872))
                command.append(str(3766484992 + 1))
                command.append(str(4026531872))
                base_last_step = 4
            elif self.fail_read_position == ReadErrorPosition.TWO:
                command.append("--fail-read-2")
                command.append(str(self.fail_read_step))
                command.append(str(3766484972))
                command.append(str(2852126724 + 1))
                command.append(str(3766484972))
                base_last_step = 7
            else:
                raise Exception("Fail read not recognized")
            if self.fail_read_type == ReadErrorType.SAME:
                command.append("0" + str(base_last_step))
            elif self.fail_read_type == ReadErrorType.AFTERWARDS:
                command.append("0" + str(base_last_step + 1))
            elif self.fail_read_type == ReadErrorType.BEFORE:
                command.append("0" + str(base_last_step - 1))

        execution_directory = self.base_path + setup_uuid

        try:
            # Run the command in the specified directory
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, cwd=execution_directory
            )
            print("Done executing command")
            execution_trace = result.stdout
            # TODO: remove when bugs are fixed
            try:
                execution_trace = list(filter(lambda x: x != "", execution_trace.split("\n")))[-1]
            except IndexError:
                words_lengths = BitVMXProtocolPropertiesDTO.trace_words_lengths
                words = list(
                    map(
                        lambda x: "f" * x,
                        words_lengths,
                    )
                )
                execution_trace = ";".join(words)
                write_trace = "".join(words[-4:])
                execution_trace += ";" + write_trace
                execution_trace += ";" + "f" * BitVMXProtocolPropertiesDTO.amount_of_nibbles_hash
            return execution_trace

        except subprocess.CalledProcessError as e:
            # Handle errors in execution
            print("An error occurred while running the command.")
            print("Return code:", e.returncode)
            print("Output:\n", e.stdout)
            print("Errors:\n", e.stderr)
            raise Exception("Some problem with the computation")

    def generate_execution_checkpoints(
        self, setup_uuid: str, elf_file: str, input_hex: Optional[str] = None
    ):
        directory = self.base_path + setup_uuid
        pattern = re.compile(r"^checkpoint\.\d+\.json$")

        # List all files in the specified directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        # Filter files that match the pattern
        checkpoint_files = [f for f in files if pattern.match(f)]
        if len(checkpoint_files) == 0:
            command = [
                "cargo",
                "run",
                "--manifest-path",
                "../../BitVMX-CPU/Cargo.toml",
                "--release",
                "--bin",
                "emulator",
                "--",
                "execute",
                "--elf",
                "../../BitVMX-CPU/docker-riscv32/riscv32/build/" + elf_file,
                "--debug",
                "--checkpoints",
            ]
            if input_hex is not None:
                command.extend(
                    [
                        "--input",
                        (
                            _tweak_input(input_hex=input_hex)
                            if self.contains_input_fail
                            else input_hex
                        ),
                        "--input-as-little",
                    ]
                )
            if self.contains_fail:
                command.extend([self.fail_type, self.fail_step])

            if self.contains_read_fail:
                assert self.fail_read_step == 16
                if self.fail_read_position == ReadErrorPosition.ONE:
                    command.append("--fail-read-1")
                    command.append(str(self.fail_read_step))
                    command.append(str(4026531872))
                    command.append(str(3766484992 + 1))
                    command.append(str(4026531872))
                    base_last_step = 4
                elif self.fail_read_position == ReadErrorPosition.TWO:
                    command.append("--fail-read-2")
                    command.append(str(self.fail_read_step))
                    command.append(str(3766484972))
                    command.append(str(2852126720 + 1))
                    command.append(str(3766484972))
                    base_last_step = 7
                else:
                    raise Exception("Fail read not recognized")
                if self.fail_read_type == ReadErrorType.SAME:
                    command.append("0" + str(base_last_step))
                elif self.fail_read_type == ReadErrorType.AFTERWARDS:
                    command.append("0" + str(base_last_step + 1))
                elif self.fail_read_type == ReadErrorType.BEFORE:
                    command.append("0" + str(base_last_step - 1))

            execution_directory = self.base_path + setup_uuid

            try:
                # Run the command in the specified directory
                subprocess.run(
                    command, capture_output=True, text=True, check=True, cwd=execution_directory
                )

            except subprocess.CalledProcessError as e:
                # Handle errors in execution
                print("An error occurred while running the command.")
                print("Return code:", e.returncode)
                print("Output:\n", e.stdout)
                print("Errors:\n", e.stderr)
                raise Exception("Some problem with the computation")
