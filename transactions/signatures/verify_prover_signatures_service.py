from transactions.signatures.verify_signature_service import VerifySignatureService


class VerifyProverSignaturesService:

    def __init__(self, destroyed_public_key):
        self.destroyed_public_key = destroyed_public_key
        self.verify_signature_service = VerifySignatureService(destroyed_public_key)

    def __call__(
        self,
        protocol_dict,
        scripts_dict,
        public_key,
        trigger_protocol_signature,
        search_choice_signatures,
    ):

        funding_result_output_amount = protocol_dict["funding_amount_satoshis"]
        step_fees_satoshis = protocol_dict["step_fees_satoshis"]

        self.verify_signature_service(
            protocol_dict["trigger_protocol_tx"],
            scripts_dict["trigger_protocol_script"],
            funding_result_output_amount - step_fees_satoshis,
            public_key,
            trigger_protocol_signature,
        )

        for i in range(len(search_choice_signatures)):
            self.verify_signature_service(
                protocol_dict["search_choice_tx_list"][i],
                scripts_dict["choice_search_scripts"][i],
                funding_result_output_amount - (3 + 2 * i) * step_fees_satoshis,
                public_key,
                search_choice_signatures[i],
            )
