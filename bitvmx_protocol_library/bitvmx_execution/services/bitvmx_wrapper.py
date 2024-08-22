import math
import os
import re
import subprocess


class BitVMXWrapper:

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.execution_checkpoint_interval = 50000000
        self.fail_actor = "verifier"
        # self.fail_actor = "prover"
        # self.fail_step = "1234567890"
        self.fail_step = "3"
        # self.fail_step = None
        self.fail_type = "--fail-execute"
        # self.fail_type = "--fail-hash"
        self.contains_fail = (
            self.fail_actor is not None
            and self.fail_actor in self.base_path
            and self.fail_step is not None
            and self.fail_type is not None
        )

    def get_execution_trace(self, setup_uuid: str, index: int):
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
            "../../BitVMX-CPU-Internal/Cargo.toml",
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
        if self.contains_fail:
            command.extend([self.fail_type, self.fail_step])

        execution_directory = self.base_path + setup_uuid

        try:
            # Run the command in the specified directory
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, cwd=execution_directory
            )
            print("Done executing command")
            execution_trace = result.stdout
            return execution_trace

        except subprocess.CalledProcessError as e:
            # Handle errors in execution
            print("An error occurred while running the command.")
            print("Return code:", e.returncode)
            print("Output:\n", e.stdout)
            print("Errors:\n", e.stderr)
            raise Exception("Some problem with the computation")

    def generate_execution_checkpoints(self, setup_uuid: str, elf_file: str):
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
                "../../BitVMX-CPU-Internal/Cargo.toml",
                "--release",
                "--bin",
                "emulator",
                "--",
                "execute",
                "--elf",
                "../../BitVMX-CPU-Internal/docker-riscv32/" + elf_file,
                "--debug",
                "--checkpoints",
            ]
            if self.contains_fail:
                command.extend([self.fail_type, self.fail_step])
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
