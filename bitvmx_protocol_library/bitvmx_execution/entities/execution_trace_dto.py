from typing import List

import pandas as pd
from pydantic import BaseModel


class ExecutionTraceDTO(BaseModel):

    read_1_address: str
    read_1_value: str
    read_1_last_step: str

    read_2_address: str
    read_2_value: str
    read_2_last_step: str

    opcode: str
    read_PC_address: str
    read_micro: str

    write_address: str
    write_value: str
    write_PC_address: str
    write_micro: str

    @staticmethod
    def not_written_last_step() -> str:
        return "ffffffff"

    @staticmethod
    def halt_opcode() -> int:
        return 115

    @staticmethod
    def halt_read_1_value() -> int:
        return 93

    @staticmethod
    def halt_read_2_value() -> int:
        return 0

    def is_halt(self):
        return (
            (int(self.opcode, 16) == self.halt_opcode())
            and (int(self.read_1_value, 16) == self.halt_read_1_value())
            and (int(self.read_2_value, 16) == self.halt_read_2_value())
        )

    @staticmethod
    def from_trace_values_list(trace_values_list: List[str]) -> "ExecutionTraceDTO":
        reversed_trace_values_list = list(map(lambda x: x[::-1], trace_values_list))
        return ExecutionTraceDTO(
            read_1_address=reversed_trace_values_list[12],
            read_1_value=reversed_trace_values_list[11],
            read_1_last_step=reversed_trace_values_list[10],
            read_2_address=reversed_trace_values_list[9],
            read_2_value=reversed_trace_values_list[8],
            read_2_last_step=reversed_trace_values_list[7],
            read_PC_address=reversed_trace_values_list[6],
            read_micro=reversed_trace_values_list[5],
            opcode=reversed_trace_values_list[4],
            write_address=reversed_trace_values_list[3],
            write_value=reversed_trace_values_list[2],
            write_PC_address=reversed_trace_values_list[1],
            write_micro=reversed_trace_values_list[0],
        )

    @staticmethod
    def from_pandas_series(
        execution_trace: pd.core.series.Series, trace_words_lengths: List[int]
    ) -> "ExecutionTraceDTO":
        trace_values = execution_trace[:13].to_list()
        trace_values.reverse()
        trace_array = []
        for j in range(len(trace_words_lengths)):
            word_length = trace_words_lengths[j]
            trace_array.append(hex(int(trace_values[j]))[2:].zfill(word_length))
        return ExecutionTraceDTO(
            read_1_address=trace_array[12],
            read_1_value=trace_array[11],
            read_1_last_step=trace_array[10],
            read_2_address=trace_array[9],
            read_2_value=trace_array[8],
            read_2_last_step=trace_array[7],
            read_PC_address=trace_array[6],
            read_micro=trace_array[5],
            opcode=trace_array[4],
            write_address=trace_array[3],
            write_value=trace_array[2],
            write_PC_address=trace_array[1],
            write_micro=trace_array[0],
        )
