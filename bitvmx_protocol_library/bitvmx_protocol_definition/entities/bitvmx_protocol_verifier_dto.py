from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_serializer

from bitvmx_protocol_library.bitvmx_execution.entities.execution_trace_dto import ExecutionTraceDTO
from bitvmx_protocol_library.bitvmx_execution.entities.read_execution_trace_dto import (
    ReadExecutionTraceDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType


class BitVMXProtocolVerifierDTO(BaseModel):
    prover_public_key: str
    verifier_public_keys: Dict[str, str]
    prover_signatures_dto: BitVMXProverSignaturesDTO
    verifier_signatures_dtos: Dict[str, BitVMXProverSignaturesDTO]
    last_confirmed_step: Optional[TransactionVerifierStepType] = None
    last_confirmed_step_tx_id: Optional[str] = None
    search_choices: List[int] = Field(default_factory=list)
    read_search_choices: List[int] = Field(default_factory=list)
    published_hashes_dict: Dict[int, str] = Field(default_factory=dict)
    published_read_hashes_dict: Dict[int, str] = Field(default_factory=dict)
    prover_trace_witness: Optional[List[str]] = None
    prover_read_trace_witness: Optional[List[str]] = None
    published_execution_trace: Optional[ExecutionTraceDTO] = None
    published_read_execution_trace: Optional[ReadExecutionTraceDTO] = None
    real_execution_trace: Optional[ExecutionTraceDTO] = None
    first_wrong_step: Optional[int] = None
    read_revealed_step: Optional[int] = None
    read_search_target: Optional[int] = None
    input_hex: Optional[str] = None
    published_halt_step: Optional[str] = None
    published_halt_hash: Optional[str] = None

    @field_serializer("last_confirmed_step", when_used="always")
    def serialize_last_confirmed_step(
        last_confirmed_step: Union[None, TransactionVerifierStepType]
    ) -> Union[None, str]:
        if last_confirmed_step is None:
            return None
        return last_confirmed_step.value

    @property
    def trigger_protocol_signatures(self) -> List[str]:
        trigger_protocol_signatures_list = []
        for elem in reversed(sorted(self.verifier_public_keys.keys())):
            trigger_protocol_signatures_list.append(
                self.verifier_signatures_dtos[elem].trigger_protocol_signature
            )
        trigger_protocol_signatures_list.append(
            self.prover_signatures_dto.trigger_protocol_signature
        )
        return trigger_protocol_signatures_list

    @property
    def search_choice_signatures(self) -> List[List[str]]:
        search_choice_signatures_list = []
        amount_of_iterations = len(
            list(self.verifier_signatures_dtos.values())[0].search_choice_signatures
        )
        for i in range(amount_of_iterations):
            current_signatures_list = []
            for elem in reversed(sorted(self.verifier_public_keys.keys())):
                current_signatures_list.append(
                    self.verifier_signatures_dtos[elem].search_choice_signatures[i]
                )
            current_signatures_list.append(self.prover_signatures_dto.search_choice_signatures[i])
            search_choice_signatures_list.append(current_signatures_list)
        return search_choice_signatures_list

    @property
    def trigger_execution_challenge_signatures(self) -> List[str]:
        trigger_execution_challenge_signatures_list = []
        for elem in reversed(sorted(self.verifier_public_keys.keys())):
            trigger_execution_challenge_signatures_list.append(
                self.verifier_signatures_dtos[elem].trigger_execution_challenge_signature
            )
        trigger_execution_challenge_signatures_list.append(
            self.prover_signatures_dto.trigger_execution_challenge_signature
        )
        return trigger_execution_challenge_signatures_list

    @property
    def read_search_choice_signatures(self) -> List[List[str]]:
        read_search_choice_signatures_list = []
        amount_of_iterations = len(
            list(self.verifier_signatures_dtos.values())[0].read_search_choice_signatures
        )
        for i in range(amount_of_iterations):
            current_signatures_list = []
            for elem in reversed(sorted(self.verifier_public_keys.keys())):
                current_signatures_list.append(
                    self.verifier_signatures_dtos[elem].read_search_choice_signatures[i]
                )
            current_signatures_list.append(
                self.prover_signatures_dto.read_search_choice_signatures[i]
            )
            read_search_choice_signatures_list.append(current_signatures_list)
        return read_search_choice_signatures_list

    @property
    def amount_of_signatures(self) -> int:
        return len(self.verifier_public_keys.keys()) + 1
