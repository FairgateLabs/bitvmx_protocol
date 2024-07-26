import requests


class BroadcastTransactionService:

    def __call__(self, transaction):
        url = "https://mempool.space/testnet/api/tx"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7,ca-ES;q=0.6,ca;q=0.5,fr-FR;q=0.4,fr;q=0.3,it-IT;q=0.2,it;q=0.1",
            "content-type": "text/plain",
            "origin": "https://mempool.space",
            "priority": "u=1, i",
            "referer": "https://mempool.space/testnet/tx/push",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }

        response = requests.post(url, headers=headers, data=transaction)

        if not response.status_code == 200:
            raise Exception(response.text)

        return {"tx_id": response.text}
