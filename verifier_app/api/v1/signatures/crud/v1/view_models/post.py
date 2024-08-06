from pydantic import BaseModel

from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_verifier_signatures_dto import (
    BitVMXVerifierSignaturesDTO,
)


class SignaturesPostV1Input(BaseModel):
    setup_uuid: str
    prover_signatures_dto: BitVMXProverSignaturesDTO


class SignaturesPostV1Output(BaseModel):
    verifier_signatures_dto: BitVMXVerifierSignaturesDTO
