from transactions.signatures.verify_signature_service import VerifySignatureService


class VerifyVerifierSignaturesService:

    def __init__(self, destroyed_public_key):
        self.destroyed_public_key = destroyed_public_key
        self.verify_signature_service = VerifySignatureService(destroyed_public_key)

    def __call__(
        self,
        protocol_dict,
        scripts_dict,
        public_key,
        hash_result_signature,
        search_hash_signatures,
        trace_signature,
        execution_challenge_signature,
    ):

        funding_result_output_amount = protocol_dict["funding_amount_satoshis"]
        step_fees_satoshis = protocol_dict["step_fees_satoshis"]

        self.verify_signature_service(
            protocol_dict["hash_result_tx"],
            scripts_dict["hash_result_script"],
            funding_result_output_amount,
            public_key,
            hash_result_signature,
        )

        for i in range(len(search_hash_signatures)):
            self.verify_signature_service(
                protocol_dict["search_hash_tx_list"][i],
                scripts_dict["hash_search_scripts"][i],
                funding_result_output_amount - (2 + 2 * i) * step_fees_satoshis,
                public_key,
                search_hash_signatures[i],
            )

        self.verify_signature_service(
            protocol_dict["trace_tx"],
            scripts_dict["trace_script"],
            funding_result_output_amount
            - (2 + 2 * len(search_hash_signatures)) * step_fees_satoshis,
            public_key,
            trace_signature,
        )

        self.verify_signature_service(
            protocol_dict["execution_challenge_tx"],
            scripts_dict["execution_challenge_script"],
            funding_result_output_amount
            - (4 + 2 * len(search_hash_signatures)) * step_fees_satoshis,
            public_key,
            execution_challenge_signature,
        )
