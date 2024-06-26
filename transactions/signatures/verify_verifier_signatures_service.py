from transactions.signatures.verify_signature_service import VerifySignatureService


class VerifyVerifierSignaturesService:

    def __init__(self, destroyed_public_key):
        self.destroyed_public_key = destroyed_public_key
        self.verify_signature_service = VerifySignatureService(destroyed_public_key)

    def __call__(self, protocol_dict, scripts_dict, public_key, hash_result_signature):

        funding_result_output_amount = protocol_dict["funding_amount_satoshis"]
        # step_fees_satoshis = protocol_dict["step_fees_satoshis"]

        self.verify_signature_service(
            protocol_dict["hash_result_tx"],
            scripts_dict["hash_result_script"],
            funding_result_output_amount,
            public_key,
            hash_result_signature,
        )
