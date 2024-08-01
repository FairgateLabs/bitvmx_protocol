from typing import List

from bitcoinutils.keys import PrivateKey
from fastapi import HTTPException

from bitvmx_protocol_library.enums import BitcoinNetwork


class CreateSetupWithFundingController:
    def __init__(
        self,
        create_setup_controller,
        faucet_service,
        common_protocol_properties,
        protocol_properties,
    ):
        self.create_setup_controller = create_setup_controller
        self.faucet_service = faucet_service
        self.common_protocol_properties = common_protocol_properties
        self.protocol_properties = protocol_properties

    async def __call__(
        self,
        max_amount_of_steps: int,
        amount_of_bits_wrong_step_search: int,
        amount_of_bits_per_digit_checksum: int,
        verifier_list: List[str],
        initial_amount_of_satoshis: int,
        step_fees_satoshis: int,
        controlled_prover_private_key: PrivateKey,
        origin_of_funds_private_key: PrivateKey,
    ):
        if not self.common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
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
        return await self.create_setup_controller(
            max_amount_of_steps=max_amount_of_steps,
            amount_of_bits_wrong_step_search=amount_of_bits_wrong_step_search,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
            verifier_list=verifier_list,
            controlled_prover_private_key=controlled_prover_private_key,
            funding_tx_id=funding_tx_id,
            funding_index=funding_index,
            step_fees_satoshis=step_fees_satoshis,
            origin_of_funds_private_key=origin_of_funds_private_key,
        )
