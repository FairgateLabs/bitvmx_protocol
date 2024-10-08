from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_serializer

from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_verifier_signatures_dto import (
    BitVMXVerifierSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.enums import TransactionProverStepType


class BitVMXProtocolProverDTO(BaseModel):
    prover_public_key: str
    verifier_public_keys: Dict[str, str]
    prover_signatures_dto: BitVMXVerifierSignaturesDTO
    verifier_signatures_dtos: Dict[str, BitVMXVerifierSignaturesDTO]
    input_hex: Optional[str] = None
    halt_step: Optional[str] = None
    last_confirmed_step: Optional[TransactionProverStepType] = None
    last_confirmed_step_tx_id: Optional[str] = None
    search_choices: List[int] = Field(default_factory=list)
    read_search_choices: List[int] = Field(default_factory=list)
    published_hashes_dict: Dict[int, str] = Field(default_factory=dict)
    published_read_hashes_dict: Dict[int, str] = Field(default_factory=dict)

    @field_serializer("last_confirmed_step", when_used="always")
    def serialize_last_confirmed_step(
        last_confirmed_step: Union[None, TransactionProverStepType]
    ) -> Union[None, str]:
        if last_confirmed_step is None:
            return None
        return last_confirmed_step.value

    @property
    def hash_result_signatures(self):
        hash_result_signatures_list = []
        for elem in reversed(sorted(self.verifier_public_keys.keys())):
            hash_result_signatures_list.append(
                self.verifier_signatures_dtos[elem].hash_result_signature
            )
        hash_result_signatures_list.append(self.prover_signatures_dto.hash_result_signature)
        return hash_result_signatures_list

    @property
    def search_hash_signatures(self):
        search_hash_signatures_list = []
        amount_of_iterations = len(
            list(self.verifier_signatures_dtos.values())[0].search_hash_signatures
        )
        for i in range(amount_of_iterations):
            current_signatures_list = []
            for elem in reversed(sorted(self.verifier_public_keys.keys())):
                current_signatures_list.append(
                    self.verifier_signatures_dtos[elem].search_hash_signatures[i]
                )
            current_signatures_list.append(self.prover_signatures_dto.search_hash_signatures[i])
            search_hash_signatures_list.append(current_signatures_list)
        return search_hash_signatures_list

    @property
    def trace_signatures(self):
        trace_signatures_list = []
        for elem in reversed(sorted(self.verifier_public_keys.keys())):
            trace_signatures_list.append(self.verifier_signatures_dtos[elem].trace_signature)
        trace_signatures_list.append(self.prover_signatures_dto.trace_signature)
        return trace_signatures_list

    @property
    def read_search_hash_signatures(self):
        read_search_hash_signatures_list = []
        amount_of_iterations = len(
            list(self.verifier_signatures_dtos.values())[0].read_search_hash_signatures
        )
        for i in range(amount_of_iterations):
            current_signatures_list = []
            for elem in reversed(sorted(self.verifier_public_keys.keys())):
                current_signatures_list.append(
                    self.verifier_signatures_dtos[elem].read_search_hash_signatures[i]
                )
            current_signatures_list.append(
                self.prover_signatures_dto.read_search_hash_signatures[i]
            )
            read_search_hash_signatures_list.append(current_signatures_list)
        return read_search_hash_signatures_list

    @property
    def read_trace_signatures(self):
        read_trace_signatures_list = []
        for elem in reversed(sorted(self.verifier_public_keys.keys())):
            read_trace_signatures_list.append(
                self.verifier_signatures_dtos[elem].read_trace_signature
            )
        read_trace_signatures_list.append(self.prover_signatures_dto.read_trace_signature)
        return read_trace_signatures_list
