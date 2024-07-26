from time import sleep
from typing import List, Optional

import requests
from pydantic import BaseModel


class TransactionInput(BaseModel):
    tx_id: str
    index: int
    witness: List[str]

    @staticmethod
    def from_mutinynet_vin(vin: dict) -> "TransactionInput":
        return TransactionInput(tx_id=vin["txid"], index=vin["vout"], witness=vin["witness"])


class TransactionOutput(BaseModel):
    address: str
    index: int
    value: int

    @staticmethod
    def from_mutinynet_vout(vout: dict, index: int) -> "TransactionOutput":
        return TransactionOutput(
            address=vout["scriptpubkey_address"], index=index, value=vout["value"]
        )


class TransactionInfo(BaseModel):
    confirmed: Optional[bool] = None
    tx_id: str
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]

    @staticmethod
    def from_mutinynet_transaction(tx: dict) -> "TransactionInfo":
        return TransactionInfo(
            confirmed=tx["status"]["confirmed"],
            tx_id=tx["txid"],
            inputs=[TransactionInput.from_mutinynet_vin(vin) for vin in tx["vin"]],
            outputs=[
                TransactionOutput.from_mutinynet_vout(vout, index)
                for index, vout in enumerate(tx["vout"])
            ],
        )

    def get_output(self, address: str) -> TransactionOutput:
        for element in self.outputs:
            if element.address == address:
                return element
        raise Exception("Address not found in the outputs")


class TransactionInfoService:

    def __call__(self, tx_id: str) -> TransactionInfo:
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
            return TransactionInfo.from_mutinynet_transaction(tx=response_json)

        raise Exception(response.text)
