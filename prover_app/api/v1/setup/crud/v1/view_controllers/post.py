from prover_app.api.v1.setup.crud.v1.view_models.post import SetupPostV1Input, SetupPostV1Output


class SetupPostViewControllerV1:
    def __init__(
        self,
        create_setup_controller,
        protocol_properties,
    ):
        self.create_setup_controller = create_setup_controller
        self.protocol_properties = protocol_properties

    async def __call__(self, setup_post_view_input: SetupPostV1Input) -> SetupPostV1Output:
        if setup_post_view_input.verifier_list is None:
            verifier_list = self.protocol_properties.verifier_list
        else:
            verifier_list = setup_post_view_input.verifier_list
        setup_uuid = await self.create_setup_controller(
            max_amount_of_steps=setup_post_view_input.max_amount_of_steps,
            amount_of_bits_wrong_step_search=setup_post_view_input.amount_of_bits_wrong_step_search,
            amount_of_bits_per_digit_checksum=setup_post_view_input.amount_of_bits_per_digit_checksum,
            verifier_list=verifier_list,
        )
        return SetupPostV1Output(setup_uuid=setup_uuid)
