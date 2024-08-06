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

        verifier_signatures_dto = self.generate_signatures_controller(
            setup_uuid=setup_uuid,
            bitvmx_prover_signatures_dto=setup_post_view_input.prover_signatures_dto,
        )

        return SignaturesPostV1Output(
            verifier_signatures_dto=verifier_signatures_dto,
        )
