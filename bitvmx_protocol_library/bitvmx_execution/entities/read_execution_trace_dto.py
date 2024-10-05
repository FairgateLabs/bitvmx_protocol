from typing import List

from pydantic import BaseModel


class ReadExecutionTraceDTO(BaseModel):

    write_address: str
    write_value: str
    write_PC_address: str
    write_micro: str

    @staticmethod
    def from_trace_values_list(trace_values_list: List[str]):
        reversed_trace_values_list = list(map(lambda x: x[::-1], trace_values_list))
        return ReadExecutionTraceDTO(
            write_address=reversed_trace_values_list[3],
            write_value=reversed_trace_values_list[2],
            write_PC_address=reversed_trace_values_list[1],
            write_micro=reversed_trace_values_list[0],
        )
