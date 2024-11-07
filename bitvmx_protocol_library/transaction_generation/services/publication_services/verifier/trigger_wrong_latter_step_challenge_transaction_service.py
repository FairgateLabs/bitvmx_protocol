from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_private_dto import (
    BitVMXProtocolVerifierPrivateDTO,
)


class GenericTriggerWrongLatterStepChallengeTransactionService:
    def __init__(self, verifier_private_key):
        pass

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):
        raise Exception("Trigger not implemented")


class TriggerWrongLatterStep1ChallengeTransactionService(
    GenericTriggerWrongLatterStepChallengeTransactionService
):
    pass


class TriggerWrongLatterStep2ChallengeTransactionService(
    GenericTriggerWrongLatterStepChallengeTransactionService
):
    pass
