import json
import os
import re

import pandas as pd

from bitvmx_execution.services.bitvmx_wrapper import BitVMXWrapper
from winternitz_keys_handling.functions.signature_functions import byte_sha256


class ExecutionTraceQueryService:

    def __init__(self, base_path):
        self.base_path = base_path
        self.hashes_checkpoing_interval = 100
        self.bitvmx_wrapper = BitVMXWrapper(base_path)

    def get_last_step(self, protocol_dict):
        directory = self.base_path + protocol_dict["setup_uuid"]
        pattern = re.compile(r"^checkpoint\.\d+\.json$")

        # List all files in the specified directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        # Filter files that match the pattern
        checkpoint_files = [f for f in files if pattern.match(f)]

        greater_file = max(checkpoint_files)
        pattern = re.compile(r"^checkpoint\.(\d+)\.json$")
        match = pattern.search(greater_file)
        last_step_number = int(match.group(1))
        return last_step_number

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

    def get_checkpoint_hashes(self, protocol_dict, last_step):
        checkpoint_hashes_filepath = (
            self.base_path + protocol_dict["setup_uuid"] + "/checkpoint_hashes.json"
        )
        if os.path.isfile(checkpoint_hashes_filepath):
            with open(checkpoint_hashes_filepath, "r") as f:
                return json.load(f)
        else:
            result = self.bitvmx_wrapper.get_execution_trace(protocol_dict, last_step)

            checkpoint_json = {}
            max_index = protocol_dict["amount_of_trace_steps"]
            i = last_step
            step_hash = result.replace("\n", "").split(";")[-1]
            write_address_hex = "f" * 8
            write_value_hex = "f" * 8
            write_pc_hex = "f" * 8
            write_micro_hex = "f" * 2
            write_trace = write_address_hex + write_value_hex + write_pc_hex + write_micro_hex
            checkpoint_json[last_step] = step_hash
            while i < max_index:
                i += 1
                step_hash = byte_sha256(bytes.fromhex(step_hash + write_trace)).hex().zfill(64)
                if i % self.hashes_checkpoing_interval == 0:
                    checkpoint_json[i] = step_hash
            checkpoint_json[max_index] = step_hash
            with open(checkpoint_hashes_filepath, "w") as f:
                json.dump(checkpoint_json, f)
            return checkpoint_json

    def get_overflow_trace(self, protocol_dict, last_step, index):
        assert index > last_step
        checkpoint_hashes = self.get_checkpoint_hashes(protocol_dict, last_step)
        # This can be highly optimized by returning the orderd list but it's not critical
        best_key = -1
        for key in checkpoint_hashes.keys():
            current_key = int(key)
            if (current_key <= index) and (current_key > int(best_key)):
                best_key = key
        step_hash = checkpoint_hashes[best_key]
        i = int(best_key)
        write_address_hex = "f" * 8
        write_value_hex = "f" * 8
        write_pc_hex = "f" * 8
        write_micro_hex = "f" * 2
        write_trace = write_address_hex + write_value_hex + write_pc_hex + write_micro_hex
        while i < index:
            i += 1
            step_hash = byte_sha256(bytes.fromhex(step_hash + write_trace)).hex().zfill(64)

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

    def get_step_trace(self, protocol_dict, index):
        last_step = self.get_last_step(protocol_dict)
        headers = self.trace_header()
        if index > last_step:
            trace = self.get_overflow_trace(protocol_dict, last_step, index)
            return trace
        else:
            result = self.bitvmx_wrapper.get_execution_trace(protocol_dict, index)
            return pd.DataFrame([result.replace("\n", "").split(";")], columns=headers).iloc[0]

    def __call__(self, protocol_dict, index):
        trace = self.get_step_trace(protocol_dict, index + 1)
        # trace_df = pd.read_csv(
        #     self.base_path + protocol_dict["setup_uuid"] + "/execution_trace.csv", sep=";"
        # )
        # return trace_df.iloc[index]
        return trace
