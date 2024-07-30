from prover_app.api.v1.next_step.crud.v1.view_models.post import (
    NextStepPostV1Input,
    NextStepPostV1Output,
)


class NextStepPostViewControllerV1:
    def __init__(
        self,
        publish_next_step_controller,
    ):
        self.publish_next_step_controller = publish_next_step_controller

    async def __call__(
        self, next_step_post_view_input: NextStepPostV1Input
    ) -> NextStepPostV1Output:
        setup_uuid = next_step_post_view_input.setup_uuid
        last_confirmed_step = self.publish_next_step_controller(setup_uuid=setup_uuid)
        return NextStepPostV1Output(setup_uuid=setup_uuid, executed_step=last_confirmed_step)
