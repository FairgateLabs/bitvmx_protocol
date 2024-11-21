import secrets

from bitcoinutils.keys import PrivateKey
from fastapi import HTTPException

from bitvmx_protocol_library.enums import BitcoinNetwork
from prover_app.api.v1.setup.fund.v1.view_models.post import (
    SetupFundPostV1Input,
    SetupFundPostV1Output,
)


class SetupFundPostViewControllerV1:
    def __init__(
        self,
        create_setup_with_funding_controller,
        protocol_properties,
        common_protocol_properties,
    ):
        self.create_setup_with_funding_controller = create_setup_with_funding_controller
        self.protocol_properties = protocol_properties
        self.common_protocol_properties = common_protocol_properties

    async def __call__(self, setup_post_view_input: SetupFundPostV1Input) -> SetupFundPostV1Output:
        # sha_256_bitcoin_script = BitcoinScript.from_int_list(script_list=pybitvmbinding.sha_256_script(int(64 / 2)))
        if (
            not self.common_protocol_properties.network == BitcoinNetwork.MUTINYNET
            and not self.common_protocol_properties.network == BitcoinNetwork.REGTEST
        ):
            raise HTTPException(
                status_code=404,
                detail="Endpoint not available for network "
                + str(self.common_protocol_properties.network.value),
            )
        if setup_post_view_input.verifier_list is None:
            verifier_list = self.protocol_properties.verifier_list
        else:
            verifier_list = setup_post_view_input.verifier_list
        if self.protocol_properties.prover_private_key is None:
            controlled_prover_private_key = PrivateKey(b=secrets.token_bytes(32))
        else:
            controlled_prover_private_key = PrivateKey(
                b=bytes.fromhex(self.protocol_properties.prover_private_key)
            )

        origin_of_funds_private_key = PrivateKey(
            b=bytes.fromhex(setup_post_view_input.secret_origin_of_funds)
        )

        setup_uuid = await self.create_setup_with_funding_controller(
            max_amount_of_steps=setup_post_view_input.max_amount_of_steps,
            amount_of_input_words=setup_post_view_input.amount_of_input_words,
            amount_of_bits_wrong_step_search=setup_post_view_input.amount_of_bits_wrong_step_search,
            amount_of_bits_per_digit_checksum=setup_post_view_input.amount_of_bits_per_digit_checksum,
            verifier_list=verifier_list,
            controlled_prover_private_key=controlled_prover_private_key,
            initial_amount_of_satoshis=self.common_protocol_properties.initial_amount_satoshis,
            step_fees_satoshis=self.common_protocol_properties.step_fees_satoshis,
            origin_of_funds_private_key=origin_of_funds_private_key,
        )
        return SetupFundPostV1Output(setup_uuid=setup_uuid)
