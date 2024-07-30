from verifier_app.api.v1.setup.crud.v1.view_models.post import SetupPostV1Input, SetupPostV1Output


class SetupPostViewControllerV1:

    def __init__(self, create_setup_controller):
        self.create_setup_controller = create_setup_controller

    async def __call__(self, setup_post_view_input: SetupPostV1Input) -> SetupPostV1Output:
        setup_uuid = setup_post_view_input.setup_uuid
        network = setup_post_view_input.network
        public_key_hex = await self.create_setup_controller(
            setup_uuid=setup_uuid,
            network=network,
        )
        return SetupPostV1Output(
            public_key=public_key_hex,
        )
