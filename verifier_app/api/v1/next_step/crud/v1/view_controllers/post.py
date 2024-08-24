import json

import httpx

from verifier_app.api.v1.next_step.crud.v1.view_models.post import (
    NextStepPostV1Input,
    NextStepPostV1Output,
)
from verifier_app.config import protocol_properties


async def _trigger_next_step_prover(next_step_post_view_input: NextStepPostV1Input):
    prover_host = protocol_properties.prover_host
    url = f"{prover_host}/next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Be careful, this body is the prover one -> app library
    # Make the POST request
    async with httpx.AsyncClient(timeout=3000.0) as client:
        await client.post(url, headers=headers, json=json.loads(next_step_post_view_input.json()))


class NextStepPostViewControllerV1:
    def __init__(
        self,
        publish_next_step_controller,
    ):
        self.publish_next_step_controller = publish_next_step_controller

    async def __call__(
        self, next_step_post_view_input: NextStepPostV1Input
    ) -> NextStepPostV1Output:

        print("Processing new step")
        setup_uuid = next_step_post_view_input.setup_uuid
        last_confirmed_step = await self.publish_next_step_controller(setup_uuid=setup_uuid)
        return NextStepPostV1Output(setup_uuid=setup_uuid, executed_step=last_confirmed_step)
