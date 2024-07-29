from fastapi import APIRouter, Body

from verifier_app.api.v1.next_step.crud.view_models import NextStepPostV1Input
from verifier_app.api.v1.next_step.crud.views import next_step_post_view
from verifier_app.api.v1.public_keys.crud.view_models import PublicKeysPostV1Input
from verifier_app.api.v1.public_keys.crud.views import public_keys_post_view
from verifier_app.api.v1.setup.crud.view_models import SetupPostV1Input
from verifier_app.api.v1.setup.crud.views import setup_post_view
from verifier_app.api.v1.signatures.crud.view_models import SignaturesPostV1Input
from verifier_app.api.v1.signatures.crud.views import signatures_post_view

router = APIRouter()


@router.post("/next_step")
async def next_step_post(next_step_post_input: NextStepPostV1Input = Body()):
    return await next_step_post_view(next_step_post_view_input=next_step_post_input)


@router.post("/public_keys")
async def public_keys_post(public_keys_post_input: PublicKeysPostV1Input = Body()):
    return await public_keys_post_view(public_keys_post_view_input=public_keys_post_input)


@router.post("/setup")
async def setup_post(setup_post_input: SetupPostV1Input = Body()):
    return await setup_post_view(setup_post_view_input=setup_post_input)


@router.post("/signatures")
async def signatures_post(signatures_post_input: SignaturesPostV1Input = Body()):
    return await signatures_post_view(setup_post_view_input=signatures_post_input)
