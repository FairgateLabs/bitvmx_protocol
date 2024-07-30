from typing import List

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
    def from_trace_values_list(trace_values_list: List[str]):
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
