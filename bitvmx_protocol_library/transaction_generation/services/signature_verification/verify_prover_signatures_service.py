from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.entities.dtos.bitvmx_bitcoin_scripts_dto import (
    BitVMXBitcoinScriptsDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.services.signature_verification.verify_signature_service import (
    VerifySignatureService,
)


class VerifyProverSignaturesService:

    def __init__(self, destroyed_public_key):
        self.destroyed_public_key = destroyed_public_key
        self.verify_signature_service = VerifySignatureService(destroyed_public_key)

    def __call__(
        self,
        public_key: str,
        bitvmx_prover_signatures_dto: BitVMXProverSignaturesDTO,
        bitvmx_bitcoin_scripts_dto: BitVMXBitcoinScriptsDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):

        funding_result_output_amount = (
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis
        )

        self.verify_signature_service(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx,
            bitvmx_bitcoin_scripts_dto.trigger_protocol_script,
            funding_result_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key,
            bitvmx_prover_signatures_dto.trigger_protocol_signature,
        )

        for i in range(len(bitvmx_prover_signatures_dto.search_choice_signatures)):
            self.verify_signature_service(
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                    i
                ],
                bitvmx_bitcoin_scripts_dto.choice_search_scripts[i],
                funding_result_output_amount
                - (3 + 2 * i) * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
                public_key,
                bitvmx_prover_signatures_dto.search_choice_signatures[i],
            )

        self.verify_signature_service(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_execution_challenge_tx,
            bitvmx_bitcoin_scripts_dto.trigger_challenge_scripts[0],
            funding_result_output_amount
            - (2 * len(bitvmx_prover_signatures_dto.search_choice_signatures) + 3)
            * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key,
            bitvmx_prover_signatures_dto.trigger_execution_challenge_signature,
        )
