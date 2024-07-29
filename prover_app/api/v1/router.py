from fastapi import APIRouter, Body

from prover_app.api.v1.fund.crud.view_models import FundPostV1Input, FundPostV1Output
from prover_app.api.v1.fund.crud.views import fund_post_view
from prover_app.api.v1.next_step.crud.view_models import NextStepPostV1Input
from prover_app.api.v1.next_step.crud.views import next_step_post_view
from prover_app.api.v1.setup.crud.view_models import SetupPostV1Input
from prover_app.api.v1.setup.crud.views import setup_post_view

router = APIRouter()

# If this becomes too big, we should create a router inside each folder, overengineering as of now


@router.post("/setup")
async def setup_post(setup_post_input: SetupPostV1Input = Body()):
    return await setup_post_view(setup_post_view_input=setup_post_input)


@router.post("/next_step")
async def next_step_post(next_step_post_input: NextStepPostV1Input = Body()):
    return await next_step_post_view(next_step_post_view_input=next_step_post_input)


@router.post("/fund")
async def fund_post(fund_post_input: FundPostV1Input) -> FundPostV1Output:
    return await fund_post_view(fund_post_view_input=fund_post_input)
