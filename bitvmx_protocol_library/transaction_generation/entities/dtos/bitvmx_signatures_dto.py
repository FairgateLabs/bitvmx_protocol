from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_verifier_signatures_dto import (
    BitVMXVerifierSignaturesDTO,
)


class BitVMXSignaturesDTO(BitVMXVerifierSignaturesDTO, BitVMXProverSignaturesDTO):
    @classmethod
    def from_prover_and_verifier_signatures(
        cls, prover: BitVMXProverSignaturesDTO, verifier: BitVMXVerifierSignaturesDTO
    ):

        return cls(
            **prover.model_dump(),
            **verifier.model_dump(),
        )

    @property
    def prover_signatures_dto(self):
        return BitVMXProverSignaturesDTO(
            **self.model_dump(),
        )

    @property
    def verifier_signatures_dto(self):
        return BitVMXVerifierSignaturesDTO(
            **self.model_dump(),
        )
