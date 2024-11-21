from fastapi import HTTPException

from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from blockchain_query_services.services.interfaces.faucet_service import FaucetServiceInterface
from prover_app.api.v1.fund.crud.v1.view_models.post import FundPostV1Input, FundPostV1Output


class FundPostViewControllerV1:

    def __init__(self, faucet_service: FaucetServiceInterface):
        self.faucet_service = faucet_service

    async def __call__(self, fund_post_view_input: FundPostV1Input) -> FundPostV1Output:
        if (
            not common_protocol_properties.network == BitcoinNetwork.MUTINYNET
            and not common_protocol_properties.network == BitcoinNetwork.REGTEST
        ):
            raise HTTPException(
                status_code=404,
                detail="Endpoint not available for network "
                + str(common_protocol_properties.network.value),
            )
        income_tx, index = self.faucet_service(
            amount=fund_post_view_input.amount,
            destination_address=fund_post_view_input.destination_address,
        )
        return FundPostV1Output(tx_id=income_tx, index=index)
