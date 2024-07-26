import requests


class BroadcastTransactionService:

    def __call__(self, transaction):
        url = "https://mutinynet.com/api/tx"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "text/plain",
            "Origin": "https://mutinynet.com",
            "Referer": "https://mutinynet.com/tx/push",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }

        response = requests.post(url, headers=headers, data=transaction)

        if not response.status_code == 200:
            raise Exception(response.text)

        return {"tx_id": response.text}
