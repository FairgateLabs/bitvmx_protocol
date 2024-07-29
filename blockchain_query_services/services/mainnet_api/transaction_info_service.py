from time import sleep

import requests

from blockchain_query_services.entities.transaction_info_service.transaction_info_bo import (
    TransactionInfoBO,
)


class TransactionInfoService:

    def __call__(self, tx_id: str) -> TransactionInfoBO:
        url = f"https://mempool.space/api/tx/{tx_id}"

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7,ca-ES;q=0.6,ca;q=0.5,fr-FR;q=0.4,fr;q=0.3,it-IT;q=0.2,it;q=0.1",
            "cookie": "_pk_ref.5.9dfc=%5B%22%22%2C%22%22%2C1721903488%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_id.5.9dfc=ffa45fbf2da4989b.1721903488.; _pk_ses.5.9dfc=1",
            "priority": "u=1, i",
            "referer": f"https://mempool.space/tx/{tx_id}",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            sleep(5)
            response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            return TransactionInfoBO.from_transaction(tx=response_json)

        raise Exception(response.text)
