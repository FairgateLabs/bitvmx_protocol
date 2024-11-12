from typing import List

from pydantic import BaseModel


class ReadExecutionTraceWitnessDTO(BaseModel):
    write_address: List[str]
    write_value: List[str]
    write_PC_address: List[str]
    write_micro: List[str]


class ExecutionTraceWitnessDTO(ReadExecutionTraceWitnessDTO):

    read_1_address: List[str]
    read_1_value: List[str]
    read_1_last_step: List[str]

    read_2_address: List[str]
    read_2_value: List[str]
    read_2_last_step: List[str]

    opcode: List[str]
    read_PC_address: List[str]
    read_micro: List[str]
