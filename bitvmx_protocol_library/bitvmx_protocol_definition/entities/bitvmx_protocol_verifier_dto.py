from typing import Dict

from pydantic import BaseModel

from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)


class BitVMXProtocolVerifierDTO(BaseModel):
    prover_signatures_dto: BitVMXProverSignaturesDTO
    verifier_signatures_dtos: Dict[str, BitVMXProverSignaturesDTO]
