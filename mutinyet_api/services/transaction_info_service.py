from time import sleep
from typing import List, Optional

import requests
from pydantic import BaseModel


class TransactionInput(BaseModel):
    tx_id: str
    index: int

    @staticmethod
    def from_mutinynet_vin(vin: dict) -> "TransactionInput":
        return TransactionInput(tx_id=vin["txid"], index=vin["vout"])


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
        url = f"https://mutinynet.com/api/tx/{tx_id}"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7,ca-ES;q=0.6,ca;q=0.5,fr-FR;q=0.4,fr;q=0.3,it-IT;q=0.2,it;q=0.1",
            "Connection": "keep-alive",
            "Referer": f"https://mutinynet.com/tx/{tx_id}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            sleep(5)
            response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            return TransactionInfo.from_mutinynet_transaction(tx=response_json)

        raise Exception(response.text)
