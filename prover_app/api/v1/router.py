from fastapi import APIRouter, Body

from prover_app.api.v1.setup.crud.view_models import CreateSetupBody
from prover_app.api.v1.setup.crud.views import setup_post_view

router = APIRouter()


@router.post("/setup")
async def setup_post(create_setup_body: CreateSetupBody = Body()):
    return await setup_post_view(create_setup_body)
