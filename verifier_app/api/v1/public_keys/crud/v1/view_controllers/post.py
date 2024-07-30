from verifier_app.api.v1.public_keys.crud.v1.view_models.post import (
    PublicKeysPostV1Input,
    PublicKeysPostV1Output,
)


class PublicKeysPostViewControllerV1:

    def __init__(self, generate_public_keys_controller):
        self.generate_public_keys_controller = generate_public_keys_controller

    async def __call__(
        self, public_keys_post_view_input: PublicKeysPostV1Input
    ) -> PublicKeysPostV1Output:
        setup_uuid = public_keys_post_view_input.setup_uuid
        (
            choice_search_verifier_public_keys_list,
            trace_verifier_public_keys,
            verifier_public_key_hex,
        ) = await self.generate_public_keys_controller(
            setup_uuid=setup_uuid,
            unspendable_public_key_hex=public_keys_post_view_input.seed_destroyed_public_key_hex,
            public_keys_post_view_input=public_keys_post_view_input,
        )
        return PublicKeysPostV1Output(
            choice_search_verifier_public_keys_list=choice_search_verifier_public_keys_list,
            trace_verifier_public_keys=trace_verifier_public_keys,
            verifier_public_key=verifier_public_key_hex,
        )
