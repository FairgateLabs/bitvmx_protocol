import secrets
from typing import List

import aiohttp
from bitcoinutils.keys import PrivateKey
from fastapi import HTTPException

from bitvmx_protocol_library.enums import BitcoinNetwork
from prover_app.api.v1.setup.crud.v1.view_models.post import SetupPostV1Input


class CreateSetupWithFundingController:
    def __init__(
        self,
        faucet_service,
        common_protocol_properties,
        protocol_properties,
    ):
        self.faucet_service = faucet_service
        self.common_protocol_properties = common_protocol_properties
        self.protocol_properties = protocol_properties

    async def __call__(
        self,
        max_amount_of_steps: int,
        amount_of_input_words: int,
        amount_of_bits_wrong_step_search: int,
        amount_of_bits_per_digit_checksum: int,
        verifier_list: List[str],
        initial_amount_of_satoshis: int,
        step_fees_satoshis: int,
        controlled_prover_private_key: PrivateKey,
        origin_of_funds_private_key: PrivateKey,
    ) -> str:
        if (
            not self.common_protocol_properties.network == BitcoinNetwork.MUTINYNET
            and not self.common_protocol_properties.network == BitcoinNetwork.REGTEST
        ):
            raise HTTPException(
                status_code=404,
                detail="Endpoint not available for network "
                + str(self.common_protocol_properties.network.value),
            )
        origin_of_funds_public_key = origin_of_funds_private_key.get_public_key()
        funding_tx_id, funding_index = self.faucet_service(
            amount=initial_amount_of_satoshis + step_fees_satoshis,
            destination_address=origin_of_funds_public_key.get_segwit_address().to_string(),
        )
        if self.common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
            prover_destination_address = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"
        elif self.common_protocol_properties.network == BitcoinNetwork.REGTEST:
            prover_destination_address = (
                origin_of_funds_private_key.get_public_key().get_segwit_address().to_string()
            )
        else:
            raise Exception(
                "Prover destination address should be set for network "
                + self.common_protocol_properties.network.value
            )
        signature_private_key = PrivateKey(b=secrets.token_bytes(32))
        # This is not architecturally correct, we should call the setup controller (as it was before)
        # Nevertheless, it's done like this to ensure we check the whole flow while developing so don't change it
        url = f"{self.protocol_properties.prover_host}/setup"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        setup_post_v1_input = SetupPostV1Input(
            max_amount_of_steps=max_amount_of_steps,
            amount_of_input_words=amount_of_input_words,
            amount_of_bits_wrong_step_search=amount_of_bits_wrong_step_search,
            funding_tx_id=funding_tx_id,
            funding_index=funding_index,
            secret_origin_of_funds=origin_of_funds_private_key.to_bytes().hex(),
            verifier_list=verifier_list,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            prover_destination_address=prover_destination_address,
            prover_signature_private_key=signature_private_key.to_bytes().hex(),
            prover_signature_public_key=signature_private_key.get_public_key().to_hex(),
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, json=setup_post_v1_input.dict()
            ) as response:
                if response.status != 200:
                    content = await response.read()
                    raise HTTPException(
                        status_code=response.status,
                        detail=content.decode(),
                    )
                response_data = await response.json()
        return response_data["setup_uuid"]
