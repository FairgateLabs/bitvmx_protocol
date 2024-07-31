import csv
import re

from bitvmx_protocol_library.winternitz_keys_handling.functions.signature_functions import (
    byte_sha256,
)


class ExecutionTraceParsingService:

    def __init__(self, input_file_path: str):
        self.input_file_path = input_file_path

    def __call__(self, output_file_path: str, amount_of_trace_steps: int):
        # Regular expressions to match the different parts of each step
        read_pattern = re.compile(r"TraceRead \{ address: (\d+), value: (\d+), last_step: (\d+) \}")
        read_pc_pattern = re.compile(
            r"TraceReadPC \{ pc: ProgramCounter \{ address: (\d+), micro: (\d+) \}, opcode: (\d+) \}"
        )
        write_step_pattern = re.compile(
            r"TraceStep \{ write_1: TraceWrite \{ address: (\d+), value: (\d+) \}, write_pc: TraceWritePC \{ pc: ProgramCounter \{ address: (\d+), micro: (\d+) \} \} \}"
        )

        result = []

        headers = [
            "read1_address",
            "read1_value",
            "read1_last_step",
            "read2_address",
            "read2_value",
            "read2_last_step",
            "read_pc_address",
            "read_pc_micro",
            "read_pc_opcode",
            "write_address",
            "write_value",
            "write_pc",
            "write_micro",
            "write_trace",
            "step_hash",
        ]

        with open(output_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=";")
            writer.writeheader()
            step_hash = byte_sha256(bytes.fromhex("ff")).hex().zfill(64)

            with open(self.input_file_path, "r") as file:
                i = 0
                while True:
                    step_line = file.readline().strip()
                    ok_line = file.readline().strip()

                    if not step_line or not ok_line:
                        break

                    step_num_match = re.match(r"Step: (\d+)", step_line)
                    if not step_num_match:
                        raise Exception("Wrong step number")

                    reads = read_pattern.findall(ok_line)
                    read_pc = read_pc_pattern.findall(ok_line)
                    write = write_step_pattern.findall(ok_line)

                    read1 = reads[0]
                    read2 = reads[1]
                    read_pc = read_pc[0]
                    write = write[0]

                    # Important to not forget the zfill so the size is as intended
                    write_address_hex = hex(int(write[0]))[2:].zfill(8)
                    write_value_hex = hex(int(write[1]))[2:].zfill(8)
                    write_pc_hex = hex(int(write[2]))[2:].zfill(8)
                    write_micro_hex = hex(int(write[3]))[2:].zfill(2)
                    write_trace = (
                        write_address_hex + write_value_hex + write_pc_hex + write_micro_hex
                    )

                    step_hash = byte_sha256(bytes.fromhex(step_hash + write_trace)).hex().zfill(64)

                    if "prover_files" in output_file_path and i == -1:
                        step_hash = (
                            byte_sha256(bytes.fromhex(step_hash + write_trace)).hex().zfill(64)
                        )

                    step_dict = {
                        "read1_address": read1[0],
                        "read1_value": read1[1],
                        "read1_last_step": read1[2],
                        "read2_address": read2[0],
                        "read2_value": read2[1],
                        "read2_last_step": read2[2],
                        "read_pc_address": read_pc[0],
                        "read_pc_micro": read_pc[1],
                        "read_pc_opcode": read_pc[2],
                        "write_address": write[0],
                        "write_value": write[1],
                        "write_pc": write[2],
                        "write_micro": write[3],
                        "write_trace": write_trace,
                        "step_hash": step_hash,
                    }
                    writer.writerow(step_dict)
                    result.append(step_dict)
                    i += 1
                while i < amount_of_trace_steps:
                    # Important to not forget the zfill so the size is as intended
                    write_address_hex = "f" * 8
                    write_value_hex = "f" * 8
                    write_pc_hex = "f" * 8
                    write_micro_hex = "f" * 2
                    write_trace = (
                        write_address_hex + write_value_hex + write_pc_hex + write_micro_hex
                    )

                    step_dict = {
                        "read1_address": "f" * 8,
                        "read1_value": "f" * 8,
                        "read1_last_step": "f" * 8,
                        "read2_address": "f" * 8,
                        "read2_value": "f" * 8,
                        "read2_last_step": "f" * 8,
                        "read_pc_address": "f" * 8,
                        "read_pc_micro": "f" * 2,
                        "read_pc_opcode": "f" * 8,
                        "write_address": "f" * 8,
                        "write_value": "f" * 8,
                        "write_pc": "f" * 8,
                        "write_micro": "f" * 2,
                        "write_trace": write_trace,
                        "step_hash": step_hash,
                    }
                    writer.writerow(step_dict)
                    result.append(step_dict)
                    i += 1
        if i > amount_of_trace_steps:
            raise Exception("Execution longer than the setup amount of steps")
        return result
