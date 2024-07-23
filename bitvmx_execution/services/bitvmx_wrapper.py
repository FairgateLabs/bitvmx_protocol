import math
import subprocess


class BitVMXWrapper:

    def __init__(self, base_path):
        self.base_path = base_path
        self.execution_checkpoint_interval = 50000000
        self.fail_actor = "prover"
        self.fail_step = "500"

    def get_execution_trace(self, protocol_dict, index):
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
            str(math.floor(index / self.execution_checkpoint_interval)),
            "--list",
            str(index),
            "--trace",
            "--limit",
            str(index),
        ]
        if self.fail_actor is not None and self.fail_actor in self.base_path:
            command.extend(["--fail", self.fail_step])

        execution_directory = self.base_path + protocol_dict["setup_uuid"]

        try:
            # Run the command in the specified directory
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, cwd=execution_directory
            )
            execution_trace = result.stdout
            return execution_trace

        except subprocess.CalledProcessError as e:
            # Handle errors in execution
            print("An error occurred while running the command.")
            print("Return code:", e.returncode)
            print("Output:\n", e.stdout)
            print("Errors:\n", e.stderr)
            raise Exception("Some problem with the computation")

    def generate_execution_checkpoints(self, protocol_dict, elf_file):
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
        if self.fail_actor is not None and self.fail_actor in self.base_path:
            command.extend(["--fail", self.fail_step])
        execution_directory = self.base_path + protocol_dict["setup_uuid"]

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
