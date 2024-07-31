from typing import Dict

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
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
        protocol_dict,
        scripts_dict: Dict,
        public_key: str,
        trigger_protocol_signature: str,
        search_choice_signatures: str,
        trigger_execution_signature: str,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):

        funding_result_output_amount = (
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis
        )
        # step_fees_satoshis = protocol_dict["step_fees_satoshis"]
        # amount_of_wrong_step_search_iterations = protocol_dict[
        #     "amount_of_wrong_step_search_iterations"
        # ]

        self.verify_signature_service(
            protocol_dict["trigger_protocol_tx"],
            scripts_dict["trigger_protocol_script"],
            funding_result_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key,
            trigger_protocol_signature,
        )

        for i in range(len(search_choice_signatures)):
            self.verify_signature_service(
                protocol_dict["search_choice_tx_list"][i],
                scripts_dict["choice_search_scripts"][i],
                funding_result_output_amount
                - (3 + 2 * i) * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
                public_key,
                search_choice_signatures[i],
            )

        self.verify_signature_service(
            protocol_dict["trigger_execution_challenge_tx"],
            scripts_dict["trigger_execution_script"],
            funding_result_output_amount
            - (2 * bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations + 3)
            * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key,
            trigger_execution_signature,
        )
