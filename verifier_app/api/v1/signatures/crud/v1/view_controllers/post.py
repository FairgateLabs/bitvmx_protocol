from verifier_app.api.v1.signatures.crud.v1.view_models.post import (
    SignaturesPostV1Input,
    SignaturesPostV1Output,
)


class SignaturesPostViewControllerV1:
    def __init__(
        self,
        generate_signatures_controller,
    ):
        self.generate_signatures_controller = generate_signatures_controller

    async def __call__(
        self, setup_post_view_input: SignaturesPostV1Input
    ) -> SignaturesPostV1Output:
        setup_uuid = setup_post_view_input.setup_uuid

        hash_result_signature_verifier, search_hash_signatures, trace_signature = (
            self.generate_signatures_controller(
                setup_uuid=setup_uuid,
                trigger_protocol_signature=setup_post_view_input.trigger_protocol_signature,
                search_choice_signatures=setup_post_view_input.search_choice_signatures,
                trigger_execution_signature=setup_post_view_input.trigger_execution_signature,
            )
        )

        return SignaturesPostV1Output(
            verifier_hash_result_signature=hash_result_signature_verifier,
            verifier_search_hash_signatures=search_hash_signatures,
            verifier_trace_signature=trace_signature,
            # verifier_execution_challenge_signature=execution_challenge_signature,
        )
