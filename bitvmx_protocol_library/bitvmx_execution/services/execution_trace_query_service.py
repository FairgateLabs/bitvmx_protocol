import os
import re
from typing import Optional

import pandas as pd

from bitvmx_protocol_library.bitvmx_execution.services.bitvmx_wrapper import BitVMXWrapper


class ExecutionTraceQueryService:

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.hashes_checkpoint_interval = 1000000
        self.bitvmx_wrapper = BitVMXWrapper(base_path)

    def get_last_step(self, setup_uuid: str):
        directory = self.base_path + setup_uuid
        pattern = re.compile(r"^checkpoint\.\d+\.json$")

        # List all files in the specified directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        # Filter files that match the pattern
        checkpoint_files = [f for f in files if pattern.match(f)]
        checkpoint_indexes = list(map(lambda filename: int(filename[11:-5]), checkpoint_files))
        return max(checkpoint_indexes)

    @staticmethod
    def trace_header():
        return [
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

    def get_overflow_trace(
        self, setup_uuid: str, last_step: int, index: int, input_hex: Optional[str]
    ):
        assert index > last_step
        write_address_hex = "f" * 8
        write_value_hex = "f" * 8
        write_pc_hex = "f" * 8
        write_micro_hex = "f" * 2
        write_trace = write_address_hex + write_value_hex + write_pc_hex + write_micro_hex
        result = self.bitvmx_wrapper.get_execution_trace(
            setup_uuid=setup_uuid, index=last_step, input_hex=input_hex
        )
        step_hash = result.replace("\n", "").split(";")[-1]
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
        return pd.DataFrame([step_dict]).iloc[0]

    def get_step_trace(self, setup_uuid: str, index: int, input_hex: Optional[str]):
        last_step = self.get_last_step(setup_uuid=setup_uuid)
        headers = self.trace_header()
        if index > last_step:
            trace = self.get_overflow_trace(
                setup_uuid=setup_uuid, last_step=last_step, index=index, input_hex=input_hex
            )
            return trace
        else:
            result = self.bitvmx_wrapper.get_execution_trace(
                setup_uuid=setup_uuid, index=index, input_hex=input_hex
            )
            return pd.DataFrame([result.replace("\n", "").split(";")], columns=headers).iloc[0]

    def __call__(self, setup_uuid: str, index: int, input_hex: Optional[str]):
        trace = self.get_step_trace(setup_uuid=setup_uuid, index=index + 1, input_hex=input_hex)
        return trace
