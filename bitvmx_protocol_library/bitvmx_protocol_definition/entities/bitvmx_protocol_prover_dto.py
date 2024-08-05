from typing import Dict

from pydantic import BaseModel

from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_verifier_signatures_dto import (
    BitVMXVerifierSignaturesDTO,
)


class BitVMXProtocolProverDTO(BaseModel):
    prover_signatures_dto: BitVMXVerifierSignaturesDTO
    verifier_signatures_dtos: Dict[str, BitVMXVerifierSignaturesDTO]
