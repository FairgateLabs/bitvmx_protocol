from typing import Optional

import requests

from blockchain_query_services.services.interfaces.faucet_service import FaucetServiceInterface
from blockchain_query_services.services.mutinynet_api.transaction_info_service import (
    TransactionInfoService,
)


class FaucetService(FaucetServiceInterface):

    def __call__(
        self,
        amount: Optional[int] = 1000000,
        destination_address: Optional[str] = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v",
    ):
        url = "https://faucet.mutinynet.com/api/onchain"
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://faucet.mutinynet.com",
            "Referer": "https://faucet.mutinynet.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }
        data = {"sats": amount, "address": destination_address}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            # Try to return the index
            transaction_info = TransactionInfoService()(tx_id=response.json()["txid"])
            faucet_output = transaction_info.get_output(address=destination_address)
            return transaction_info.tx_id, faucet_output.index

        raise Exception(response.text)
