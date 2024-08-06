from typing import Dict, Optional

from pydantic import BaseModel

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

    @property
    def trigger_protocol_signatures(self):
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
    def search_choice_signatures(self):
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
    def trigger_execution_challenge_signatures(self):
        trigger_execution_challenge_signatures_list = []
        for elem in reversed(sorted(self.verifier_public_keys.keys())):
            trigger_execution_challenge_signatures_list.append(
                self.verifier_signatures_dtos[elem].trigger_execution_challenge_signature
            )
        trigger_execution_challenge_signatures_list.append(
            self.prover_signatures_dto.trigger_execution_challenge_signature
        )
        return trigger_execution_challenge_signatures_list
