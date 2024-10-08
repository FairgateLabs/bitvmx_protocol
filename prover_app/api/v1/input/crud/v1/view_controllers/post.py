from prover_app.api.v1.input.crud.v1.view_models.post import InputPostV1Input, InputPostV1Output


class InputPostViewControllerV1:

    def __init__(
        self,
        input_controller,
    ):
        self.input_controller = input_controller

    async def __call__(self, input_post_view_input: InputPostV1Input) -> InputPostV1Output:
        self.input_controller(
            setup_uuid=input_post_view_input.setup_uuid, input_hex=input_post_view_input.input_hex
        )
        return InputPostV1Output()
