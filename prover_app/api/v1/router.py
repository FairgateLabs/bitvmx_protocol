from typing import Annotated

from fastapi import APIRouter, Body

from prover_app.api.v1.fund.crud.v1.view_models.post import FundPostV1Input, FundPostV1Output
from prover_app.api.v1.next_step.crud.v1.view_models.post import NextStepPostV1Input
from prover_app.api.v1.setup.crud.v1.swagger_examples.post import (
    setup_post_v1_input_swagger_examples,
)
from prover_app.api.v1.setup.crud.v1.view_models.post import SetupPostV1Input
from prover_app.dependency_injection.api.v1.fund import FundPostViewControllers
from prover_app.dependency_injection.api.v1.next_step import NextStepPostViewControllers
from prover_app.dependency_injection.api.v1.setup import SetupPostViewControllers

router = APIRouter()

# If this becomes too big, we should create a router inside each folder, overengineering as of now


@router.post("/setup")
async def setup_post(
    setup_post_input: Annotated[
        SetupPostV1Input, Body(openapi_examples=setup_post_v1_input_swagger_examples)
    ]
):
    view_controller = SetupPostViewControllers.v1()
    return await view_controller(setup_post_view_input=setup_post_input)


@router.post("/next_step")
async def next_step_post(next_step_post_input: NextStepPostV1Input = Body()):
    view_controller = NextStepPostViewControllers.v1()
    return await view_controller(next_step_post_view_input=next_step_post_input)


@router.post("/fund")
async def fund_post(fund_post_input: FundPostV1Input = Body()) -> FundPostV1Output:
    view_controller = FundPostViewControllers.v1()
    return await view_controller(fund_post_view_input=fund_post_input)
