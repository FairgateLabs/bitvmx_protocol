from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from blockchain_query_services.services.mutinynet_api.faucet_service import FaucetService
from prover_app.api.v1.fund.crud.view_models import FundPostV1Input, FundPostV1Output


async def fund_post_view(fund_post_view_input: FundPostV1Input) -> FundPostV1Output:
    assert common_protocol_properties.network == BitcoinNetwork.MUTINYNET
    faucet_service = FaucetService()
    income_tx, index = faucet_service(
        amount=fund_post_view_input.amount,
        destination_address=fund_post_view_input.destination_address,
    )
    return FundPostV1Output(tx_id=income_tx, index=index)
