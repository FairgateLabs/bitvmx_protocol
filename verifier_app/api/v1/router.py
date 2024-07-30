from fastapi import APIRouter, Body

from verifier_app.api.v1.next_step.crud.v1.view_models.post import NextStepPostV1Input
from verifier_app.api.v1.public_keys.crud.v1.view_models.post import PublicKeysPostV1Input
from verifier_app.api.v1.setup.crud.v1.view_models.post import SetupPostV1Input
from verifier_app.api.v1.signatures.crud.v1.view_models.post import SignaturesPostV1Input
from verifier_app.dependency_injection.api.v1.view_controllers.next_step import (
    NextStepPostViewControllers,
)
from verifier_app.dependency_injection.api.v1.view_controllers.public_keys import (
    PublicKeysPostViewControllers,
)
from verifier_app.dependency_injection.api.v1.view_controllers.setup import SetupPostViewControllers
from verifier_app.dependency_injection.api.v1.view_controllers.signatures import (
    SignaturesPostViewControllers,
)

router = APIRouter()


@router.post("/next_step")
async def next_step_post(next_step_post_input: NextStepPostV1Input = Body()):
    view_controller = NextStepPostViewControllers.v1()
    return await view_controller(next_step_post_view_input=next_step_post_input)


@router.post("/public_keys")
async def public_keys_post(public_keys_post_input: PublicKeysPostV1Input = Body()):
    view_controller = PublicKeysPostViewControllers.v1()
    return await view_controller(public_keys_post_view_input=public_keys_post_input)


@router.post("/setup")
async def setup_post(setup_post_input: SetupPostV1Input = Body()):
    view_controller = SetupPostViewControllers.v1()
    return await view_controller(setup_post_view_input=setup_post_input)


@router.post("/signatures")
async def signatures_post(signatures_post_input: SignaturesPostV1Input = Body()):
    view_controller = SignaturesPostViewControllers.v1()
    return await view_controller(setup_post_view_input=signatures_post_input)
